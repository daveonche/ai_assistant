"""Story S2.1, Step 2: clean-install placement of the assistant files.

Verifies that scripts/install.sh detects a project with no existing
assistant files, retrieves them from a fixed, published release reference,
places .agent/ and agent.sh into the project root, and leaves no temporary
artifacts behind.

git is stubbed first on PATH to record its invocations and emulate cloning
a release that contains the assistant files, so the full install path is
exercised hermetically — no network and no real repository needed.
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
    cloning a release that contains the assistant files."""
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
        "fi\n"
    )
    stub.chmod(0o755)
    return stub_dir, log


def clone_args(log: Path) -> list[str]:
    """Return the clone invocation's arguments from the git stub log.

    The stub logs one argument per line, and clone is the last git call
    the installer makes, so everything from the 'clone' token onward is
    that invocation's argument list.
    """
    lines = log.read_text().splitlines()
    return lines[lines.index("clone"):]


def clone_target(log: Path) -> Path:
    """Extract the clone target directory (the clone invocation's final
    argument) from the git stub log."""
    return Path(clone_args(log)[-1])


def run_installer(
    sandbox: Path, stub_dir: Path, *args: str
) -> subprocess.CompletedProcess:
    """Run install.sh as one command with cwd inside the sandbox repo.

    bash is resolved to an absolute path so restricted-PATH variants
    cannot break interpreter lookup via /usr/bin/env.
    """
    env = os.environ.copy()
    env["PATH"] = f"{stub_dir}{os.pathsep}{env.get('PATH', '')}"
    return subprocess.run(
        [shutil.which("bash"), str(INSTALLER), *args],
        cwd=sandbox,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_clean_sandbox_install_proceeds(sandbox, git_stub):
    """A project with no existing assistant files lets the install proceed."""
    stub_dir, _log = git_stub

    result = run_installer(sandbox, stub_dir)
    assert result.returncode == 0, result.stderr
    assert "existing assistant files" not in result.stderr
    assert "installer: install complete" in result.stdout


def test_existing_agent_dir_fails_with_clear_error(sandbox, git_stub):
    """A pre-existing .agent/ is detected and the install is refused.

    The existing files must be left untouched (the update path is Step 3),
    and no retrieval may run before the detection gate.
    """
    stub_dir, log = git_stub

    (sandbox / ".agent").mkdir()
    marker = sandbox / ".agent" / "keep"
    marker.write_text("local\n")

    result = run_installer(sandbox, stub_dir)
    assert result.returncode != 0
    assert "existing assistant files" in result.stderr
    assert "updating an existing install is not supported yet" in result.stderr
    assert marker.read_text() == "local\n"
    assert "clone" not in log.read_text()


def test_existing_agent_sh_fails_with_clear_error(sandbox, git_stub):
    """A pre-existing agent.sh alone is also detected and refused.

    The detection gate must cover both assistant entry points, not just
    the .agent/ directory; the existing file stays untouched and no
    retrieval runs before the gate.
    """
    stub_dir, log = git_stub

    local_script = "#!/usr/bin/env bash\n# local\n"
    (sandbox / "agent.sh").write_text(local_script)

    result = run_installer(sandbox, stub_dir)
    assert result.returncode != 0
    assert "existing assistant files" in result.stderr
    assert "updating an existing install is not supported yet" in result.stderr
    assert (sandbox / "agent.sh").read_text() == local_script
    assert "clone" not in log.read_text()


def test_retrieval_uses_pinned_ref_and_external_target(sandbox, git_stub):
    """Retrieval clones the pinned release ref to a target outside the project.

    The fixed, published reference is the pinned tag (v1.0.0) fetched as a
    shallow clone, and the clone target lives outside the project so the
    consumer's history stays clean.
    """
    stub_dir, log = git_stub

    result = run_installer(sandbox, stub_dir)
    assert result.returncode == 0, result.stderr

    args = clone_args(log)
    # fixed, published release reference: shallow clone of the pinned tag
    assert args[0] == "clone"
    assert "--branch" in args and "v1.0.0" in args
    assert "--depth" in args and "1" in args
    assert "https://github.com/daveonche/ai_assistant.git" in args
    # retrieval happens outside the project: project history stays clean
    target = Path(args[-1])
    assert not target.is_relative_to(sandbox)


def test_places_assistant_dir_and_entry_script_in_root(sandbox, git_stub):
    """After the run, .agent/ and agent.sh exist in the project root.

    The emulated release clone contains .agent/ai-assistant.sh and
    agent.sh; placement must copy both into the project root.
    """
    stub_dir, _log = git_stub

    result = run_installer(sandbox, stub_dir)
    assert result.returncode == 0, result.stderr

    # the assistant directory and entry script land in the project root
    assert (sandbox / ".agent").is_dir()
    assert (sandbox / "agent.sh").is_file()
    # contents copied through from the emulated release clone
    assert (sandbox / ".agent" / "ai-assistant.sh").is_file()


def test_temp_clone_removed_after_successful_install(sandbox, git_stub):
    """The temporary retrieval location is removed after a successful install.

    The stub records where the installer cloned the release; after
    completion that directory must no longer exist.
    """
    stub_dir, log = git_stub

    result = run_installer(sandbox, stub_dir)
    assert result.returncode == 0, result.stderr

    # the retrieval location recorded by the stub is gone after completion
    assert not clone_target(log).exists()
