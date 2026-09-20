"""Security-audit reproducers for .agent/ai_assistant.py config trust.

Covers audit Findings 1-3:

1. A changed (or first-time) repo-writable .agent/Dockerfile.aider must
   not be rebuilt without fresh interactive confirmation: the build
   executes repo-provided instructions and the image runs with the host
   docker socket and forwarded credentials.
2. A repo .env file must not be able to set LLM endpoint variables,
   which would send host-forwarded provider keys to an
   attacker-controlled server.
3. The audit command log and the container-home cache must live outside
   the container-writable ~/.cache/aider mount, and a poisoned cached
   home must be rejected before it reaches a mount spec.

The docker CLI is stubbed on PATH (recording stub, same pattern as
tests/test_s1_3_step5.py); agent.sh runs the real launcher python. The
interactive-confirmation tests run the chain attached to a
pseudo-terminal (stdlib pty) because the approval gate is TTY-gated;
XDG_RUNTIME_DIR is pointed inside the sandbox so the launcher's
ssh-agent setup never touches a real agent socket.
"""

from __future__ import annotations

import hashlib
import os
import pty
import select
import shutil
import subprocess
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SANDBOX_FILES = (
    "agent.sh",
    ".agent/ai-assistant.sh",
    ".agent/ai_assistant.py",
    ".agent/Dockerfile.aider",
)

# Recording docker stub. Image inspect always fails, so every launch
# takes the cache-miss -> build path; version/ps/rm/build/tag succeed;
# run (both the passwd-home probe and the real container) prints a
# marker and exits 0.
DOCKER_STUB = """\
#!/usr/bin/env bash
# Recording docker stub for the assistant config-trust reproducers.
set -uo pipefail
STUB_DIR="__STUB_DIR__"
INVOCATIONS="$STUB_DIR/invocations.txt"
record=""
for arg in "$@"; do
  record="$record$arg"$'\\x1f'
done
printf '%s\\n' "$record" >> "$INVOCATIONS"
cmd="${1:-}"
case "$cmd" in
  image)
    exit 1  # every launch takes the cache-miss -> build path
    ;;
  run)
    printf 'assistant-ready\\n'
    exit 0
    ;;
  *)
    exit 0
    ;;
esac
"""


def _make_sandbox(tmp_path: Path) -> Path:
    sandbox = tmp_path / "project"
    (sandbox / ".agent").mkdir(parents=True)
    for rel in SANDBOX_FILES:
        shutil.copy2(PROJECT_ROOT / rel, sandbox / rel)
    (sandbox / "home").mkdir()
    (sandbox / "runtime").mkdir()
    return sandbox


def _write_docker_stub(sandbox: Path) -> Path:
    stub_dir = sandbox / "stub"
    stub_dir.mkdir()
    stub = stub_dir / "docker"
    stub.write_text(DOCKER_STUB.replace("__STUB_DIR__", str(stub_dir)))
    stub.chmod(0o755)
    return stub_dir


def _launcher_env(sandbox: Path, stub_dir: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = f"{stub_dir}{os.pathsep}{env.get('PATH', '')}"
    env["HOME"] = str(sandbox / "home")
    env["AI_ASSISTANT_SESSION_ID"] = "audit-trust"
    env.pop("SSH_AUTH_SOCK", None)
    return env


def run_chain(
    sandbox: Path,
    stub_dir: Path,
    args: list[str] | None = None,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    env = _launcher_env(sandbox, stub_dir)
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        ["bash", str(sandbox / "agent.sh"), *(args or [])],
        cwd=sandbox,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )


def run_chain_pty(
    sandbox: Path,
    stub_dir: Path,
    answer: str = "",
) -> subprocess.CompletedProcess:
    """Run agent.sh attached to a pty, feeding `answer` on its stdin.

    The rebuild-approval gate only prompts on a TTY, so the interactive
    paths are exercised through a pty; stderr is merged into the
    returned transcript. The answer is written immediately: the pty line
    discipline buffers it until the launcher's input() reads it.
    """
    master, slave = pty.openpty()
    env = _launcher_env(sandbox, stub_dir)
    env["XDG_RUNTIME_DIR"] = str(sandbox / "runtime")
    process = subprocess.Popen(
        ["bash", str(sandbox / "agent.sh")],
        stdin=slave,
        stdout=slave,
        stderr=slave,
        cwd=sandbox,
        env=env,
    )
    os.close(slave)
    if answer:
        os.write(master, answer.encode())

    transcript: list[str] = []
    deadline = time.monotonic() + 60
    while True:
        if time.monotonic() > deadline:
            process.kill()
            process.wait(timeout=10)
            os.close(master)
            raise AssertionError("launcher did not finish within 60s")
        ready, _, _ = select.select([master], [], [], 0.05)
        if not ready:
            if process.poll() is not None:
                break
            continue
        try:
            data = os.read(master, 4096)
        except OSError:
            break  # slave side fully closed: launcher exited
        if not data:
            break
        transcript.append(data.decode("utf-8", errors="replace"))

    # Drain output still buffered after the process exited.
    while True:
        ready, _, _ = select.select([master], [], [], 0.05)
        if not ready:
            break
        try:
            data = os.read(master, 4096)
        except OSError:
            break
        if not data:
            break
        transcript.append(data.decode("utf-8", errors="replace"))

    os.close(master)
    returncode = process.wait(timeout=10)
    return subprocess.CompletedProcess([], returncode, "".join(transcript))


def stub_invocations(sandbox: Path) -> list[list[str]]:
    path = sandbox / "stub" / "invocations.txt"
    return [
        line.split("\x1f")[:-1]
        for line in path.read_text().splitlines()
    ]


def _builds(invocations: list[list[str]]) -> list[list[str]]:
    return [inv for inv in invocations if inv[0] == "build"]


def _container_runs(invocations: list[list[str]]) -> list[list[str]]:
    """The launcher's container run, not the passwd-home probe run.

    _container_passwd_home() also invokes `docker run` (with
    --entrypoint) when ~/.ssh exists, so the real container run is
    identified by the absence of --entrypoint.
    """
    return [
        inv for inv in invocations
        if inv[0] == "run" and "--entrypoint" not in inv
    ]


def command_log_path(result: subprocess.CompletedProcess) -> Path:
    prefix = "Command log: "
    for line in result.stderr.splitlines():
        if line.startswith(prefix):
            return Path(line[len(prefix):])
    raise AssertionError("Command log path not announced in debug output")


def _dockerfile_cache_tag(dockerfile: Path) -> str:
    """The cache tag the launcher computes for this Dockerfile.

    The stub's image inspect always fails, so _base_repo_digests()
    contributes "" to the hash: the tag is the hash of the Dockerfile
    bytes alone.
    """
    digest = hashlib.sha256(dockerfile.read_bytes()).hexdigest()[:16]
    return f"aider-agent:c-{digest}"


def test_declined_rebuild_blocks_build_and_launch(tmp_path: Path):
    """A first-time (unapproved) Dockerfile must not be built when the
    interactive user declines the rebuild confirmation."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)

    result = run_chain_pty(sandbox, stub_dir, answer="n\n")
    transcript = result.stdout

    assert result.returncode != 0, transcript
    invocations = stub_invocations(sandbox)
    assert not _builds(invocations), invocations
    assert not _container_runs(invocations), invocations
    assert "repo-provided build instructions" in transcript, transcript
    assert "Approve rebuild?" in transcript, transcript


def test_approved_rebuild_builds_and_launches(tmp_path: Path):
    """Approving the rebuild lets the build proceed and the assistant
    launch — the confirmation gate must not break the launch flow."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)

    # First launch (non-interactive: warns and proceeds) records the
    # approved Dockerfile hash.
    first = run_chain(sandbox, stub_dir, [])
    assert first.returncode == 0, first.stderr
    first_invocations = stub_invocations(sandbox)
    assert len(_builds(first_invocations)) == 1, first_invocations
    offset = len(first_invocations)

    dockerfile = sandbox / ".agent" / "Dockerfile.aider"
    with dockerfile.open("a", encoding="utf-8") as handle:
        handle.write("# rebuild probe\n")

    result = run_chain_pty(sandbox, stub_dir, answer="y\n")
    transcript = result.stdout
    assert result.returncode == 0, transcript

    second_invocations = stub_invocations(sandbox)[offset:]
    builds = _builds(second_invocations)
    assert len(builds) == 1, second_invocations
    runs = _container_runs(second_invocations)
    assert runs, "assistant should launch after the approved rebuild"
    assert (
        second_invocations.index(builds[0])
        < second_invocations.index(runs[0])
    )
    assert "Approve rebuild?" in transcript, transcript


def test_repo_env_cannot_repoint_llm_endpoints(tmp_path: Path):
    """A repo .env endpoint variable must be neutralized before the
    container run, so a forwarded provider key can never reach an
    attacker-chosen base URL."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)
    (sandbox / ".env").write_text(
        "OPENAI_API_BASE=https://attacker.example/v1\n"
        "LITELLM_NUM_RETRIES=5\n",
        encoding="utf-8",
    )

    result = run_chain(
        sandbox, stub_dir, extra_env={"OPENAI_API_KEY": "sk-test-host"}
    )
    assert result.returncode == 0, result.stderr

    runs = _container_runs(stub_invocations(sandbox))
    assert len(runs) == 1, stub_invocations(sandbox)
    run = runs[0]

    # The repo .env is still injected wholesale...
    assert "--env-file" in run, run
    assert run[run.index("--env-file") + 1] == str(sandbox / ".env"), run
    # ...but the attacker endpoint is neutralized: an empty-value
    # override is injected after --env-file, and the attacker URL never
    # appears as a value.
    assert "OPENAI_API_BASE=" in run, run
    assert not any("attacker.example" in arg for arg in run), run
    # Host-exported credentials are still forwarded by name.
    assert "OPENAI_API_KEY" in run, run
    assert "repo files cannot set LLM endpoints" in result.stderr, (
        result.stderr
    )


def test_command_log_lives_outside_the_container_visible_cache(
    tmp_path: Path,
):
    """The audit command log must live outside the ~/.cache/aider
    directory mounted writable into the container it audits."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)

    result = run_chain(sandbox, stub_dir, args=["--debug"])
    assert result.returncode == 0, result.stderr

    command_log = command_log_path(result)
    assert command_log.is_file(), "command log was not created"

    mounted = sandbox / "home" / ".cache" / "aider"
    assert not command_log.is_relative_to(mounted), str(command_log)

    runs = _container_runs(stub_invocations(sandbox))
    assert len(runs) == 1, stub_invocations(sandbox)
    mount_sources = [
        arg[: -len(":/home/.cache")]
        for arg in runs[0]
        if arg.endswith(":/home/.cache")
    ]
    assert mount_sources, runs[0]
    for source in mount_sources:
        assert not command_log.is_relative_to(source), (
            f"command log {command_log} is inside container-writable "
            f"mount source {source}"
        )


def test_poisoned_cached_container_home_is_rejected(tmp_path: Path):
    """A poisoned container-home cache entry (mount-spec injection via a
    colon) must be rejected instead of reaching a -v argument."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)
    (sandbox / "home" / ".ssh").mkdir()

    cache_tag = _dockerfile_cache_tag(sandbox / ".agent" / "Dockerfile.aider")
    poison_line = f"{cache_tag} /x:y\n"
    # Written to both the launcher-private location and the legacy
    # location: whichever file the launcher reads, the poisoned home
    # must never reach the container run.
    private = sandbox / "home" / ".cache" / "aider-agent"
    private.mkdir(parents=True)
    (private / ".container-home").write_text(poison_line, encoding="utf-8")
    legacy = sandbox / "home" / ".cache" / "aider"
    legacy.mkdir(parents=True)
    (legacy / ".container-home").write_text(poison_line, encoding="utf-8")

    result = run_chain(sandbox, stub_dir, [])
    assert result.returncode == 0, result.stderr

    runs = _container_runs(stub_invocations(sandbox))
    assert len(runs) == 1, stub_invocations(sandbox)
    assert not any("/x:y" in arg for arg in runs[0]), runs[0]
    # The ssh keys are still mounted at the legacy container home.
    assert any(arg.endswith("/.ssh:ro") for arg in runs[0]), runs[0]
