"""Story S1.2, Step 1: single-command host entry delegation.

Verifies that the entry script (`.agent/start.sh`) delegates all lifecycle
logic to the assistant launcher (`.agent/launcher.py`) via its single
exec handoff.

The launcher is never executed: a stub `python3` is placed first on PATH to
record its invocation, so the full chain is exercised without Docker.
"""

import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def sandbox(tmp_path: Path) -> Path:
    """Isolated workspace preserving the entry-chain layout."""
    (tmp_path / ".agent").mkdir()
    shutil.copy2(
        PROJECT_ROOT / ".agent" / "start.sh",
        tmp_path / ".agent" / "start.sh",
    )
    executable = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    script = tmp_path / ".agent" / "start.sh"
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


def run_entry(sandbox: Path, stub_dir: Path) -> subprocess.CompletedProcess:
    """Run .agent/start.sh with the stub python3 first on PATH.

    The caller's cwd is deliberately unrelated to the sandbox: the chain
    must resolve its own script locations, not the caller's directory.
    """
    env = os.environ.copy()
    env["PATH"] = f"{stub_dir}{os.pathsep}{env.get('PATH', '')}"
    return subprocess.run(
        [str(sandbox / ".agent" / "start.sh")],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_start_sh_delegates_to_launcher(sandbox, python3_stub):
    """start.sh reaches the launcher through its single exec handoff."""
    stub_dir, log = python3_stub

    result = run_entry(sandbox, stub_dir)
    assert result.returncode == 0, result.stderr
    invocations = log.read_text().splitlines()
    assert invocations == [str(sandbox / ".agent" / "launcher.py")]

    # Negative control: removing the exec line must break delegation —
    # start.sh must not reach the launcher by any other means.
    script = sandbox / ".agent" / "start.sh"
    lines = [
        line
        for line in script.read_text().splitlines()
        if not line.strip().startswith("exec ")
    ]
    script.write_text("\n".join(lines) + "\n")
    run_entry(sandbox, stub_dir)
    assert len(log.read_text().splitlines()) == 1


def test_start_sh_contains_no_lifecycle_logic():
    """start.sh bootstraps the environment and execs the launcher; it
    performs no container lifecycle logic of its own."""
    source = (PROJECT_ROOT / ".agent" / "start.sh").read_text()
    tokens = {"docker", "build", "run", "image", "container"}
    for raw_line in source.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        assert not tokens & set(line.lower().split()), line
    exec_lines = [l for l in source.splitlines()
                  if l.strip().startswith("exec ")]
    assert len(exec_lines) == 1
    assert "launcher.py" in exec_lines[0]
