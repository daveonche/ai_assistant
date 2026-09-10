"""Tests for S1.5 Step 3: Enable container engine access from inside the container."""

from __future__ import annotations

import grp
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
# Recording docker stub for S1.5 Step 3 tests.
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
    env["AI_ASSISTANT_SESSION_ID"] = "s1-5-3"
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


def _docker_gid() -> int | None:
    """Return the host docker group's GID, or None when unresolvable."""
    try:
        return grp.getgrnam("docker").gr_gid
    except (KeyError, ImportError):
        return None


def test_engine_socket_mounted_into_session_container(tmp_path):
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)

    result = run_chain(sandbox, stub_dir, [])
    assert result.returncode == 0, result.stderr

    run_inv = _last_run(stub_invocations(sandbox))

    # The host engine socket is bind-mounted into the session container at
    # the identical path (the engine CLI's default), so in-container engine
    # commands reach the host daemon.
    mounts = _values_after(run_inv, "-v")
    assert "/var/run/docker.sock:/var/run/docker.sock" in mounts, mounts


def test_engine_group_mapping_uses_host_docker_gid(tmp_path):
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)

    result = run_chain(sandbox, stub_dir, [])
    assert result.returncode == 0, result.stderr

    run_inv = _last_run(stub_invocations(sandbox))
    group_adds = _values_after(run_inv, "--group-add")

    gid = _docker_gid()
    if gid is not None:
        # Group-based permission mapping: the launcher resolves the host
        # docker group's GID and maps it into the container (no privilege
        # elevation — membership, not root).
        assert str(gid) in group_adds, group_adds
    else:
        # Documented assumption: the environment's group database decides
        # the branch. Without a docker group, the launcher reports the
        # skipped mapping instead of failing silently.
        assert "host 'docker' group not found" in result.stderr, result.stderr


def test_no_engine_redirect_in_run_environment(tmp_path):
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)

    result = run_chain(sandbox, stub_dir, [])
    assert result.returncode == 0, result.stderr

    run_inv = _last_run(stub_invocations(sandbox))

    # The launcher forwards no DOCKER_HOST override into the container, so
    # engine commands issued inside it use the CLI's default socket path —
    # which Test 1 confirmed is the mounted host daemon socket.
    env_values = _values_after(run_inv, "-e")
    assert not any(
        value.startswith("DOCKER_HOST=") for value in env_values
    ), env_values
