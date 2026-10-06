"""Story S1.2, Step 5: dual-mode installation support.

Verifies that the entry chain works when run from a standalone clone
of this repository, and that it keeps working after the core
configuration is copied into another project's root (resolving its own
location, not the source repository's).

README documentation of the usage modes is realigned with the
single-directory install by the documentation story (S6.3); its
verification moves there.
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
    """Standalone-clone layout: .agent/start.sh.

    Mirrors the entry-chain file a fresh clone provides; the mode is
    forced so the test does not depend on the working tree's bit state
    (executability itself is Step 3 scope).
    """
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
    root: Path,
    stub_dir: Path,
    args: list[str] | None = None,
    script: Path | None = None,
    cwd: Path | None = None,
):
    """Run the entry chain with the stub python3 first on PATH.

    The launcher is never executed (stubbed), consistent with the
    Step 1–2 tests: the invocation log alone proves delegation.
    Default invocation: ./.agent/start.sh with cwd=root. Pass `script`
    (absolute path) and `cwd` to run from an unrelated directory.
    """
    env = os.environ.copy()
    env["PATH"] = f"{stub_dir}{os.pathsep}{env.get('PATH', '')}"
    command = str(script) if script is not None else "./.agent/start.sh"
    return subprocess.run(
        [command, *(args or [])],
        cwd=root if cwd is None else cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_entry_chain_works_from_standalone_clone(sandbox, python3_stub):
    """Running ./.agent/start.sh from the clone root reaches its own launcher.

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


@pytest.fixture
def target_project(tmp_path: Path) -> Path:
    """Another project's root with the single-directory copy applied.

    Mirrors the documented copy procedure: `cp -r .agent` into the
    target root, then `chmod +x` on the launcher. Copying the real
    `.agent` tree keeps the test faithful to the documented procedure.
    """
    target = tmp_path / "target-project"
    target.mkdir()
    shutil.copytree(PROJECT_ROOT / ".agent", target / ".agent")
    executable = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    script = target / ".agent" / "start.sh"
    script.chmod(script.stat().st_mode | executable)
    return target


@pytest.mark.parametrize(
    "from_target_root",
    [True, False],
    ids=["from-target-root", "from-unrelated-cwd"],
)
def test_entry_chain_works_from_copied_project_root(
    target_project, python3_stub, from_target_root
):
    """Copied-in chain reaches the target's own launcher copy.

    Maps to Step 5 Must Support: "The entry chain works after the core
    configuration is copied into another project's root." Both the
    documented invocation (./.agent/start.sh from the target root) and
    an invocation from an unrelated cwd must reach <target>/.agent/
    ai_assistant.py — paths resolve from the script's own location
    (Step 5 Developer Note), never from the caller's directory or the
    source repository.
    """
    stub_dir, log = python3_stub

    if from_target_root:
        result = run_entry(target_project, stub_dir)
    else:
        result = run_entry(
            target_project,
            stub_dir,
            script=target_project / ".agent" / "start.sh",
            cwd=PROJECT_ROOT,
        )

    assert result.returncode == 0, result.stderr
    assert log.read_text().splitlines() == [
        str(target_project / ".agent" / "ai_assistant.py")
    ]


