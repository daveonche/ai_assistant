"""Story S2.1, Step 2: clean-install placement of the assistant files.

Verifies that scripts/install.sh detects a project with no existing
assistant files, retrieves them from a fixed, published release reference,
places .agent/, agent.sh, and — when the release ships the commit-msg
hook — .githooks/ into the project root, enables the commit message gate
(core.hooksPath=.githooks) unless core.hooksPath is already set, and
leaves no temporary artifacts behind.

git is stubbed first on PATH to record its invocations and emulate cloning
a release that contains the assistant files and the commit-msg hook, so
the full install path is exercised hermetically — no network and no real
repository needed.
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
    cloning a release that contains the assistant files and the
    commit-msg hook (.githooks/commit-msg).

    Knobs read from the environment by the stub:
    - NO_GITHOOKS=1  the cloned release predates the commit-msg gate:
      the clone contains no .githooks/ files
    - HOOKSPATH=<value>  core.hooksPath is already set to <value>
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
        '  : > "${target}/.agent/ai-assistant.sh"\n'
        '  : > "${target}/agent.sh"\n'
        '  if [[ -z "${NO_GITHOOKS:-}" ]]; then\n'
        '    mkdir -p "${target}/.githooks"\n'
        '    : > "${target}/.githooks/commit-msg"\n'
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

    The fixed, published reference is the pinned tag (v1.0.12) fetched as a
    shallow clone, and the clone target lives outside the project so the
    consumer's history stays clean.
    """
    stub_dir, log = git_stub

    result = run_installer(sandbox, stub_dir)
    assert result.returncode == 0, result.stderr

    args = clone_args(log)
    # fixed, published release reference: shallow clone of the pinned tag
    assert args[0] == "clone"
    assert "--branch" in args and "v1.0.12" in args
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


def test_places_commit_msg_hook_and_enables_gate(sandbox, git_stub):
    """The install places the hook and enables the commit message gate.

    The emulated release ships .githooks/commit-msg; placement must copy
    it into the project root, leave it executable on disk, record it
    executable in the index like the entry scripts, and enable the gate
    via core.hooksPath.
    """
    stub_dir, log = git_stub

    result = run_installer(sandbox, stub_dir)
    assert result.returncode == 0, result.stderr

    # the hook landed in the project root, executable on disk
    hook = sandbox / ".githooks" / "commit-msg"
    assert hook.is_file()
    assert hook.stat().st_mode & stat.S_IXUSR, "hook is not executable"
    assert "commit message gate enabled (core.hooksPath=.githooks)" in (
        result.stdout
    )

    # the hook's executability was recorded in the index (a second
    # update-index beside the entry scripts'), and the gate configuration
    # closed the run: query, then the enable
    lines = log.read_text().splitlines()
    assert lines.count("update-index") == 2
    assert ".githooks/commit-msg" in lines
    assert lines[-3:] == ["config", "core.hooksPath", ".githooks"]


def test_install_preserves_existing_hooks_path(sandbox, git_stub):
    """An existing core.hooksPath value is never clobbered on install.

    A consumer running another hook framework (for example husky) keeps
    its configuration: the installer warns and leaves the setting
    untouched, while the hook files themselves are still placed.
    """
    stub_dir, log = git_stub

    result = run_installer(
        sandbox, stub_dir, extra_env={"HOOKSPATH": ".husky"}
    )
    assert result.returncode == 0, result.stderr
    assert "commit message gate enabled" not in result.stdout
    assert "core.hooksPath is already set to .husky" in result.stderr
    assert "leaving it untouched" in result.stderr
    # the hook files are placed regardless; only the config is preserved
    assert (sandbox / ".githooks" / "commit-msg").is_file()

    # no set-form configuration: the only core.hooksPath call is --get
    lines = log.read_text().splitlines()
    assert lines.count("core.hooksPath") == 1
    assert lines[lines.index("core.hooksPath") - 1] == "--get"


def test_install_from_ref_without_hook_skips_gate(sandbox, git_stub):
    """A release predating the gate installs without touching config.

    Older pinned references ship no .githooks/commit-msg; the installer
    must place only the classic file set and issue no git config calls.
    """
    stub_dir, log = git_stub

    result = run_installer(
        sandbox, stub_dir, extra_env={"NO_GITHOOKS": "1"}
    )
    assert result.returncode == 0, result.stderr
    assert "commit message gate" not in result.stdout
    assert not (sandbox / ".githooks").exists()

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
    assert "does not contain the assistant files" in result.stderr

    # cleanup ran despite the failure: the recorded clone target is gone
    assert not clone_target(log).exists()
