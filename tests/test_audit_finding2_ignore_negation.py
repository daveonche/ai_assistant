"""Reproducer test for security-audit Finding 2 (.aiderignore negation).

Asserts the secure behavior: the union merge of the agent-side and
project-root .aiderignore must be monotonic — root-supplied negation
patterns (!pattern) must not be able to unignore paths that the
agent-side ignore file protects.

Fails against the current implementation because _merge_aiderignore()
appends root-only patterns (negations included) after the agent
patterns, and gitignore semantics are last-match-wins.
"""

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

# Paths the agent-side ignore policy protects (secret material), and the
# root-supplied negations that would unignore them under last-match-wins.
AGENT_IGNORE = ".env\n**/*.pem\n"
ROOT_IGNORE = "!.env\n!**/*.pem\n"

# Recording docker stub: same contract as the other reproducer modules;
# the run case snapshots the --aiderignore file mid-session.
DOCKER_STUB = """\
#!/usr/bin/env bash
# Recording docker stub for security-audit reproducer tests.
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
    # Snapshot config/ignore files while the container is running.
    prev=""
    for arg in "$@"; do
      case "$prev" in
        --config|--aiderignore)
          cp -- "$arg" "$STUB_DIR/snapshot-$(basename -- "$arg")" 2>/dev/null || true
          ;;
      esac
      prev="$arg"
    done
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
    env["AI_ASSISTANT_SESSION_ID"] = "audit-finding-2"
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


def test_root_negations_cannot_unignore_protected_paths(tmp_path):
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)

    (sandbox / ".agent" / ".aiderignore").write_text(AGENT_IGNORE)
    (sandbox / ".aiderignore").write_text(ROOT_IGNORE)

    result = run_chain(sandbox, stub_dir, [])
    assert result.returncode == 0, result.stderr

    snapshot = stub_dir / "snapshot-.aiderignore"
    assert snapshot.is_file(), "launcher did not pass a merged --aiderignore file"

    merged_lines = snapshot.read_text().splitlines()
    for negation in ("!.env", "!**/*.pem"):
        assert negation not in merged_lines, (
            "root negation survived the merge and unignores a protected "
            f"path: {negation!r}"
        )
    for protected in (".env", "**/*.pem"):
        assert protected in merged_lines, (
            "agent-side deny pattern missing from the merged ignore file: "
            f"{protected!r}"
        )
