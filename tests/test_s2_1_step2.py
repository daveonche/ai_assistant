"""Story S2.1, Step 2: clean-install placement of the assistant files.

Verifies that scripts/install.sh detects a project with no existing
assistant files, retrieves them from a fixed, published release reference,
places .agent/ — the single self-contained directory carrying the entry
script and the commit-msg hook — into the project root, records the entry
script's executability in the git index, and leaves no temporary
artifacts behind. Install mode never configures the commit message gate;
gate enablement is update-mode scope (configure_commit_gate).

git is stubbed first on PATH to record its invocations and emulate cloning
a release that contains the consolidated assistant directory, so the full
install path is exercised hermetically — no network and no real repository
needed.
"""

import os
import shutil
import stat
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
    cloning a release that contains the consolidated assistant directory
    (.agent/ with the entry script and the commit-msg hook inside it).

    Knobs read from the environment by the stub:
    - NO_GITHOOKS=1  the cloned release predates the commit-msg gate:
      the clone contains no .agent/githooks/ files
    - HOOKSPATH=<value>  core.hooksPath is already set to <value>
      (install mode never queries it; the knob exists to prove that)
    """
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
        '  : > "${target}/.agent/start.sh"\n'
        '  chmod +x "${target}/.agent/start.sh"\n'
        '  if [[ -z "${NO_GITHOOKS:-}" ]]; then\n'
        '    mkdir -p "${target}/.agent/githooks"\n'
        '    : > "${target}/.agent/githooks/commit-msg"\n'
        '    chmod +x "${target}/.agent/githooks/commit-msg"\n'
        "  fi\n"
        'elif [[ "${1:-}" == "config" && "${2:-}" == "--get" ]]; then\n'
        '  if [[ -n "${HOOKSPATH:-}" ]]; then\n'
        "    printf '%s\\n' \"${HOOKSPATH}\"\n"
        "  else\n"
        "    exit 1\n"
        "  fi\n"
        "fi\n"
    )
    stub.chmod(0o755)
    return stub_dir, log


def clone_args(log: Path) -> list[str]:
    """Return the clone invocation's arguments from the git stub log.

    The stub logs one argument per line and every invocation starts with
    its subcommand token, so the clone's arguments run from the 'clone'
    token up to the next invocation's subcommand. Since Step 4 the
    installer also runs update-index after placement, which must not be
    mistaken for clone arguments.
    """
    lines = log.read_text().splitlines()
    start = lines.index("clone")
    rest = lines[start + 1:]
    stop = rest.index("update-index") if "update-index" in rest else len(rest)
    return [lines[start], *rest[:stop]]


def clone_target(log: Path) -> Path:
    """Extract the clone target directory (the clone invocation's final
    argument) from the git stub log."""
    return Path(clone_args(log)[-1])


def run_installer(
    sandbox: Path,
    stub_dir: Path,
    *args: str,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    """Run install.sh as one command with cwd inside the sandbox repo.

    bash is resolved to an absolute path so restricted-PATH variants
    cannot break interpreter lookup via /usr/bin/env. extra_env sets
    additional variables for the run (the git stub's knobs) on top of
    the parent environment.
    """
    env = os.environ.copy()
    env["PATH"] = f"{stub_dir}{os.pathsep}{env.get('PATH', '')}"
    if extra_env:
        env.update(extra_env)
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


def test_retrieval_uses_pinned_ref_and_external_target(sandbox, git_stub):
    """Retrieval clones the pinned release ref to a target outside the project.

    The fixed, published reference is the pinned tag (v1.0.24) fetched as a
    shallow clone, and the clone target lives outside the project so the
    consumer's history stays clean.
    """
    stub_dir, log = git_stub

    result = run_installer(sandbox, stub_dir)
    assert result.returncode == 0, result.stderr

    args = clone_args(log)
    # fixed, published release reference: shallow clone of the pinned tag
    assert args[0] == "clone"
    assert "--branch" in args and "v1.0.24" in args
    assert "--depth" in args and "1" in args
    assert "https://github.com/daveonche/dev-orchestrator.git" in args
    # retrieval happens outside the project: project history stays clean
    target = Path(args[-1])
    assert not target.is_relative_to(sandbox)


def test_places_assistant_dir_with_entry_script_in_root(sandbox, git_stub):
    """After the run, .agent/ exists in the project root — and nothing else.

    The emulated release clone contains .agent/start.sh; placement must
    copy the directory into the project root and stage no root-level
    files.
    """
    stub_dir, _log = git_stub

    result = run_installer(sandbox, stub_dir)
    assert result.returncode == 0, result.stderr

    # the assistant directory lands in the project root
    assert (sandbox / ".agent").is_dir()
    # contents copied through from the emulated release clone
    assert (sandbox / ".agent" / "start.sh").is_file()
    # nothing else is staged: no root entry script, no root hook dir
    assert not (sandbox / "agent.sh").exists()
    assert not (sandbox / ".githooks").exists()


def test_places_commit_msg_hook_inside_assistant_dir(sandbox, git_stub):
    """The commit-msg hook travels inside .agent/; no gate configuration.

    The emulated release ships .agent/githooks/commit-msg; placement
    copies it as part of the directory (executable on disk, mirroring
    the release tree), records only the entry script in the index, and
    issues no core.hooksPath calls — gate enablement is update-mode
    scope.
    """
    stub_dir, log = git_stub

    result = run_installer(sandbox, stub_dir)
    assert result.returncode == 0, result.stderr

    # the hook landed inside the assistant directory, executable on disk
    hook = sandbox / ".agent" / "githooks" / "commit-msg"
    assert hook.is_file()
    assert hook.stat().st_mode & stat.S_IXUSR, "hook is not executable"
    # no root-level hook directory was created
    assert not (sandbox / ".githooks").exists()
    # no gate configuration: install mode never queries or sets
    # core.hooksPath
    assert "commit message gate" not in result.stdout
    assert "config" not in log.read_text().splitlines()

    # only the entry script's executability was recorded in the index
    lines = log.read_text().splitlines()
    assert lines.count("update-index") == 1
    assert ".agent/start.sh" in lines


def test_install_never_touches_hooks_path_config(sandbox, git_stub):
    """Install mode leaves an existing core.hooksPath value untouched.

    A consumer running another hook framework (for example husky) keeps
    its configuration: install mode issues no core.hooksPath calls at
    all — not even the query — while the assistant files are still
    placed.
    """
    stub_dir, log = git_stub

    result = run_installer(
        sandbox, stub_dir, extra_env={"HOOKSPATH": ".husky"}
    )
    assert result.returncode == 0, result.stderr
    assert "commit message gate" not in result.stdout
    assert "core.hooksPath" not in result.stderr
    # no configuration calls of any form: not even the --get query
    assert "config" not in log.read_text().splitlines()
    # the assistant directory is placed regardless
    assert (sandbox / ".agent" / "githooks" / "commit-msg").is_file()


def test_install_from_ref_without_hook_installs_clean(sandbox, git_stub):
    """A release predating the gate installs without touching config.

    Older pinned references ship no .agent/githooks/commit-msg; the
    installer places the assistant directory as-is and issues no git
    config calls.
    """
    stub_dir, log = git_stub

    result = run_installer(
        sandbox, stub_dir, extra_env={"NO_GITHOOKS": "1"}
    )
    assert result.returncode == 0, result.stderr
    assert "commit message gate" not in result.stdout
    assert not (sandbox / ".agent" / "githooks").exists()

    lines = log.read_text().splitlines()
    assert "config" not in lines
    assert ".githooks" not in lines


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


def test_temp_clone_removed_after_failed_install(sandbox, tmp_path):
    """The temporary retrieval location is removed after a failed install.

    A release lacking the assistant files makes placement fail; the exit
    trap must still remove the clone so no temporary artifacts remain.
    """
    stub_dir = tmp_path / "no-files-bin"
    stub_dir.mkdir()
    log = stub_dir / "git.log"
    stub = stub_dir / "git"
    stub.write_text(
        "#!/usr/bin/env bash\n"
        f"printf '%s\\n' \"$@\" >> {log}\n"
        'if [[ "${1:-}" == "rev-parse" ]]; then\n'
        "  printf 'true\\n'\n"
        'elif [[ "${1:-}" == "clone" ]]; then\n'
        '  mkdir -p "${@: -1}"\n'
        "fi\n"
    )
    stub.chmod(0o755)

    result = run_installer(sandbox, stub_dir)
    assert result.returncode != 0
    assert "does not contain the .agent files" in result.stderr

    # cleanup ran despite the failure: the recorded clone target is gone
    assert not clone_target(log).exists()
