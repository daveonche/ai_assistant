"""S1.3 Step 1: the .agent entry file completes the delegation chain.

Must Support verified:
- A launcher entry file within the `.agent/` configuration directory that
  executes on the host and completes the delegation chain started by
  agent.sh.
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
    assert invocations[0][:2] == ["version"], invocations[0]
    # The launcher attempts to launch the assistant container.
    assert any(inv[:2] == ["run"] for inv in invocations), invocations
