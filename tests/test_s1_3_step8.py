"""Tests for S1.3 Step 8: Enable session container cleanup."""

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

# Recording docker stub (same contract as Steps 5–7), with one addition:
# the ps branch prints the contents of ps_output.txt when that file exists,
# letting a test seed the container list the launcher's launch-time cleanup
# sees (e.g., a live container from another session).
DOCKER_STUB = """\
#!/usr/bin/env bash
# Recording docker stub for S1.3 Step 8 tests.
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
  ps)
    if [[ -f "$STUB_DIR/ps_output.txt" ]]; then
      cat "$STUB_DIR/ps_output.txt"
    fi
    exit 0
    ;;
  rm)
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
    env["AI_ASSISTANT_SESSION_ID"] = "s8"
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


def test_session_container_removed_when_assistant_session_ends(tmp_path):
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)

    result = run_chain(sandbox, stub_dir, [])

    # The launcher returns cleanly once the assistant session ends.
    assert result.returncode == 0, result.stderr

    run_inv = _last_run(stub_invocations(sandbox))

    # Session-end removal is engine-side: --rm sits among the docker flags
    # (before the image token), so the engine stops and removes the session
    # container automatically when the session ends.
    image_idx = run_inv.index(AIDER_IMAGE)
    assert "--rm" in run_inv[:image_idx], run_inv


def test_other_sessions_untouched_and_rerun_leaves_no_errors(tmp_path):
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)

    # Seed the container list with a live same-workspace container from
    # another session: its host launcher PID is this test process, which is
    # certainly alive during both launches.
    other_id = "other-session-container-01"
    (stub_dir / "ps_output.txt").write_text(
        f"{other_id} {os.getpid()}\n", encoding="utf-8"
    )

    offsets = []
    for _ in range(2):
        result = run_chain(sandbox, stub_dir, [])
        assert result.returncode == 0, result.stderr
        assert "Traceback" not in result.stderr
        assert "Error" not in result.stderr
        offsets.append(len(stub_invocations(sandbox)))

    invocations = stub_invocations(sandbox)

    # The other session's live container is never an rm target — neither at
    # launch-time cleanup nor after either session ends.
    rm_targets = [inv[-1] for inv in invocations if inv[0] == "rm"]
    assert other_id not in rm_targets, rm_targets

    # Session-end removal is engine-side (--rm): after each run invocation
    # the launcher issues no container-destructive command of its own.
    bounds = ((0, offsets[0]), (offsets[0], offsets[1]))
    for start, end in bounds:
        window = invocations[start:end]
        run_indices = [i for i, inv in enumerate(window) if inv[0] == "run"]
        assert run_indices, window
        after_run = window[run_indices[-1] + 1 :]
        assert not [
            inv for inv in after_run if inv[0] in ("rm", "stop", "kill")
        ], after_run
