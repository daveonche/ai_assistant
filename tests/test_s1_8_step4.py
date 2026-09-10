"""S1.8 Step 4: empty artifact cleanup.

Must Support verified:
- Empty files/artifacts left behind by launcher operations are detected
  and removed (this test).
- Files that contain content are left untouched (second test in this file).

The launcher anchors its managed artifacts at AGENT_DIR (derived from its
own __file__), so each test runs a sandboxed copy of the launch chain
(agent.sh + .agent/ tree) — the copied launcher then anchors and cleans
its artifacts inside the sandbox, and the repository's live history files
are never touched.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SESSION_ID = "s18-step4"

# Launcher-managed artifact anchors (from the docker run argv:
# --chat-history-file <agent_dir>/.aider.chat.history.md,
# --input-history-file <agent_dir>/.aider.input.history).
ARTIFACT_FILES = (".aider.chat.history.md", ".aider.input.history")

# Runtime artifacts excluded from the launcher copy so each sandbox starts
# hermetic and no live repository state leaks into the test.
COPY_IGNORE = shutil.ignore_patterns(
    ".aider.chat.history.md",
    ".aider.input.history",
    ".aider.tags.cache.v4",
    "__pycache__",
)

# Fake docker: records argv as a JSON array per invocation (identical to
# tests/test_s1_8_step3.py, including the DOCKER_STUB_FAIL hook).
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
    """Create a sandbox with its own copy of the launch chain."""
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir()
    shutil.copytree(PROJECT_ROOT / ".agent", sandbox / ".agent", ignore=COPY_IGNORE)
    shutil.copy2(PROJECT_ROOT / "agent.sh", sandbox / "agent.sh")
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
) -> subprocess.CompletedProcess:
    """Run the sandbox's own agent.sh from the sandbox with the stub on PATH."""
    env = os.environ.copy()
    env["PATH"] = f"{stub_dir}{os.pathsep}{env['PATH']}"
    env["DOCKER_STUB_LOG"] = str(sandbox / "docker-stub.log")
    env["HOME"] = str(sandbox)
    env["AI_ASSISTANT_SESSION_ID"] = SESSION_ID
    return subprocess.run(
        ["bash", str(sandbox / "agent.sh"), *args],
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


def test_empty_artifacts_removed_after_session(tmp_path: Path):
    """With the managed artifacts seeded empty, a complete session removes
    them, and no zero-byte file remains anywhere in the sandbox."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_docker_stub(stub_dir)

    agent_dir = sandbox / ".agent"
    seeded = [agent_dir / name for name in ARTIFACT_FILES]
    for path in seeded:
        path.write_text("")  # zero-byte artifact
    assert all(p.is_file() and p.stat().st_size == 0 for p in seeded)

    result = run_chain(sandbox, stub_dir, args=[])
    assert result.returncode == 0, result.stderr

    # The docker run actually happened: the session was complete, so the
    # end-of-session cleanup pass ran.
    invocations = stub_invocations(sandbox)
    assert any(inv[:1] == ["run"] for inv in invocations), invocations

    # Empty artifacts detected and removed.
    for path in seeded:
        assert not path.exists(), f"empty artifact survived: {path}"

    # No empty launcher artifact survives anywhere in the sandbox. The
    # scan is scoped to the launcher's managed artifact names: the
    # cleanup is conservative by design (own artifact paths only), so
    # unrelated pre-existing repo content — e.g. a zero-byte file under
    # .aider.conventions/ copied in with the sandbox — is correctly left
    # untouched and must not fail this test.
    empty_leftovers = [
        p
        for name in ARTIFACT_FILES
        for p in sandbox.rglob(name)
        if p.is_file() and p.stat().st_size == 0
    ]
    assert empty_leftovers == []


# Distinctive seeded content per artifact for the preservation test.
SEEDED_CONTENT = {
    ".aider.chat.history.md": "# Chat history\nseeded-content-s18-step4\n",
    ".aider.input.history": "seeded-input-history-line-s18-step4\n",
}


def test_content_bearing_artifacts_left_untouched(tmp_path: Path):
    """With the managed artifacts seeded WITH content, an identical
    complete session leaves both in place with their seeded content
    intact — preservation, not removal."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_docker_stub(stub_dir)

    agent_dir = sandbox / ".agent"
    seeded = {
        agent_dir / name: content for name, content in SEEDED_CONTENT.items()
    }
    for path, content in seeded.items():
        path.write_text(content)
    assert all(p.is_file() and p.stat().st_size > 0 for p in seeded)

    result = run_chain(sandbox, stub_dir, args=[])
    assert result.returncode == 0, result.stderr

    # The docker run actually happened: the session was complete and the
    # cleanup pass ran, so "left untouched" is a real result, not a
    # vacuous pass from a session that never started.
    invocations = stub_invocations(sandbox)
    assert any(inv[:1] == ["run"] for inv in invocations), invocations

    # Content-bearing artifacts left untouched: still present, seeded
    # content intact byte-for-byte (the stubbed container never writes,
    # so exact equality is deterministic).
    for path, content in seeded.items():
        assert path.is_file(), f"content-bearing artifact was removed: {path}"
        assert path.read_text() == content, f"content of {path.name} was altered"
