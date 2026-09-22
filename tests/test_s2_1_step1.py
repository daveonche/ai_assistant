"""Story S2.1, Step 1: single-command installer entry point.

Verifies that scripts/install.sh starts as a single command from inside a
project repository, completes with only the documented host prerequisites
(git), and gates on nothing beyond them.

git is stubbed first on PATH to record its invocations, so prerequisite
gating is exercised hermetically — no real repository or network needed.
Since Step 2 the installer performs the full clean install, so the stub
also emulates cloning a release that contains the assistant files and the
commit-msg hook (the install therefore enables the commit message gate,
mirroring the pinned release), and the gate-only probe test runs with
--dry-run: the install path's base-system tools (mktemp, cp, chmod) are
covered by the Step 2 tests.
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
    """Stub git that logs its arguments, reports a work tree, and emulates
    cloning a release that contains the assistant files and the
    commit-msg hook (.githooks/commit-msg), mirroring the pinned release.
    Unhandled subcommands (update-index, config) fall through and exit 0,
    so placement and gate configuration succeed."""
    stub_dir = tmp_path / "stub-bin"
    stub_dir.mkdir()
    log = stub_dir / "git.log"
    stub = stub_dir / "git"
    stub.write_text(
        "#!/usr/bin/env bash\n"
        f"printf '%s\\n' \"$@\" >> {log}\n"
        'if [[ "${1:-}" == "rev-parse" ]]; then\n'
        "  printf 'true\\n'\n"
        'elif [[ "${1:-}" == "clone" ]]; then\n'
        '  target="${@: -1}"\n'
        '  mkdir -p "${target}/.agent"\n'
        '  : > "${target}/.agent/ai-assistant.sh"\n'
        '  : > "${target}/agent.sh"\n'
        '  mkdir -p "${target}/.githooks"\n'
        '  : > "${target}/.githooks/commit-msg"\n'
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


def test_piped_execution_reaches_main(sandbox, git_stub):
    """Script fed on stdin (curl | bash form) still runs main.

    When bash reads the script from a pipe, BASH_SOURCE[0] is empty; the
    entry-point guard must treat that as direct execution.
    """
    stub_dir, log = git_stub

    env = os.environ.copy()
    env["PATH"] = f"{stub_dir}{os.pathsep}{env.get('PATH', '')}"
    with INSTALLER.open("rb") as script_stdin:
        result = subprocess.run(
            [shutil.which("bash")],
            cwd=sandbox,
            env=env,
            stdin=script_stdin,
            capture_output=True,
            text=True,
            check=False,
        )

    assert result.returncode == 0, result.stderr
    assert "installer: repository:" in result.stdout
    assert "installer: reference:" in result.stdout
    # main actually ran: the prerequisite probe hit the git stub first,
    # then the install path cloned the pinned ref through the same stub
    lines = log.read_text().splitlines()
    assert lines[:2] == ["rev-parse", "--is-inside-work-tree"]
    assert lines[2] == "clone"
    assert "--branch" in lines and "v1.0.13" in lines


def test_installer_completes_with_documented_prerequisites(sandbox, git_stub):
    """With git available and inside a work tree, the installer completes.

    This is the sandbox proxy for the manual check "no missing-prerequisite
    error appears on a machine with the documented prerequisites".
    """
    stub_dir, _log = git_stub

    result = run_installer(sandbox, stub_dir)
    assert result.returncode == 0, result.stderr
    assert "installer: install complete" in result.stdout
    assert "error" not in result.stderr.lower()


def test_missing_git_fails_with_clear_error(sandbox, tmp_path):
    """Without git on PATH, the installer fails and names git as required.

    PATH is restricted to an empty stub dir: the script only needs bash
    builtins before the prerequisite check, so this proves git is the
    decisive prerequisite rather than an incidental lookup failure.
    """
    empty_bin = tmp_path / "empty-bin"
    empty_bin.mkdir()

    env = os.environ.copy()
    env["PATH"] = str(empty_bin)
    result = subprocess.run(
        [shutil.which("bash"), str(INSTALLER)],
        cwd=sandbox,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "git is required" in result.stderr


def test_outside_work_tree_fails_with_clear_error(sandbox, tmp_path):
    """Git present but outside a work tree: installer fails with guidance.

    The stub git answers rev-parse with 'false' (and fails, as real git
    does outside a repository), so the work-tree branch of the check is
    exercised rather than the missing-git branch.
    """
    stub_dir = tmp_path / "outside-bin"
    stub_dir.mkdir()
    stub = stub_dir / "git"
    stub.write_text(
        "#!/usr/bin/env bash\n"
        'if [[ "${1:-}" == "rev-parse" ]]; then\n'
        "  printf 'false\\n'\n"
        "  exit 1\n"
        "fi\n"
    )
    stub.chmod(0o755)

    env = os.environ.copy()
    env["PATH"] = f"{stub_dir}{os.pathsep}{env.get('PATH', '')}"
    result = subprocess.run(
        [shutil.which("bash"), str(INSTALLER)],
        cwd=sandbox,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "not a git work tree" in result.stderr
    assert "inside a project repository" in result.stderr


def test_prerequisite_probing_is_limited_to_git(sandbox, tmp_path):
    """Prerequisite gating probes only git — no additional gate probes.

    PATH contains nothing but the git stub, so any other command lookup in
    the gate would fail the run. --dry-run exercises exactly the gate (the
    install path's base-system tools — mktemp, cp, chmod — are covered by
    the Step 2 sandbox tests), so the log proves git was the sole probe.
    """
    stub_dir = tmp_path / "only-git-bin"
    stub_dir.mkdir()
    log = stub_dir / "git.log"
    stub = stub_dir / "git"
    stub.write_text(
        f"#!{shutil.which('bash')}\n"          # absolute shebang: env is not on PATH
        f"printf '%s\\n' \"$@\" >> {log}\n"
        'if [[ "${1:-}" == "rev-parse" ]]; then\n'
        "  printf 'true\\n'\n"
        "fi\n"
    )
    stub.chmod(0o755)

    env = os.environ.copy()
    env["PATH"] = str(stub_dir)
    result = subprocess.run(
        [shutil.which("bash"), str(INSTALLER), "--dry-run"],
        cwd=sandbox,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "installer: dry run complete" in result.stdout
    assert log.read_text().splitlines() == ["rev-parse", "--is-inside-work-tree"]
