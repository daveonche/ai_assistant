"""Tests for S1.3 Step 7: Enable interactive assistant session launch."""

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
# Recording docker stub for S1.3 Step 7 tests.
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
    env["AI_ASSISTANT_SESSION_ID"] = "s7"
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


def test_run_uses_built_image_session_identity_and_exposes_workspace(tmp_path):
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)

    result = run_chain(sandbox, stub_dir, [])
    assert result.returncode == 0, result.stderr

    run_inv = _last_run(stub_invocations(sandbox))

    # The container is started from the built image: the image token is the
    # last docker argument, with every assistant argument following it.
    image_idx = run_inv.index(AIDER_IMAGE)
    assert image_idx > 0

    # Session identity: a dedicated container name plus session and
    # workspace labels bind the run to this session/workspace.
    names = _values_after(run_inv, "--name")
    assert len(names) == 1 and names[0], run_inv
    labels = _values_after(run_inv, "--label")
    assert "aider.session=s7" in labels, labels
    assert any(l.startswith("aider.dir=") for l in labels), labels

    # Workspace exposure: the current workspace is bind-mounted at its own
    # path and used as the container working directory.
    mounts = _values_after(run_inv, "-v")
    assert f"{sandbox}:{sandbox}" in mounts, mounts
    assert _values_after(run_inv, "-w") == [str(sandbox)]
