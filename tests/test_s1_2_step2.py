"""Story S1.2, Step 2: argument and debug-flag forwarding.

Verifies that the entry chain (`.agent/start.sh` → `python3`) forwards the
debug flag and every assistant argument to the launcher unchanged, in
order, without consuming, reordering, or dropping anything.

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


def run_entry(
    sandbox: Path, stub_dir: Path, args: list[str]
) -> subprocess.CompletedProcess:
    """Run .agent/start.sh with extra arguments, stub python3 first on
    PATH.

    The caller's cwd is deliberately unrelated to the sandbox: the chain
    must resolve its own script locations, not the caller's directory.
    """
    env = os.environ.copy()
    env["PATH"] = f"{stub_dir}{os.pathsep}{env.get('PATH', '')}"
    return subprocess.run(
        [str(sandbox / ".agent" / "start.sh"), *args],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_start_sh_forwards_debug_flag_to_launcher(sandbox, python3_stub):
    """--debug must reach the launcher right after its path, in position."""
    stub_dir, log = python3_stub

    result = run_entry(sandbox, stub_dir, ["--debug"])

    assert result.returncode == 0, result.stderr
    invocations = log.read_text().splitlines()
    assert invocations == [
        str(sandbox / ".agent" / "launcher.py"),
        "--debug",
    ]


def test_start_sh_forwards_all_arguments_unchanged_in_order(
    sandbox, python3_stub
):
    """The entry chain must deliver the full argv to the launcher intact.

    Exact list equality proves unchanged content, original order, and no
    consumption, reordering, dropping, or word-splitting by the chain.
    """
    stub_dir, log = python3_stub

    args = [
        "--debug",
        "--model",
        "gpt-4",
        "--message",
        "hello world",
        "--no-auto-commits",
    ]
    result = run_entry(sandbox, stub_dir, args)

    assert result.returncode == 0, result.stderr
    invocations = log.read_text().splitlines()
    assert invocations == [
        str(sandbox / ".agent" / "launcher.py"),
        *args,
    ]
