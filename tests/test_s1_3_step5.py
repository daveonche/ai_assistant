"""Tests for S1.3 Step 5: Enable container image build management."""

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

# Recording docker stub: image inspect succeeds only for tags the launcher
# itself has tagged/built, so the cache-miss/cache-hit/rebuild decisions are
# driven by real launcher commands. Digest probes (--format) always fail,
# making the cache tag a deterministic hash of the Dockerfile bytes alone.
DOCKER_STUB = """\
#!/usr/bin/env bash
# Recording docker stub for S1.3 Step 5 tests.
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
    env["AI_ASSISTANT_SESSION_ID"] = "s5"
    (sandbox / "home").mkdir(exist_ok=True)
    return env


def run_chain(
    sandbox: Path, stub_dir: Path, args: list[str]
) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(sandbox / "agent.sh"), *args],
        cwd=sandbox,
        env=_launcher_env(sandbox, stub_dir),
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


def _builds(invocations: list[list[str]]) -> list[list[str]]:
    return [inv for inv in invocations if inv[:2] == ["docker", "build"]]


def test_missing_image_triggers_build_from_agent_definition(tmp_path):
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)

    result = run_chain(sandbox, stub_dir, [])
    assert result.returncode == 0, result.stderr

    invocations = stub_invocations(sandbox)
    builds = _builds(invocations)
    assert len(builds) == 1, invocations

    dockerfile = sandbox / ".agent" / "Dockerfile.aider"
    build = builds[0]
    f_idx = build.index("-f")
    t_idx = build.index("-t")
    assert build[f_idx + 1] == str(dockerfile)
    assert build[t_idx + 1] == "aider-agent:latest"
    assert build[-1] == str(sandbox / ".agent")

    runs = [inv for inv in invocations if inv[:2] == ["docker", "run"]]
    assert runs, "assistant should launch after the build"
    assert invocations.index(build) < invocations.index(runs[0])
