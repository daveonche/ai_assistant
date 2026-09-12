"""Story S2.1, Step 4: executable entry scripts that survive
mode-insensitive environments.

Verifies that scripts/install.sh leaves both entry scripts (agent.sh and
.agent/ai-assistant.sh) runnable immediately after install or update,
records their executability explicitly in the project's git index
(update-index --chmod=+x) so it survives environments that do not
preserve file modes (core.fileMode=false), and that this source
repository itself records mode 100755 for both entry scripts.

Two layers keep the suite hermetic:
- the install path uses a git stub that emulates cloning the release and
  passes every other git call through to the real binary, so the
  update-index recording is exercised against a real index without
  network;
- the update path uses real git end to end, fully offline (git's
  insteadOf rewrite redirects the canonical assistant URL to a local
  release repository whose entry scripts were committed as 100644 with
  core.fileMode=false, simulating a mode-insensitive source environment).

"Runnable immediately" is verified as the exec bit on disk (the sandbox
proxy for actually executing the entry script, which stays a manual step).
"""

import os
import shutil
import stat
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INSTALLER = PROJECT_ROOT / "scripts" / "install.sh"
ENTRY_SCRIPTS = ("agent.sh", ".agent/ai-assistant.sh")


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    """Run a real git command in repo, failing loudly on errors."""
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )


def _recorded_modes(repo: Path, *git_args: str) -> dict[str, str]:
    """Map path -> recorded git mode ('100755'/'100644') for the entry
    scripts, from `git ls-files -s` (index) or `git ls-tree HEAD`
    (commit tree) depending on the given arguments."""
    modes: dict[str, str] = {}
    out = _git(repo, *git_args, "--", *ENTRY_SCRIPTS).stdout
    for line in out.splitlines():
        meta, path = line.split("\t", 1)
        modes[path] = meta.split()[0]
    return modes


def _index_modes(repo: Path) -> dict[str, str]:
    """Recorded modes for the entry scripts in the git index."""
    return _recorded_modes(repo, "ls-files", "-s")


def _tree_modes(repo: Path) -> dict[str, str]:
    """Recorded modes for the entry scripts in the HEAD commit tree."""
    return _recorded_modes(repo, "ls-tree", "HEAD")


def run_installer(
    sandbox: Path,
    stub_dir: Path | None,
    *args: str,
) -> subprocess.CompletedProcess:
    """Run install.sh as one command with cwd inside the sandbox repo.

    bash is resolved to an absolute path so restricted-PATH variants
    cannot break interpreter lookup via /usr/bin/env. The stub directory
    is prepended to the subprocess PATH only — never the parent
    environment.
    """
    env = os.environ.copy()
    if stub_dir is not None:
        env["PATH"] = f"{stub_dir}{os.pathsep}{env.get('PATH', '')}"
    return subprocess.run(
        [shutil.which("bash"), str(INSTALLER), *args],
        cwd=sandbox,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_source_repo_records_executable_entry_scripts():
    """Requirement 3: this repository records executability for both
    entry scripts — mode 100755 in the git index (Definition of Done
    check: `git ls-files -s` shows 100755)."""
    modes = _index_modes(PROJECT_ROOT)
    for path in ENTRY_SCRIPTS:
        assert modes.get(path) == "100755", (
            f"{path} is recorded as {modes.get(path)!r}, not 100755; "
            f"fix with: git update-index --chmod=+x {path}"
        )


@pytest.fixture
def fresh_repo(tmp_path: Path) -> Path:
    """Initialized consumer repository with no assistant files yet (the
    clean-install scenario)."""
    repo = tmp_path / "project"
    repo.mkdir()
    _git(repo, "init")
    return repo


@pytest.fixture
def clone_stub(tmp_path: Path):
    """Stub git that logs its arguments, reports a work tree, emulates
    cloning a release that contains the assistant files, and passes every
    other git call through to the real binary. The passthrough keeps the
    update-index executability recording real while retrieval stays
    hermetic; the absolute real-git path avoids recursing into the stub."""
    real_git = shutil.which("git")
    assert real_git is not None, "git is required for these tests"
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
        "else\n"
        f"  exec {real_git} \"$@\"\n"
        "fi\n"
    )
    stub.chmod(0o755)
    return stub_dir, log


def test_install_records_executable_and_immediately_runnable(
    fresh_repo, clone_stub
):
    """Requirements 1+2 on the install path: after the one-command
    install both entry scripts carry the exec bit on disk (runnable with
    no further preparation) and are recorded 100755 in the consumer's
    git index, robust to core.fileMode=false."""
    stub_dir, _log = clone_stub

    result = run_installer(fresh_repo, stub_dir)
    assert result.returncode == 0, result.stderr
    assert "installer: install complete" in result.stdout

    # runnable immediately: the exec bit is set on disk
    for path in ENTRY_SCRIPTS:
        script = fresh_repo / path
        assert script.is_file()
        mode = script.stat().st_mode
        assert mode & stat.S_IXUSR, f"{path} is not executable on disk"

    # recorded explicitly: 100755 in the index, so the consumer's next
    # commit preserves executability on any filesystem
    assert _index_modes(fresh_repo) == {
        "agent.sh": "100755",
        ".agent/ai-assistant.sh": "100755",
    }


@pytest.fixture
def release_repo(tmp_path: Path) -> Path:
    """Local release repository tagged v1.0.3 whose entry scripts were
    committed as 100644 under core.fileMode=false, simulating a
    mode-insensitive source environment."""
    repo = tmp_path / "release"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    # mode-insensitive source: the on-disk exec bit is ignored on add
    _git(repo, "config", "core.fileMode", "false")
    (repo / ".agent").mkdir()
    (repo / ".agent" / "release.txt").write_text("release\n")
    (repo / ".agent" / "ai-assistant.sh").write_text("release\n")
    (repo / "agent.sh").write_text("release\n")
    for path in ENTRY_SCRIPTS:
        (repo / path).chmod(0o755)  # exec bit on disk, but ...
    _git(repo, "add", ".agent", "agent.sh")
    _git(repo, "commit", "-m", "release v1.0.3")
    _git(repo, "tag", "v1.0.3")
    # ... the source records 100644, as on a mode-insensitive filesystem
    assert set(_index_modes(repo).values()) == {"100644"}
    return repo


@pytest.fixture
def consumer_repo(tmp_path: Path, release_repo: Path, monkeypatch) -> Path:
    """Consumer project with an existing install and no assistant remote
    yet; GIT_CONFIG_GLOBAL rewrites the canonical assistant URL to the
    local release repo, keeping the update fully offline while the
    installer records the canonical remote URL."""
    repo = tmp_path / "project"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    (repo / "agent.sh").write_text("local\n")
    (repo / ".agent").mkdir()
    (repo / ".agent" / "custom.txt").write_text("keep\n")
    _git(repo, "add", ".agent", "agent.sh")
    _git(repo, "commit", "-m", "base")
    # redirect the canonical assistant URL to the local release repo so
    # the installer's fetch never touches the network
    git_config = tmp_path / "gitconfig"
    git_config.write_text(
        f'[url "{release_repo}"]\n'
        "\tinsteadOf = https://github.com/daveonche/ai_assistant.git\n"
    )
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(git_config))
    return repo


def test_update_records_executable_surviving_mode_insensitive_source(
    consumer_repo,
):
    """Requirements 1+2 on the update path: refreshing from a source that
    records 100644 (mode-insensitive environment) still leaves both entry
    scripts executable on disk immediately and records 100755 for them in
    the consumer's index and in the update commit's tree, so
    executability survives any future filemode-blind checkout."""
    result = run_installer(consumer_repo, None, "--yes")
    assert result.returncode == 0, result.stderr
    assert "recorded the refresh as commit" in result.stdout

    # runnable immediately after the update: exec bits on disk
    for path in ENTRY_SCRIPTS:
        mode = (consumer_repo / path).stat().st_mode
        assert mode & stat.S_IXUSR, (
            f"{path} is not executable on disk after the update"
        )

    # recorded explicitly: 100755 in the index and in the update commit
    expected = {"agent.sh": "100755", ".agent/ai-assistant.sh": "100755"}
    assert _index_modes(consumer_repo) == expected
    assert _tree_modes(consumer_repo) == expected
