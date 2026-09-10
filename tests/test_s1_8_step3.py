"""S1.8 Step 3: credential handling at launch.

Must Support verified:
- Credentials passed to the assistant only as environment variables at
  launch time (this test).
- No credential values written to any git-tracked file; command traces and
  logs that never reveal secret values (subsequent tests in this file).

Sentinel technique: unique fake credential values injected into the
launcher environment; every assertion greps for the value and, where
forwarding is verified, for the variable NAME.
"""

from __future__ import annotations

import json
import os
import subprocess
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SESSION_ID = "s18-step3"

# Credential variables evidenced in the launcher's forwarding set (the
# recorded docker run argv shows -e OPENAI_API_KEY -e GEMINI_API_KEY
# -e OPENROUTER_API_KEY -e HF_TOKEN); two are exercised here.
CREDENTIAL_VARS = ("OPENAI_API_KEY", "OPENROUTER_API_KEY")

# Fake docker: records argv as a JSON array per invocation (identical to
# tests/test_s1_8_step1.py, including the DOCKER_STUB_FAIL hook reused by
# the surfaced-recent-entries test later in this file).
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


def stub_invocations(sandbox: Path) -> list[list[str]]:
    """Parse the stub's recorded argv, one JSON array per invocation."""
    log = sandbox / "docker-stub.log"
    return [
        json.loads(line)
        for line in log.read_text().splitlines()
        if line.strip()
    ]


def test_credentials_forwarded_by_name_only(tmp_path: Path):
    """With sentinel credentials exported, the docker run argv forwards the
    variables by NAME only: adjacent (-e, NAME) pairs present, values absent
    from every recorded argv element."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_docker_stub(stub_dir)

    sentinels = {
        name: f"sentinel-{name.lower()}-{uuid.uuid4().hex}"
        for name in CREDENTIAL_VARS
    }
    result = run_chain(sandbox, stub_dir, args=[], extra_env=sentinels)
    assert result.returncode == 0, result.stderr

    invocations = stub_invocations(sandbox)
    runs = [inv for inv in invocations if inv[:1] == ["run"]]
    assert runs, "no docker run invocation was recorded"

    # Values appear nowhere in any recorded command line.
    for invocation in invocations:
        joined = " ".join(invocation)
        for sentinel in sentinels.values():
            assert sentinel not in joined

    # Names are forwarded as adjacent (-e, NAME) pairs: Docker injects the
    # value from the launcher environment at container start.
    run_argv = runs[-1]
    forwarded = {
        run_argv[i + 1]
        for i, arg in enumerate(run_argv)
        if arg == "-e" and i + 1 < len(run_argv)
    }
    for name in CREDENTIAL_VARS:
        assert name in forwarded, f"{name} not forwarded as -e NAME"
