"""S1.3 Step 3: container engine availability gating.

Must Support verified:
- A pre-launch check that confirms the container engine is available before
  any container lifecycle action is attempted.
- When the engine is missing, an immediate exit with a clear, actionable
  error and an unsuccessful result instead of a crash or partial run.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Fake docker: records argv as a JSON array per invocation. When
# FAIL_VERSION is set, a `version` probe exits 1 — simulating a missing
# container engine while every other subcommand would still succeed.
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

if [[ -n "${FAIL_VERSION:-}" && "$1" == "version" ]]; then
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
    env["AI_ASSISTANT_SESSION_ID"] = "s13-step3"
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


def test_unavailable_engine_gates_all_lifecycle_actions(tmp_path: Path):
    """With a failing availability probe, the launcher stops immediately:
    the probe is the only engine invocation; no build, tag, or run is ever
    attempted."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_docker_stub(stub_dir)

    result = run_chain(sandbox, stub_dir, args=[], extra_env={"FAIL_VERSION": "1"})

    # Gate: the probe ran and nothing else — no build/run lifecycle action.
    assert result.returncode != 0, result.stderr
    assert stub_invocations(sandbox) == [["version"]], stub_invocations(sandbox)


def test_missing_engine_exits_unsuccessfully_with_actionable_error(tmp_path: Path):
    """With the engine missing, the launcher exits unsuccessfully with a
    clear, actionable error — no traceback, no partial lifecycle run."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_docker_stub(stub_dir)

    result = run_chain(sandbox, stub_dir, args=[], extra_env={"FAIL_VERSION": "1"})

    # Unsuccessful result.
    assert result.returncode != 0
    # No crash: a Python traceback means the launcher died instead of
    # handling the missing engine deliberately.
    assert "Traceback" not in result.stderr
    # Clear, actionable error: names what is missing and what to do next.
    error_text = (result.stderr + result.stdout).lower()
    assert "docker" in error_text
    assert "install" in error_text or "path" in error_text
