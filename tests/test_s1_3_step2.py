"""S1.3 Step 2: command tracing and debug output.

Must Support verified:
- A single tracing routine through which every command the launcher performs
  is recorded before it runs.
- Verbose output that prints each traced command when the debug flag is
  enabled.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SESSION_ID = "s13-step2"

# Fake docker: records argv as a JSON array per invocation. When verification
# is armed via DOCKER_CMD_LOG + DOCKER_STUB_MISSING, it first asserts that its
# own trace line already exists in the launcher's command log, proving every
# command is recorded before it runs; an untraced command is appended to the
# missing marker and fails the invocation.
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

if [[ -n "${DOCKER_CMD_LOG:-}" && -n "${DOCKER_STUB_MISSING:-}" ]]; then
  trace="+ docker $*"
  if ! grep -Fqx -- "$trace" "$DOCKER_CMD_LOG"; then
    printf '%s\\n' "$trace" >> "$DOCKER_STUB_MISSING"
    exit 1
  fi
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


def stub_invocations(sandbox: Path) -> list[list[str]]:
    """Return the docker stub's recorded argument vectors."""
    log = sandbox / "docker-stub.log"
    if not log.exists():
        return []
    return [json.loads(line) for line in log.read_text().splitlines() if line]


def command_log_path(result: subprocess.CompletedProcess) -> Path:
    """Extract the per-session command log path announced in debug mode."""
    prefix = "Command log: "
    for line in result.stderr.splitlines():
        if line.startswith(prefix):
            return Path(line[len(prefix):])
    raise AssertionError("Command log path not announced in debug output")


def test_every_command_recorded_before_execution(tmp_path: Path):
    """Every launcher Docker command is traced before it runs: a verifying
    stub checks its own trace line exists in the command log at invocation
    time and fails the invocation if it was not pre-recorded."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_docker_stub(stub_dir)

    # Phase 1: discover the per-session command log path, announced by the
    # launcher itself in debug mode (no launcher internals replicated).
    discovery = run_chain(sandbox, stub_dir, args=["--debug"])
    assert discovery.returncode == 0, discovery.stderr
    command_log = command_log_path(discovery)
    assert command_log.is_file(), "command log was not created"

    # Phase 2: truncate the log, arm the stub's pre-execution check, rerun.
    command_log.write_text("")
    result = run_chain(
        sandbox,
        stub_dir,
        args=["--debug"],
        extra_env={
            "DOCKER_CMD_LOG": str(command_log),
            "DOCKER_STUB_MISSING": str(sandbox / "untraced.log"),
        },
    )

    assert result.returncode == 0, result.stderr
    missing = sandbox / "untraced.log"
    assert not missing.exists(), (
        f"commands ran without being recorded first: {missing.read_text()}"
    )
    invocations = stub_invocations(sandbox)
    assert invocations, "docker stub was never invoked; chain did not complete"
    # The availability gate runs first and is traced like every other command.
    assert invocations[0] == ["version"], invocations[0]
