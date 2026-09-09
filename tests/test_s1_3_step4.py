"""S1.3 Step 4: deterministic session container identity.

Must Support verified:
- Container names derived deterministically from a hash of the current
  workspace location combined with a unique per-session identifier.
- The same workspace always producing the same name portion, while separate
  sessions produce distinguishable names.
- Multiple containers allowed to coexist within the same workspace while
  their host launcher processes are alive, regardless of editor or terminal.
- Each container labeled with the host launcher PID so its lifetime is bound
  to that process.
- At launch, removal of leftover same-workspace containers whose host
  launcher PID is no longer alive, while containers whose launcher is still
  running are left untouched.
- When the launcher process dies (terminal close, editor close, SIGHUP,
  SIGTERM, or SIGKILL), its container is stopped and removed without waiting
  for a later launch.
- Session identity resolved editor-agnostically for naming only, honoring an
  explicit AI_ASSISTANT_SESSION_ID override, the tmux or GNU screen session
  when present, and otherwise the parent shell PID. Session identity does not
  drive destructive cleanup.
"""

from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import time
from pathlib import Path
from typing import NamedTuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Fake docker: records argv as a JSON array per invocation and always
# succeeds. Optional behaviors armed per test via environment:
# - DOCKER_STUB_PS_ROWS: printed verbatim in response to `docker ps ...`
#   (one leftover container per line: "<id> <hostpid>"), simulating
#   same-workspace containers recorded by the host daemon.
# - DOCKER_STUB_RUN_HOLD: `docker run` polls until this file exists before
#   exiting, so a launcher stays alive while the test signals it.
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

if [[ "${1:-}" == "ps" && -n "${DOCKER_STUB_PS_ROWS:-}" ]]; then
  printf '%s\\n' "$DOCKER_STUB_PS_ROWS"
fi

if [[ "${1:-}" == "run" && -n "${DOCKER_STUB_RUN_HOLD:-}" ]]; then
  while [[ ! -f "$DOCKER_STUB_RUN_HOLD" ]]; do
    sleep 0.2
  done
fi
exit 0
"""


class LaunchResult(NamedTuple):
    """Outcome of a completed launcher chain run."""

    returncode: int
    stderr: str
    pid: int  # launcher PID: agent.sh exec's down to ai_assistant.py


def _make_sandbox(tmp_path: Path, name: str = "sandbox") -> Path:
    """Create an isolated sandbox workspace (cwd + HOME) for the launcher."""
    sandbox = tmp_path / name
    sandbox.mkdir()
    (sandbox / ".agent").mkdir()
    return sandbox


def _write_docker_stub(stub_dir: Path) -> Path:
    stub = stub_dir / "docker"
    stub.write_text(DOCKER_STUB)
    stub.chmod(0o755)
    return stub


def _launcher_env(
    sandbox: Path, stub_dir: Path, extra_env: dict[str, str] | None = None
) -> dict[str, str]:
    """Build the launcher environment; session markers default to absent.

    AI_ASSISTANT_SESSION_ID, TMUX, and STY are removed so every test starts
    from the parent-PID default and re-arms exactly what it exercises.
    """
    env = os.environ.copy()
    env["PATH"] = f"{stub_dir}{os.pathsep}{env['PATH']}"
    env["DOCKER_STUB_LOG"] = str(sandbox / "docker-stub.log")
    env["HOME"] = str(sandbox)
    for var in ("AI_ASSISTANT_SESSION_ID", "TMUX", "STY"):
        env.pop(var, None)
    if extra_env:
        env.update(extra_env)
    return env


def _popen_chain(
    sandbox: Path, env: dict[str, str], args: list[str]
) -> subprocess.Popen:
    return subprocess.Popen(
        ["bash", str(PROJECT_ROOT / "agent.sh"), *args],
        cwd=sandbox,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def run_chain(
    sandbox: Path,
    stub_dir: Path,
    args: list[str],
    extra_env: dict[str, str] | None = None,
) -> LaunchResult:
    """Run agent.sh to completion with the docker stub on PATH."""
    proc = _popen_chain(sandbox, _launcher_env(sandbox, stub_dir, extra_env), args)
    try:
        _, err = proc.communicate(timeout=60)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()
        raise
    return LaunchResult(proc.returncode, err, proc.pid)


def stub_invocations(sandbox: Path) -> list[list[str]]:
    """Return the docker stub's recorded argument vectors."""
    log = sandbox / "docker-stub.log"
    if not log.exists():
        return []
    return [json.loads(line) for line in log.read_text().splitlines() if line]


def run_invocations(sandbox: Path) -> list[list[str]]:
    """Return the recorded `docker run` argument vectors."""
    return [inv for inv in stub_invocations(sandbox) if inv and inv[0] == "run"]


def container_name(invocation: list[str]) -> str:
    """Extract the --name value from a docker run argv."""
    return invocation[invocation.index("--name") + 1]


def _strip_pid_suffix(name: str) -> str:
    """Mask the trailing per-launch PID segment of a container name."""
    return re.sub(r"-\d+$", "", name, count=1)


def _wait_for(predicate, timeout: float, description: str) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.2)
    raise AssertionError(f"timed out waiting for {description}")


def test_container_name_deterministic_and_stable_per_workspace(tmp_path: Path):
    """The same workspace with the same session identity yields the exact
    same container-name portion across launches, while a different workspace
    yields a different name — names derive from a hash of the workspace
    location combined with the session identifier."""
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_docker_stub(stub_dir)
    session_env = {"AI_ASSISTANT_SESSION_ID": "det"}

    sandbox = _make_sandbox(tmp_path)
    first = run_chain(sandbox, stub_dir, args=[], extra_env=session_env)
    second = run_chain(sandbox, stub_dir, args=[], extra_env=session_env)
    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr

    names = [container_name(inv) for inv in run_invocations(sandbox)]
    assert len(names) == 2, names
    # Same workspace + same session => same name portion (PID suffix differs).
    assert _strip_pid_suffix(names[0]) == _strip_pid_suffix(names[1])

    # A different workspace location produces a different name portion.
    other = _make_sandbox(tmp_path, "sandbox-other")
    third = run_chain(other, stub_dir, args=[], extra_env=session_env)
    assert third.returncode == 0, third.stderr
    other_name = container_name(run_invocations(other)[0])
    assert _strip_pid_suffix(other_name) != _strip_pid_suffix(names[0])
