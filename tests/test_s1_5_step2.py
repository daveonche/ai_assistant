"""Tests for S1.5 Step 2: Enable read-write project root access inside the session container."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SANDBOX_FILES = (
    "agent.sh",
    ".agent/ai-assistant.sh",
    ".agent/ai_assistant.py",
    ".agent/Dockerfile.aider",
)

AIDER_IMAGE = "aider-agent:latest"

# Recording docker stub: image inspect succeeds only for tags the launcher
# itself has tagged/built, so the chain reaches docker run and every
# invocation is recorded. Digest probes (--format) always fail, making the
# cache tag a deterministic hash of the Dockerfile bytes alone.
DOCKER_STUB = """\
#!/usr/bin/env bash
# Recording docker stub for S1.5 Step 2 tests.
set -uo pipefail
STUB_DIR="__STUB_DIR__"
INVOCATIONS="$STUB_DIR/invocations.txt"
KNOWN_TAGS="$STUB_DIR/known_tags.txt"

record=""
for arg in "$@"; do
  record="$record$arg"$'\\x1f'
done
printf '%s\\n' "$record" >> "$INVOCATIONS"

cmd="${1:-}"
case "$cmd" in
  version)
    exit 0
    ;;
  ps|rm)
    exit 0
    ;;
  image)
    if [[ "${2:-}" == "inspect" ]]; then
      if [[ " $* " == *" --format "* ]]; then
        exit 1
      fi
      tag="${*: -1}"
      if [[ -f "$KNOWN_TAGS" ]] && grep -Fxq -- "$tag" "$KNOWN_TAGS"; then
        exit 0
      fi
      exit 1
    fi
    exit 0
    ;;
  build)
    printf '%s\\n' "aider-agent:latest" >> "$KNOWN_TAGS"
    printf 'docker build ok\\n'
    exit "${FAIL_BUILD:-0}"
    ;;
  tag)
    printf '%s\\n' "${*: -1}" >> "$KNOWN_TAGS"
    exit 0
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
        shutil.copy2(REPO_ROOT / rel, sandbox / rel)
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
    env["AI_ASSISTANT_SESSION_ID"] = "s1-5-2"
    (sandbox / "home").mkdir(exist_ok=True)
    return env


def run_chain(
    sandbox: Path,
    stub_dir: Path,
    args: list[str],
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    env = _launcher_env(sandbox, stub_dir)
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        ["bash", str(sandbox / "agent.sh"), *args],
        cwd=sandbox,
        env=env,
        capture_output=True,
        text=True,
        timeout=180,
    )


def stub_invocations(sandbox: Path) -> list[list[str]]:
    path = sandbox / "stub" / "invocations.txt"
    return [
        line.split("\x1f")[:-1]
        for line in path.read_text().splitlines()
    ]


def _last_run(invocations: list[list[str]]) -> list[str]:
    return [inv for inv in invocations if inv[0] == "run"][-1]


def _values_after(invocation: list[str], flag: str) -> list[str]:
    return [
        invocation[i + 1]
        for i, arg in enumerate(invocation)
        if arg == flag and i + 1 < len(invocation)
    ]


def _root_mount(mounts: list[str], root: Path) -> str | None:
    """Return the bind-mount entry whose source and destination are both root."""
    for mount in mounts:
        parts = mount.split(":")
        if len(parts) >= 2 and parts[0] == str(root) and parts[1] == str(root):
            return mount
    return None


def test_project_root_bind_mounted_at_same_path(tmp_path):
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)

    result = run_chain(sandbox, stub_dir, [])
    assert result.returncode == 0, result.stderr

    run_inv = _last_run(stub_invocations(sandbox))

    # The project root is bind-mounted at its own path: source and
    # destination are both the launcher's working directory.
    mounts = _values_after(run_inv, "-v")
    assert f"{sandbox}:{sandbox}" in mounts, mounts

    # The same path is the container's working directory.
    assert _values_after(run_inv, "-w") == [str(sandbox)]


def test_assistant_config_directory_included_in_mount(tmp_path):
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)

    result = run_chain(sandbox, stub_dir, [])
    assert result.returncode == 0, result.stderr

    run_inv = _last_run(stub_invocations(sandbox))

    # The bind-mount source is the project root, which contains the
    # assistant configuration directory (.agent) — so the configuration
    # directory is included in the mounted tree at its host-relative path.
    mounts = _values_after(run_inv, "-v")
    mount = _root_mount(mounts, sandbox)
    assert mount is not None, mounts
    source = mount.split(":")[0]
    assert (Path(source) / ".agent").is_dir(), source


def test_project_root_mount_is_read_write(tmp_path):
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)

    result = run_chain(sandbox, stub_dir, [])
    assert result.returncode == 0, result.stderr

    run_inv = _last_run(stub_invocations(sandbox))

    # The project-root bind mount carries no read-only option, so changes
    # made to project files inside the container persist on the host.
    mounts = _values_after(run_inv, "-v")
    mount = _root_mount(mounts, sandbox)
    assert mount is not None, mounts
    parts = mount.split(":")
    options = parts[2:]  # empty for a plain read-write mount
    flags = {f for opt in options for f in opt.split(",")}
    assert not flags & {"ro", "readonly"}, mount


def test_buildx_state_redirected_to_writable_cache(tmp_path):
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)

    result = run_chain(sandbox, stub_dir, [])
    assert result.returncode == 0, result.stderr

    run_inv = _last_run(stub_invocations(sandbox))

    # Buildx writes per-builder state under $HOME/.docker/buildx, but
    # /home/.docker is mounted read-only; the launcher must point buildx's
    # state at the writable cache mount so in-container builds succeed.
    env_values = _values_after(run_inv, "-e")
    assert "BUILDX_CONFIG=/home/.cache/buildx" in env_values, env_values


def test_ssh_directory_mounted_read_only(tmp_path):
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)

    # The launcher resolves ~/.ssh from its own HOME (the sandbox's home
    # directory); create it so the conditional mount fires.
    ssh_dir = sandbox / "home" / ".ssh"
    ssh_dir.mkdir(parents=True)

    result = run_chain(sandbox, stub_dir, [])
    assert result.returncode == 0, result.stderr

    run_inv = _last_run(stub_invocations(sandbox))

    # The host ~/.ssh is bind-mounted read-only at the identical path so
    # git push/pull over SSH remotes works inside the container.
    mounts = _values_after(run_inv, "-v")
    assert f"{ssh_dir}:/home/.ssh:ro" in mounts, mounts


def test_ssh_agent_socket_forwarded_when_present(tmp_path):
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)

    ssh_dir = sandbox / "home" / ".ssh"
    ssh_dir.mkdir(parents=True)

    # The launcher only checks that the SSH_AUTH_SOCK path exists; a
    # regular file satisfies that check, and the stub records argv only.
    agent_sock = sandbox / "agent.sock"
    agent_sock.touch()

    result = run_chain(
        sandbox,
        stub_dir,
        [],
        extra_env={"SSH_AUTH_SOCK": str(agent_sock)},
    )
    assert result.returncode == 0, result.stderr

    run_inv = _last_run(stub_invocations(sandbox))

    # The host agent socket is mounted at its identical path and the
    # variable is forwarded by name, so passphrase-protected keys work
    # inside the container through the host's unlocked agent.
    mounts = _values_after(run_inv, "-v")
    assert f"{agent_sock}:{agent_sock}" in mounts, mounts
    assert "SSH_AUTH_SOCK" in _values_after(run_inv, "-e"), run_inv
