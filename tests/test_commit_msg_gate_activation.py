"""Commit-msg gate activation during launcher host-side setup.

Must Support verified:
- A capability to activate the repo's commit-msg gate automatically when
  core.hooksPath is unset.

The gate's subject-format enforcement itself is covered by
tests/test_commit_msg_hook.py; this module covers only the launcher's
activation behavior in _ensure_commit_msg_gate.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SESSION_ID = "gate-activation"

# Same recording docker stub as tests/test_s1_8_step1.py: every invocation
# is appended to $DOCKER_STUB_LOG as a JSON argv array and exits 0, so the
# launcher chain runs to completion without a real daemon.
DOCKER_STUB = """\
#!/usr/bin/env bash
set -euo pipefail
json="["
for arg in "$@"; do
  esc=${arg//\\\\/\\\\\\\\}
  esc=${esc//\\"/\\\\\\\"}
  json+="\\"$esc\\","
done
printf '%s\\n' "${json%,}]" >> "$DOCKER_STUB_LOG"

if [[ -n "${DOCKER_STUB_FAIL:-}" && "${1:-}" == "${DOCKER_STUB_FAIL}" ]]; then
  exit 1
fi
exit 0
"""


def _git_env(sandbox: Path) -> dict[str, str]:
    """Return an env that isolates git config to the sandbox."""
    env = os.environ.copy()
    env["HOME"] = str(sandbox)
    env["GIT_CONFIG_GLOBAL"] = str(sandbox / ".gitconfig")
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    return env


def _make_git_sandbox(tmp_path: Path) -> Path:
    """Create an isolated git-repo sandbox cwd and HOME for the launcher."""
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir()
    (sandbox / ".agent").mkdir()
    subprocess.run(
        ["git", "init", "-q", str(sandbox)],
        check=True,
        capture_output=True,
        env=_git_env(sandbox),
    )
    return sandbox


def _write_commit_msg_gate(sandbox: Path) -> None:
    """Ship the gate files the launcher looks for in the project root."""
    hook = sandbox / ".githooks" / "commit-msg"
    hook.parent.mkdir()
    hook.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    hook.chmod(0o755)


def _write_docker_stub(stub_dir: Path) -> Path:
    stub = stub_dir / "docker"
    stub.write_text(DOCKER_STUB)
    stub.chmod(0o755)
    return stub


def run_chain(
    sandbox: Path,
    stub_dir: Path,
    args: list[str],
) -> subprocess.CompletedProcess:
    """Run agent.sh from the sandbox with the docker stub on PATH."""
    env = _git_env(sandbox)
    env["PATH"] = f"{stub_dir}{os.pathsep}{env['PATH']}"
    env["DOCKER_STUB_LOG"] = str(sandbox / "docker-stub.log")
    env["AI_ASSISTANT_SESSION_ID"] = SESSION_ID
    return subprocess.run(
        ["bash", str(PROJECT_ROOT / "agent.sh"), *args],
        cwd=sandbox,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )


def _hooks_path(sandbox: Path) -> str | None:
    """Return the sandbox repo's core.hooksPath, or None when unset."""
    result = subprocess.run(
        ["git", "-C", str(sandbox), "config", "core.hooksPath"],
        capture_output=True,
        text=True,
        env=_git_env(sandbox),
    )
    return result.stdout.strip() if result.returncode == 0 else None


def test_gate_activated_when_unset(tmp_path: Path):
    """A launch in a git worktree that ships the gate sets core.hooksPath
    to .githooks, and a second launch leaves the value in place."""
    sandbox = _make_git_sandbox(tmp_path)
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_docker_stub(stub_dir)
    _write_commit_msg_gate(sandbox)

    first = run_chain(sandbox, stub_dir, args=[])
    assert first.returncode == 0, first.stderr
    assert _hooks_path(sandbox) == ".githooks"

    # Idempotent: the second launch sees the value already set and must
    # leave it exactly as recorded by the first run.
    second = run_chain(sandbox, stub_dir, args=[])
    assert second.returncode == 0, second.stderr
    assert _hooks_path(sandbox) == ".githooks"


def test_existing_hooks_path_is_never_overwritten(tmp_path: Path):
    """A pre-set core.hooksPath (another hook manager) survives a launch
    unchanged: the launcher activates the gate only when unset."""
    sandbox = _make_git_sandbox(tmp_path)
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_docker_stub(stub_dir)
    _write_commit_msg_gate(sandbox)
    subprocess.run(
        ["git", "-C", str(sandbox), "config", "core.hooksPath", ".my-hooks"],
        check=True,
        capture_output=True,
        env=_git_env(sandbox),
    )

    result = run_chain(sandbox, stub_dir, args=[])
    assert result.returncode == 0, result.stderr
    assert _hooks_path(sandbox) == ".my-hooks"


def test_no_gate_files_leaves_hooks_path_unset(tmp_path: Path):
    """Without .githooks/commit-msg the launcher writes no hooksPath, so
    projects that never shipped the gate stay untouched."""
    sandbox = _make_git_sandbox(tmp_path)
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_docker_stub(stub_dir)

    result = run_chain(sandbox, stub_dir, args=[])
    assert result.returncode == 0, result.stderr
    assert _hooks_path(sandbox) is None


def test_non_executable_hook_warns_but_still_activates(tmp_path: Path):
    """A non-executable hook file cannot run even when hooksPath points
    at it; the launcher says so on stderr and still records the setting
    so the gate goes live as soon as the execute bit is fixed."""
    sandbox = _make_git_sandbox(tmp_path)
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_docker_stub(stub_dir)
    _write_commit_msg_gate(sandbox)
    (sandbox / ".githooks" / "commit-msg").chmod(0o644)

    result = run_chain(sandbox, stub_dir, args=[])
    assert result.returncode == 0, result.stderr
    assert _hooks_path(sandbox) == ".githooks"
    assert "not executable" in result.stderr
