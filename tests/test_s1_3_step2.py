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

if [[ -n "${DOCKER_STUB_TRACE:-}" ]]; then
  printf '+ docker %s\n' "$*" >> "$DOCKER_STUB_TRACE"
fi

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


def test_command_log_matches_executed_invocations_in_order(tmp_path: Path):
    """In normal (non-debug) mode the launcher's command log still records
    every executed docker command, in the same order the stub received them
    and in the identical trace-line format — no command bypasses the single
    tracing routine."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_docker_stub(stub_dir)

    # Phase 1: discover the per-session command log path in debug mode.
    discovery = run_chain(sandbox, stub_dir, args=["--debug"])
    assert discovery.returncode == 0, discovery.stderr
    command_log = command_log_path(discovery)

    # Phase 2: truncate both records, arm the stub's own trace, rerun in
    # normal mode (no --debug) and compare the two sides.
    command_log.write_text("")
    stub_trace = sandbox / "stub-trace.log"
    result = run_chain(
        sandbox,
        stub_dir,
        args=[],
        extra_env={"DOCKER_STUB_TRACE": str(stub_trace)},
    )

    assert result.returncode == 0, result.stderr
    launcher_lines = command_log.read_text().splitlines()
    stub_lines = stub_trace.read_text().splitlines()
    assert launcher_lines, "launcher recorded no commands; chain did not run"
    assert stub_lines, "docker stub was never invoked; chain did not run"
    # Every executed command was logged before running, 1:1, same order,
    # same format ("+ docker <args>"): logging is independent of debug mode.
    assert launcher_lines == stub_lines


def test_debug_mode_prints_each_performed_command(tmp_path: Path):
    """With --debug, every performed docker command appears in stderr as a
    trace line, in invocation order, with no duplicates or omissions."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_docker_stub(stub_dir)

    result = run_chain(sandbox, stub_dir, args=["--debug"])
    assert result.returncode == 0, result.stderr

    invocations = stub_invocations(sandbox)
    assert invocations, "docker stub was never invoked; chain did not run"

    stderr_lines = result.stderr.splitlines()
    trace_lines = [line for line in stderr_lines if line.startswith("+ docker")]

    # Every performed command was printed before it ran: one trace line per
    # stub invocation, nothing missing, nothing extra.
    assert len(trace_lines) == len(invocations), (
        f"{len(trace_lines)} trace lines vs {len(invocations)} invocations"
    )

    # Rebuild the expected trace text for each recorded invocation and
    # compare the sequences in order (first: availability gate, last: launch).
    expected = ["+ docker " + " ".join(inv) for inv in invocations]
    assert trace_lines == expected
    assert trace_lines[0] == "+ docker version"
    assert trace_lines[-1].startswith("+ docker run")


def test_non_debug_mode_no_trace_and_identical_behavior(tmp_path: Path):
    """Without the debug flag no trace output appears in stderr while the
    launcher performs exactly the same sequence of docker commands as the
    debug baseline — identical behavior, only the verbose output differs."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_docker_stub(stub_dir)

    # Baseline: debug run defines the canonical invocation sequence.
    debug_run = run_chain(sandbox, stub_dir, args=["--debug"])
    assert debug_run.returncode == 0, debug_run.stderr
    baseline = stub_invocations(sandbox)
    assert baseline, "docker stub was never invoked in the debug run"

    # Normal mode: same sandbox, same stub log (append-only).
    before = len(baseline)
    quiet_run = run_chain(sandbox, stub_dir, args=[])
    assert quiet_run.returncode == 0, quiet_run.stderr

    # No verbose trace output in normal mode.
    assert "+ docker" not in quiet_run.stderr

    # Identical behavior: the new invocations match the baseline 1:1, in order.
    new_invocations = stub_invocations(sandbox)[before:]
    assert new_invocations == baseline
