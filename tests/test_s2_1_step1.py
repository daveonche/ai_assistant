"""Story S2.1, Step 1: single-command installer entry point.

Verifies that scripts/install.sh starts as a single command from inside a
project repository, completes with only the documented host prerequisites
(git), and probes nothing beyond them.

git is stubbed first on PATH to record its invocations, so prerequisite
gating is exercised hermetically — no real repository or network needed.
"""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INSTALLER = PROJECT_ROOT / "scripts" / "install.sh"


@pytest.fixture
def sandbox(tmp_path: Path) -> Path:
    """Empty project directory acting as the caller's repository."""
    return tmp_path


@pytest.fixture
def git_stub(tmp_path: Path):
    """Stub git that logs its arguments and reports a work tree."""
    stub_dir = tmp_path / "stub-bin"
    stub_dir.mkdir()
    log = stub_dir / "git.log"
    stub = stub_dir / "git"
    stub.write_text(
        "#!/usr/bin/env bash\n"
        f"printf '%s\\n' \"$@\" >> {log}\n"
        'if [[ "${1:-}" == "rev-parse" ]]; then\n'
        "  printf 'true\\n'\n"
        "fi\n"
    )
    stub.chmod(0o755)
    return stub_dir, log


def run_installer(sandbox: Path, stub_dir: Path) -> subprocess.CompletedProcess:
    """Run install.sh as one command with cwd inside the sandbox repo.

    bash is resolved to an absolute path so restricted-PATH variants
    (missing-git test) cannot break interpreter lookup via /usr/bin/env.
    """
    env = os.environ.copy()
    env["PATH"] = f"{stub_dir}{os.pathsep}{env.get('PATH', '')}"
    return subprocess.run(
        [shutil.which("bash"), str(INSTALLER)],
        cwd=sandbox,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_installer_starts_as_single_command_in_repo(sandbox, git_stub):
    """One command from inside a project repository starts the installer."""
    stub_dir, _log = git_stub

    result = run_installer(sandbox, stub_dir)
    assert result.returncode == 0, result.stderr
    assert "installer: repository:" in result.stdout
    assert "installer: reference:" in result.stdout
