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


def _git(*args: str) -> subprocess.CompletedProcess:
    """Run a git command from the project root."""
    return subprocess.run(
        ["git", "--no-pager", *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_no_credential_value_in_any_git_tracked_file(tmp_path: Path):
    """After debug and normal runs with sentinel credentials exported, no
    credential value appears in any git-tracked file (git grep -F, exit 1
    = no match)."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_docker_stub(stub_dir)

    sentinels = {
        name: f"sentinel-{name.lower()}-{uuid.uuid4().hex}"
        for name in CREDENTIAL_VARS
    }

    # Debug run: exercises command-log writing and trace output paths.
    debug_result = run_chain(
        sandbox, stub_dir, args=["--debug"], extra_env=sentinels
    )
    assert debug_result.returncode == 0, debug_result.stderr

    # Normal run: exercises the default (non-debug) launch path.
    normal_result = run_chain(sandbox, stub_dir, args=[], extra_env=sentinels)
    assert normal_result.returncode == 0, normal_result.stderr

    # No tracked file contains any sentinel value. git grep exit codes:
    # 0 = match found, 1 = no match, >=2 = error (show stderr).
    for name, sentinel in sentinels.items():
        grep = _git("grep", "--fixed-strings", "--quiet", sentinel)
        assert grep.returncode == 1, (
            f"credential value for {name} leaked into a git-tracked file "
            f"(grep exit {grep.returncode}): {grep.stderr or grep.stdout}"
        )


def command_log_path(result: subprocess.CompletedProcess) -> Path:
    """Extract the per-session command log path announced in debug mode."""
    prefix = "Command log: "
    for line in result.stderr.splitlines():
        if line.startswith(prefix):
            return Path(line[len(prefix):])
    raise AssertionError("Command log path not announced in debug output")


def test_traces_and_logs_never_reveal_secret_values(tmp_path: Path):
    """With sentinel credentials exported, the variable NAME appears in the
    debug trace, the command log, and the surfaced recent-entries block —
    proving those mechanisms ran — while the sentinel VALUE appears in none
    of the three channels."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_docker_stub(stub_dir)

    sentinels = {
        name: f"sentinel-{name.lower()}-{uuid.uuid4().hex}"
        for name in CREDENTIAL_VARS
    }
    values = list(sentinels.values())

    # Channel (a)+(b): successful debug run — trace lines on stderr, and
    # the command log file announced by the launcher.
    ok = run_chain(sandbox, stub_dir, args=["--debug"], extra_env=sentinels)
    assert ok.returncode == 0, ok.stderr

    # Channel (a): stderr trace. NAME visible, value never.
    traces = [l for l in ok.stderr.splitlines() if l.startswith("+ docker")]
    assert traces, "no debug trace lines found"
    assert any("-e OPENAI_API_KEY" in l for l in traces), traces[-1]
    for sentinel in values:
        assert sentinel not in ok.stderr

    # Channel (b): the command log file. Same guarantee.
    command_log = command_log_path(ok)
    log_text = command_log.read_text()
    assert "+ docker" in log_text, "command log holds no traced commands"
    assert "-e OPENAI_API_KEY" in log_text
    for sentinel in values:
        assert sentinel not in log_text

    # Channel (c): failing debug run — the failure checkpoint surfaces the
    # recent log entries; the surfaced block must stay value-free.
    fail = run_chain(
        sandbox,
        stub_dir,
        args=["--debug"],
        extra_env={**sentinels, "DOCKER_STUB_FAIL": "version"},
    )
    assert fail.returncode == 1, fail.stderr

    stderr_lines = fail.stderr.splitlines()
    header_index = stderr_lines.index("--- Recent command log entries ---")
    surfaced = [
        l for l in stderr_lines[header_index + 1:] if l.startswith("+ docker")
    ]
    assert surfaced, "failure checkpoint surfaced no recent entries"
    assert "+ docker version" in surfaced
    for sentinel in values:
        assert sentinel not in fail.stderr
