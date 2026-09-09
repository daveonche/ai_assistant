"""S1.3 Step 1: the .agent entry file completes the delegation chain.

Must Support verified:
- A launcher entry file within the `.agent/` configuration directory that
  executes on the host and completes the delegation chain started by
  agent.sh.
- Accepting a debug flag that turns on verbose output.
- Forwarding all remaining user arguments, unchanged and in order, to the
  assistant environment launch.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DOCKER_STUB = """\
#!/usr/bin/env bash
set -euo pipefail
# Fake docker: records argv as a JSON array per invocation and always succeeds.
json="["
for arg in "$@"; do
  esc=${arg//\\\\/\\\\\\\\}
  esc=${esc//\\"/\\\\\\\"}
  json+="\\"$esc\\","
done
printf '%s\\n' "${json%,}]" >> "$DOCKER_STUB_LOG"
exit 0
"""


def _write_docker_stub(stub_dir: Path) -> Path:
    stub = stub_dir / "docker"
    stub.write_text(DOCKER_STUB)
    stub.chmod(0o755)
    return stub


def _make_sandbox(tmp_path: Path) -> Path:
    """Create an isolated sandbox cwd and HOME for the launcher."""
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir()
    (sandbox / ".agent").mkdir()
    home = tmp_path / "home"
    home.mkdir()
    return sandbox


def run_chain(sandbox: Path, stub_dir: Path, args: list[str]) -> subprocess.CompletedProcess:
    """Run agent.sh from the sandbox with the docker stub on PATH."""
    env = os.environ.copy()
    env["PATH"] = f"{stub_dir}{os.pathsep}{env['PATH']}"
    env["DOCKER_STUB_LOG"] = str(sandbox / "docker-stub.log")
    env["HOME"] = str(sandbox)
    env.pop("AI_ASSISTANT_SESSION_ID", None)
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


def test_agent_chain_completes_via_launcher(tmp_path: Path):
    """agent.sh -> .agent/ai-assistant.sh -> .agent/ai_assistant.py runs the
    real launcher, which reaches the container engine (via the stub)."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_docker_stub(stub_dir)

    result = run_chain(sandbox, stub_dir, args=[])

    assert result.returncode == 0, result.stderr
    invocations = stub_invocations(sandbox)
    assert invocations, "docker stub was never invoked; chain did not complete"
    # _docker_available() runs first as the availability gate.
    assert invocations[0][0] == "version", invocations[0]
    # The launcher attempts to launch the assistant container.
    assert any(inv[0] == "run" for inv in invocations), invocations


def test_launcher_debug_flag_enables_verbose_output(tmp_path: Path):
    """--debug prints each performed command before it runs; without the
    flag no trace output appears while behavior stays otherwise identical."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_docker_stub(stub_dir)

    # With --debug: every performed command is printed before it runs.
    debug_run = run_chain(sandbox, stub_dir, args=["--debug"])
    assert debug_run.returncode == 0, debug_run.stderr
    assert "+ docker version" in debug_run.stderr  # traced availability gate
    assert "Command log:" in debug_run.stderr  # log path announced

    # Without the flag: no trace output, behavior otherwise identical.
    before = len(stub_invocations(sandbox))
    quiet_run = run_chain(sandbox, stub_dir, args=[])
    assert quiet_run.returncode == 0, quiet_run.stderr
    assert "+ docker" not in quiet_run.stderr
    assert len(stub_invocations(sandbox)) > before  # same work still done


def test_launcher_forwards_arguments_unchanged_in_order(tmp_path: Path):
    """User arguments appear at the tail of the docker run argv verbatim and
    in order; the debug flag is consumed by the launcher, never forwarded."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_docker_stub(stub_dir)

    user_args = ["--model", "gpt-4", "--message", "verify forwarding"]
    result = run_chain(sandbox, stub_dir, args=["--debug", *user_args])
    assert result.returncode == 0, result.stderr

    run_inv = next(
        inv for inv in stub_invocations(sandbox) if inv[0] == "run"
    )
    # main() pops the leading debug flag and appends the rest verbatim after
    # all launcher-owned args, so the run argv must END with the user args
    # exactly as given (grouping preserved: "verify forwarding" is one arg).
    assert run_inv[-len(user_args):] == user_args
    # The debug flag is consumed by the launcher, never forwarded.
    assert "--debug" not in run_inv
