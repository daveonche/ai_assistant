"""S5.1 step 2 verification: per-project args loading and precedence.

Exercises the launcher from the outside, the way a user runs it: the
sandbox copies the real launch chain (.agent/start.sh ->
.agent/launcher.py), the docker CLI is a recording stub on PATH,
and HOME points inside the sandbox so the per-project args file sits at
its documented host-side location under ~/.config/aider-agent/projects/
— outside the repository the launcher runs in, where repository content
can never create or alter it.

Covered here:
- args-file entries reach the assistant command one token per line:
  blank lines and '#' comments contribute nothing, and every remaining
  line is passed verbatim as a single argument token (no shell
  interpretation);
- explicitly typed command-line arguments win over file entries: the
  file's tokens are prepended, so a flag given in both places takes its
  typed value (the last occurrence wins);
- on an interactive terminal a status line reports the args-file path
  and how many entries were loaded, or the creation hint when the file
  is absent; without a TTY no status line is printed.
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

AIDER_IMAGE = "aider-agent:latest"

SANDBOX_FILES = (
    ".agent/start.sh",
    ".agent/launcher.py",
    ".agent/Dockerfile.aider",
)

# Recording docker stub. Image inspect always fails, so every launch
# takes the cache-miss -> build path; version/ps/rm/build/tag succeed;
# run (both the passwd-home probe and the real container) prints a
# marker and exits 0.
DOCKER_STUB = """\
#!/usr/bin/env bash
# Recording docker stub for the S5.1 args-loading reproducers.
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

# One token per line: a comment, a blank line, and five real tokens —
# including a spaced value that must stay a single argument and a token
# with shell metacharacters that must never be interpreted.
ARGS_FILE_BODY = """\
# a comment line is ignored

--test-cmd
python -m pytest -q
--dark-mode
--lint-cmd
echo "verbatim" $(id -u)
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
    env["AI_ASSISTANT_SESSION_ID"] = "s5-1-step2"
    env.pop("SSH_AUTH_SOCK", None)
    return env


def run_chain(
    sandbox: Path,
    stub_dir: Path,
    args: list[str] | None = None,
) -> subprocess.CompletedProcess:
    """Run .agent/start.sh with output captured (no TTY)."""
    env = _launcher_env(sandbox, stub_dir)
    return subprocess.run(
        ["bash", str(sandbox / ".agent" / "start.sh"), *(args or [])],
        cwd=sandbox,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )


def run_chain_pty(sandbox: Path, stub_dir: Path) -> subprocess.CompletedProcess:
    """Run .agent/start.sh attached to a pty so TTY-gated output is produced.

    stdin is never written; the launch needs no input (a first-time
    build proceeds after a warning, without prompting).
    """
    master, slave = pty.openpty()
    env = _launcher_env(sandbox, stub_dir)
    env["XDG_RUNTIME_DIR"] = str(sandbox / "runtime")
    process = subprocess.Popen(
        ["bash", str(sandbox / ".agent" / "start.sh")],
        stdin=slave,
        stdout=slave,
        stderr=slave,
        cwd=sandbox,
        env=env,
    )
    os.close(slave)

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


def _workspace_hash(project_root: Path) -> str:
    """The launcher's project-identity hash (md5 of the path + newline)."""
    return hashlib.md5((str(project_root) + "\n").encode()).hexdigest()


def _args_file_path(sandbox: Path) -> Path:
    """The per-project args-file path the launcher derives for the sandbox."""
    digest = _workspace_hash(sandbox)
    file_name = f"{sandbox.name}-{digest[:8]}.args"
    return (
        sandbox / "home" / ".config" / "aider-agent" / "projects" / file_name
    )


def _write_args_file(sandbox: Path, text: str) -> Path:
    path = _args_file_path(sandbox)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def stub_invocations(sandbox: Path) -> list[list[str]]:
    path = sandbox / "stub" / "invocations.txt"
    return [
        line.split("\x1f")[:-1]
        for line in path.read_text().splitlines()
    ]


def _container_run(sandbox: Path) -> list[str]:
    """The launcher's container run, not the passwd-home probe run.

    _container_passwd_home() also invokes `docker run` (with
    --entrypoint) whenever ~/.ssh exists — and the launcher's GitHub
    host-key pinning creates it — so the real container run is
    identified by the absence of --entrypoint.
    """
    runs = [
        inv for inv in stub_invocations(sandbox)
        if inv[0] == "run" and "--entrypoint" not in inv
    ]
    assert len(runs) == 1, stub_invocations(sandbox)
    return runs[0]


def test_args_file_entries_reach_the_assistant_verbatim(tmp_path: Path):
    """File entries are applied one token per line: the comment and the
    blank line contribute nothing, and each remaining line arrives as a
    single verbatim argument token — quotes and command substitution
    intact, nothing executed."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)
    _write_args_file(sandbox, ARGS_FILE_BODY)

    result = run_chain(sandbox, stub_dir)
    assert result.returncode == 0, result.stderr

    run = _container_run(sandbox)
    tail = run[run.index(AIDER_IMAGE) + 1:]
    assert tail[-5:] == [
        "--test-cmd",
        "python -m pytest -q",
        "--dark-mode",
        "--lint-cmd",
        'echo "verbatim" $(id -u)',
    ], run


def test_typed_cli_args_win_over_file_entries(tmp_path: Path):
    """A flag provided both in the args file and on the command line
    takes its typed value: the file's tokens are prepended, so the typed
    occurrence lands after the file's and the last one wins."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)
    _write_args_file(sandbox, "--test-cmd\necho from-file\n")

    result = run_chain(sandbox, stub_dir, ["--test-cmd", "echo from-typed"])
    assert result.returncode == 0, result.stderr

    run = _container_run(sandbox)
    tail = run[run.index(AIDER_IMAGE) + 1:]
    assert tail[-4:] == [
        "--test-cmd",
        "echo from-file",
        "--test-cmd",
        "echo from-typed",
    ], run
    assert tail.index("echo from-typed") > tail.index("echo from-file")


def test_status_line_reports_path_and_count_on_a_tty(tmp_path: Path):
    """On an interactive terminal the launch reports the args-file path
    and how many entries were loaded."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)
    args_path = _write_args_file(sandbox, ARGS_FILE_BODY)

    result = run_chain_pty(sandbox, stub_dir)
    assert result.returncode == 0, result.stdout

    assert f"Project args: {args_path}" in result.stdout, result.stdout
    assert "(5 argument(s) loaded)" in result.stdout, result.stdout


def test_status_line_hints_to_create_when_absent(tmp_path: Path):
    """With no args file, the TTY status line names the would-be path
    and points at --init-project-args."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)

    result = run_chain_pty(sandbox, stub_dir)
    assert result.returncode == 0, result.stdout

    expected = _args_file_path(sandbox)
    assert (
        f"Project args: {expected} not found; create it with "
        "--init-project-args"
    ) in result.stdout, result.stdout


def test_no_status_line_without_a_tty(tmp_path: Path):
    """With output captured (not a terminal), no args status line is
    printed on either stream."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)
    _write_args_file(sandbox, ARGS_FILE_BODY)

    result = run_chain(sandbox, stub_dir)
    assert result.returncode == 0, result.stderr

    assert "Project args:" not in result.stdout, result.stdout
    assert "Project args:" not in result.stderr, result.stderr
