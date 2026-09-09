"""Story S1.2, Step 5: dual-mode installation support.

Verifies that the entry chain works when run from a standalone clone
of this repository, that it keeps working after the core configuration
is copied into another project's root (resolving its own location, not
the source repository's), and that the readme documents both usage
modes with the exact steps for each.
"""

import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
README = PROJECT_ROOT / "README.md"


@pytest.fixture
def sandbox(tmp_path: Path) -> Path:
    """Standalone-clone layout: agent.sh + .agent/ai-assistant.sh.

    Mirrors the entry-chain files a fresh clone provides; modes are
    forced so the test does not depend on the working tree's bit state
    (executability itself is Step 3 scope).
    """
    (tmp_path / ".agent").mkdir()
    shutil.copy2(PROJECT_ROOT / "agent.sh", tmp_path / "agent.sh")
    shutil.copy2(
        PROJECT_ROOT / ".agent" / "ai-assistant.sh",
        tmp_path / ".agent" / "ai-assistant.sh",
    )
    executable = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    for script in (
        tmp_path / "agent.sh",
        tmp_path / ".agent" / "ai-assistant.sh",
    ):
        script.chmod(script.stat().st_mode | executable)
    return tmp_path


@pytest.fixture
def python3_stub(tmp_path: Path):
    """Stub python3 that logs its arguments and exits 0."""
    stub_dir = tmp_path / "stub-bin"
    stub_dir.mkdir()
    log = stub_dir / "invocations.log"
    stub = stub_dir / "python3"
    stub.write_text(f"#!/usr/bin/env bash\nprintf '%s\\n' \"$@\" >> {log}\n")
    stub.chmod(0o755)
    return stub_dir, log


def run_entry(root: Path, stub_dir: Path, args: list[str] | None = None):
    """Run the entry chain from `root` with the stub python3 on PATH.

    The launcher is never executed (stubbed), consistent with the
    Step 1–2 tests: the invocation log alone proves delegation.
    """
    env = os.environ.copy()
    env["PATH"] = f"{stub_dir}{os.pathsep}{env.get('PATH', '')}"
    return subprocess.run(
        ["./agent.sh", *(args or [])],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_entry_chain_works_from_standalone_clone(sandbox, python3_stub):
    """Running ./agent.sh from the clone root reaches its own launcher.

    Maps to Step 5 Must Support: "The entry chain works when run from
    a standalone clone of this repository." The stub log must record
    exactly one invocation, targeting the clone's own launcher copy.
    """
    stub_dir, log = python3_stub

    result = run_entry(sandbox, stub_dir)
    assert result.returncode == 0, result.stderr
    assert log.read_text().splitlines() == [
        str(sandbox / ".agent" / "ai_assistant.py")
    ]
