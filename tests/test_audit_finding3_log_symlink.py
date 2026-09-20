"""Reproducer tests for security-audit Finding 3 (symlink-following writes).

Asserts the secure behavior: files the launcher writes at predictable
shared-temp paths — the per-session command log and the merged-config
intermediates — must not follow a pre-planted symlink to append to,
overwrite, or chmod an arbitrary victim file outside the launcher's
scope.

Fails against the current implementation because _trace_command() opens
the log with O_CREAT|O_APPEND (no O_NOFOLLOW) and chmod()s the path, and
_write_merged_value_file() writes intermediates with Path.write_text();
all of these follow symlinks.
"""

from __future__ import annotations

import hashlib
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

# Recording docker stub: same contract as the other reproducer modules.
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
    # Created here, not only in _launcher_env: the symlink-target tests
    # write the victim file into sandbox/home before the launcher runs.
    (sandbox / "home").mkdir()
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
    env["AI_ASSISTANT_SESSION_ID"] = "audit-finding-3"
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


def _command_log_path(sandbox: Path, session_id: str) -> Path:
    """Replicate the launcher's command-log path derivation.

    Mirrors _configure_command_log: the log lives under ~/.cache/aider,
    named by workspace hash and session ID. HOME is redirected into the
    sandbox by _launcher_env, so the launcher's Path.home() resolves to
    sandbox/home — the same directory used here.
    """
    workspace_hash = hashlib.md5((str(sandbox.resolve()) + "\n").encode()).hexdigest()
    return (
        sandbox
        / "home"
        / ".cache"
        / "aider"
        / f"ai-assistant-{workspace_hash[:8]}-{session_id}.log"
    )


def test_command_log_symlink_does_not_reach_victim_file(tmp_path):
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)

    session_id = "audit-f3-log"
    victim = sandbox / "home" / "victim.txt"
    victim.write_text("victim original content\n")
    original_mode = victim.stat().st_mode & 0o777

    log_path = _command_log_path(sandbox, session_id)
    # The launcher creates ~/.cache/aider during _configure_command_log,
    # but the symlink must be planted before the launcher runs — an
    # attacker pre-creating the directory is part of the threat model.
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.symlink_to(victim)

    try:
        result = run_chain(
            sandbox, stub_dir, [], extra_env={"AI_ASSISTANT_SESSION_ID": session_id}
        )
        assert result.returncode == 0, result.stderr

        assert victim.read_text() == "victim original content\n", (
            "launcher appended to the command log through a planted symlink"
        )
        assert victim.stat().st_mode & 0o777 == original_mode, (
            "launcher chmod'ed the command log through a planted symlink"
        )
    finally:
        if log_path.is_symlink():
            log_path.unlink()


def test_merged_intermediate_symlink_does_not_reach_victim_file(tmp_path):
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)

    # Both config copies present -> the launcher writes the merged
    # intermediate to .agent/.merged/.aider.conf.yml. The victim holds
    # valid YAML so the merge proceeds to the write step.
    (sandbox / ".agent" / ".aider.conf.yml").write_text("model: gpt-4o\n")
    (sandbox / ".aider.conf.yml").write_text("model: gpt-4o-mini\n")

    victim = sandbox / "home" / "victim.txt"
    victim.write_text("model: victim\n")

    merged_dir = sandbox / ".agent" / ".merged"
    merged_dir.mkdir()
    (merged_dir / ".aider.conf.yml").symlink_to(victim)

    try:
        result = run_chain(sandbox, stub_dir, [])
        assert result.returncode == 0, result.stderr

        assert victim.read_text() == "model: victim\n", (
            "launcher wrote a merged-config intermediate through a planted "
            "symlink"
        )
    finally:
        _command_log_path(sandbox, "audit-finding-3").unlink(missing_ok=True)


def test_merged_ignore_symlink_does_not_reach_victim_file(tmp_path):
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)

    # Both ignore copies present -> the launcher writes the union
    # intermediate to .agent/.merged/.aiderignore. The symlink planted
    # there must never redirect the write onto the victim file.
    (sandbox / ".agent" / ".aiderignore").write_text("node_modules\n")
    (sandbox / ".aiderignore").write_text("dist\n")

    victim = sandbox / "home" / "victim.txt"
    victim.write_text("victim original content\n")

    merged_dir = sandbox / ".agent" / ".merged"
    merged_dir.mkdir()
    (merged_dir / ".aiderignore").symlink_to(victim)

    try:
        result = run_chain(sandbox, stub_dir, [])
        assert result.returncode == 0, result.stderr

        assert victim.read_text() == "victim original content\n", (
            "launcher wrote the merged ignore intermediate through a "
            "planted symlink"
        )
    finally:
        _command_log_path(sandbox, "audit-finding-3").unlink(missing_ok=True)
