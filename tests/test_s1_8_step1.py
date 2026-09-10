"""S1.8 Step 1: surfacing recent command-log entries during debug runs.

Must Support verified:
- A capability to surface recent log entries during a debug run.

Items 1-2 of this step (every engine command recorded to a log; a debug
mode printing full command details) are already covered by
tests/test_s1_3_step2.py and are intentionally not duplicated here.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SESSION_ID = "s18-step1"

# Fake docker: records argv as a JSON array per invocation (same recording
# body as tests/test_s1_3_step2.py). When DOCKER_STUB_FAIL names the stub's
# first argument, it exits nonzero after recording, driving the launcher to
# a deterministic failure checkpoint.
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


def _make_sandbox(tmp_path: Path) -> Path:
    """Create an isolated sandbox cwd and HOME for the launcher."""
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir()
    (sandbox / ".agent").mkdir()
    return sandbox


def _write_docker_stub(stub_dir: Path) -> Path:
    stub = stub_dir / "docker"
    stub.write_text(DOCKER_STUB)
    stub.chmod(0o755)
    return stub


def run_chain(
    sandbox: Path,
    stub_dir: Path,
    args: list[str],
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    """Run agent.sh from the sandbox with the docker stub on PATH."""
    env = os.environ.copy()
    env["PATH"] = f"{stub_dir}{os.pathsep}{env['PATH']}"
    env["DOCKER_STUB_LOG"] = str(sandbox / "docker-stub.log")
    env["HOME"] = str(sandbox)
    env["AI_ASSISTANT_SESSION_ID"] = SESSION_ID
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        ["bash", str(PROJECT_ROOT / "agent.sh"), *args],
        cwd=sandbox,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )


def command_log_path(result: subprocess.CompletedProcess) -> Path:
    """Extract the per-session command log path announced in debug mode."""
    prefix = "Command log: "
    for line in result.stderr.splitlines():
        if line.startswith(prefix):
            return Path(line[len(prefix):])
    raise AssertionError("Command log path not announced in debug output")


def test_failure_checkpoint_surfaces_recent_command_log_entries(tmp_path: Path):
    """A debug run that reaches a failure checkpoint surfaces the recent
    command-log entries under the documented header, matching exactly what
    the log recorded."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_docker_stub(stub_dir)

    # The availability gate fails, driving the launcher to the failure
    # checkpoint; --debug arms the recent-entry surfacing.
    result = run_chain(
        sandbox,
        stub_dir,
        args=["--debug"],
        extra_env={"DOCKER_STUB_FAIL": "version"},
    )

    assert result.returncode == 1, result.stderr

    # The traced command was recorded before it ran; the log path was
    # announced by the launcher itself in debug output.
    command_log = command_log_path(result)
    assert command_log.is_file(), "command log was not created"
    log_lines = command_log.read_text().splitlines()
    assert log_lines == ["+ docker version"]

    # The failure checkpoint surfaces the recent entries under the
    # documented header, matching the log's recorded lines.
    stderr_lines = result.stderr.splitlines()
    assert "--- Recent command log entries ---" in stderr_lines
    header_index = stderr_lines.index("--- Recent command log entries ---")
    surfaced = [
        line
        for line in stderr_lines[header_index + 1:]
        if line.startswith("+ docker")
    ]
    assert surfaced == log_lines
