"""Story S2.1, Step 3: repeatable updates through the project's own history.

Verifies that scripts/install.sh detects existing assistant files, refreshes
them through the consumer's own git (ai-assistant remote -> fetch -> preview
-> confirm -> checkout -> commit) so the change is recorded as one normal,
reviewable, revertable project commit, and warns before replacing local
customizations.

Two layers keep the suite hermetic:
- stub-git tests log the exact command sequence and emulate the update-path
  git operations (with DIFF_RC / FAIL_FETCH knobs), so routing, ordering,
  the no-op path, and the failure ordering run without network;
- real-git tests run fully offline against a local release repository
  (git's insteadOf rewrite redirects the canonical assistant URL there, so
  no network is touched) and prove the recorded commit is scoped to
  .agent/ + agent.sh and reverts cleanly, including on a repository with
  no commits yet (unborn HEAD).
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
    """Project directory acting as the caller's repository."""
    return tmp_path


@pytest.fixture
def git_stub(tmp_path: Path):
    """Stub git that logs its arguments and emulates the update-path
    operations: reports a work tree, has no assistant remote yet, succeeds
    at remote add / fetch / checkout / commit, and reports index changes
    against HEAD.

    Knobs read from the environment by the stub:
    - DIFF_RC=0  no-op probe reports no changes ("already up to date")
    - FAIL_FETCH=1  the fetch fails, aborting the update after the warning
    """
    stub_dir = tmp_path / "stub-bin"
    stub_dir.mkdir()
    log = stub_dir / "git.log"
    stub = stub_dir / "git"
    stub.write_text(
        "#!/usr/bin/env bash\n"
        f"printf '%s\\n' \"$@\" >> {log}\n"
        'case "${1:-}" in\n'
        "  rev-parse)\n"
        '    if [[ "${2:-}" == "--is-inside-work-tree" ]]; then\n'
        "      printf 'true\\n'\n"
        '    elif [[ "${2:-}" == "--short" ]]; then\n'
        "      printf 'stub4242\\n'\n"
        "    fi\n"
        "    ;;\n"
        "  diff)\n"
        "    # scope gate and no-op probe: index differs from HEAD\n"
        "    # unless DIFF_RC=0\n"
        '    exit "${DIFF_RC:-1}"\n'
        "    ;;\n"
        "  remote)\n"
        '    if [[ "${2:-}" == "get-url" ]]; then\n'
        "      # no ai-assistant remote yet: the installer adds it\n"
        "      exit 1\n"
        "    fi\n"
        "    ;;\n"
        "  fetch)\n"
        '    if [[ -n "${FAIL_FETCH:-}" ]]; then\n'
        "      exit 1\n"
        "    fi\n"
        "    ;;\n"
        "  checkout)\n"
        "    # emulate staging the release content into the worktree\n"
        "    mkdir -p .agent\n"
        "    printf 'release\\n' > .agent/ai-assistant.sh\n"
        "    printf 'release\\n' > agent.sh\n"
        "    ;;\n"
        "esac\n"
        "exit 0\n"
    )
    stub.chmod(0o755)
    return stub_dir, log


def run_installer(
    sandbox: Path,
    stub_dir: Path | None,
    *args: str,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    """Run install.sh as one command with cwd inside the sandbox repo.

    bash is resolved to an absolute path so restricted-PATH variants cannot
    break interpreter lookup via /usr/bin/env. The stub directory is
    prepended to the subprocess PATH only — never the parent environment.
    """
    env = os.environ.copy()
    if stub_dir is not None:
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


def test_dry_run_reports_update_mode_for_existing_files(sandbox, git_stub):
    """--dry-run with existing assistant files reports the update path.

    Detection is observable through the mode-aware dry-run message, and the
    log proves no update action was probed: only the prerequisite gate ran.
    """
    stub_dir, log = git_stub

    (sandbox / ".agent").mkdir()
    marker = sandbox / ".agent" / "marker"
    marker.write_text("local\n")

    result = run_installer(sandbox, stub_dir, "--dry-run")
    assert result.returncode == 0, result.stderr
    assert (
        "dry run: would update the existing .agent/ and agent.sh"
        " from ref v1.0.10" in result.stdout
    )
    assert "dry run complete; no changes were made" in result.stdout
    # nothing changed, and no update action was probed
    assert marker.read_text() == "local\n"
    assert log.read_text().splitlines() == [
        "rev-parse",
        "--is-inside-work-tree",
    ]


@pytest.mark.parametrize(
    "trigger", [".agent", "agent.sh"], ids=["agent-dir", "agent-sh"]
)
def test_existing_assistant_files_route_to_update_without_clone(
    sandbox, git_stub, trigger
):
    """Either existing entry point routes the run to the update path.

    The refresh must go through the consumer's own git: no clone may be
    issued, since a temporary clone would bypass the reviewable-commit path.
    """
    stub_dir, log = git_stub

    if trigger == "agent.sh":
        (sandbox / "agent.sh").write_text("local\n")
    else:
        (sandbox / ".agent").mkdir()

    result = run_installer(sandbox, stub_dir, "--yes")
    assert result.returncode == 0, result.stderr
    assert "updating an existing install" in result.stdout
    assert "update complete" in result.stdout
    # the refresh went through the consumer's git, never a temp clone
    assert "clone" not in log.read_text().splitlines()
    # the triggering entry point is still in place after the refresh
    assert (sandbox / trigger).exists()


def test_update_syncs_via_consumer_git_sequence(sandbox, git_stub):
    """The update syncs through the consumer's git in the documented order.

    The stub log must show the exact sequence: prerequisite probe, staged
    scope gate, assistant remote setup, shallow fetch of the pinned ref,
    the incoming-change preview (HEAD resolution probe, stat against
    HEAD..FETCH_HEAD, then the uncommitted-local-changes probe and its
    stat), checkout of .agent + agent.sh, explicit executability recording
    (update-index --chmod=+x), no-op probe, scoped commit, and the
    short-hash lookup for the progress message. --yes skips the
    confirmation prompt, which needs a terminal.
    """
    stub_dir, log = git_stub

    (sandbox / ".agent").mkdir()
    (sandbox / ".agent" / "custom.txt").write_text("keep\n")

    result = run_installer(sandbox, stub_dir, "--yes")
    assert result.returncode == 0, result.stderr

    assert log.read_text().splitlines() == [
        "rev-parse",
        "--is-inside-work-tree",
        "diff",
        "--cached",
        "--name-only",
        "remote",
        "get-url",
        "ai-assistant",
        "remote",
        "add",
        "ai-assistant",
        "https://github.com/daveonche/ai_assistant.git",
        "fetch",
        "--quiet",
        "--depth",
        "1",
        "ai-assistant",
        "v1.0.10",
        "rev-parse",
        "--verify",
        "--quiet",
        "HEAD",
        "--no-pager",
        "diff",
        "--stat",
        "HEAD",
        "FETCH_HEAD",
        "--",
        ".agent",
        "agent.sh",
        "diff",
        "--quiet",
        "--",
        ".agent",
        "agent.sh",
        "--no-pager",
        "diff",
        "--stat",
        "--",
        ".agent",
        "agent.sh",
        "checkout",
        "FETCH_HEAD",
        "--",
        ".agent",
        "agent.sh",
        "update-index",
        "--chmod=+x",
        "agent.sh",
        ".agent/ai-assistant.sh",
        "diff",
        "--cached",
        "--quiet",
        "--",
        ".agent",
        "agent.sh",
        "commit",
        "--quiet",
        "-m",
        "Update assistant files to v1.0.10",
        "--",
        ".agent",
        "agent.sh",
        "rev-parse",
        "--short",
        "HEAD",
    ]


def test_update_noop_reports_already_up_to_date(sandbox, git_stub):
    """A refresh that changes nothing reports so and records no commit.

    With the no-op probe reporting no index change (DIFF_RC=0), the
    installer must not record a spurious commit.
    """
    stub_dir, log = git_stub

    (sandbox / ".agent").mkdir()
    result = run_installer(
        sandbox, stub_dir, "--yes", extra_env={"DIFF_RC": "0"}
    )
    assert result.returncode == 0, result.stderr
    assert "already up to date at ref v1.0.10" in result.stdout
    assert "update complete" in result.stdout
    assert "commit" not in log.read_text().splitlines()


def test_overwrite_warning_precedes_update_actions_and_names_scope(
    sandbox, git_stub
):
    """The overwrite warning is emitted before any update action runs.

    The stub fails the fetch, aborting the update before checkout or
    commit; the warning must already be on STDERR and must name the
    affected configuration area.
    """
    stub_dir, log = git_stub

    (sandbox / "agent.sh").write_text("local\n")
    result = run_installer(sandbox, stub_dir, extra_env={"FAIL_FETCH": "1"})
    assert result.returncode != 0
    assert "WARNING" in result.stderr
    assert "replaces .agent/ and agent.sh" in result.stderr
    assert "read: list in .agent/.aider.conf.yml" in result.stderr
    assert "failed to retrieve the assistant ref v1.0.10" in result.stderr
    # the run died at the fetch, before any mutation: the warning was
    # emitted ahead of the update actions that followed it
    lines = log.read_text().splitlines()
    assert "fetch" in lines
    assert "checkout" not in lines
    assert "commit" not in lines


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    """Run a real git command in repo, failing loudly on errors."""
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )


@pytest.fixture
def release_repo(tmp_path: Path) -> Path:
    """Local release repository tagged v1.0.10 holding the assistant files."""
    repo = tmp_path / "release"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    (repo / ".agent").mkdir()
    (repo / ".agent" / "release.txt").write_text("release\n")
    (repo / ".agent" / "ai-assistant.sh").write_text("release\n")
    (repo / "agent.sh").write_text("release\n")
    _git(repo, "add", ".agent", "agent.sh")
    _git(repo, "commit", "-m", "release v1.0.10")
    _git(repo, "tag", "v1.0.10")
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


def test_update_records_one_scoped_revertable_commit(consumer_repo):
    """The refresh lands as one scoped, revertable commit in consumer git.

    Real git, fully offline: ensure_assistant_remote adds the canonical
    assistant remote, and git's insteadOf rewrite redirects its fetch to
    the local release repo. The update must produce exactly one commit
    touching only .agent/ and agent.sh, and reverting it must restore the
    prior state.
    """
    base = _git(consumer_repo, "rev-parse", "HEAD").stdout.strip()

    result = run_installer(consumer_repo, None, "--yes")
    assert result.returncode == 0, result.stderr
    assert "recorded the refresh as commit" in result.stdout

    # exactly one new commit on top of the base commit
    assert _git(consumer_repo, "rev-parse", "HEAD~1").stdout.strip() == base
    # scoped: only the assistant files changed
    files = set(
        _git(
            consumer_repo, "show", "--name-only", "--format=", "HEAD"
        ).stdout.splitlines()
    )
    assert files == {
        ".agent/release.txt",
        ".agent/ai-assistant.sh",
        "agent.sh",
    }
    assert (
        _git(consumer_repo, "log", "-1", "--format=%s").stdout.strip()
        == "Update assistant files to v1.0.10"
    )
    # the release content replaced the entry script; local customizations
    # outside the release tree survive until the user re-applies them
    assert (consumer_repo / "agent.sh").read_text() == "release\n"
    assert (consumer_repo / ".agent" / "custom.txt").read_text() == "keep\n"

    # revertable: reverting the update commit restores the prior state
    _git(consumer_repo, "revert", "--no-edit", "HEAD")
    assert (consumer_repo / "agent.sh").read_text() == "local\n"
    assert not (consumer_repo / ".agent" / "release.txt").exists()


@pytest.fixture
def unborn_consumer_repo(tmp_path: Path, release_repo: Path, monkeypatch) -> Path:
    """Consumer repository with the assistant files staged but no commits
    yet (unborn HEAD) — the state a clean install leaves in a fresh
    `git init`; GIT_CONFIG_GLOBAL rewrites the canonical assistant URL to
    the local release repo as in consumer_repo."""
    repo = tmp_path / "unborn-project"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    (repo / "agent.sh").write_text("local\n")
    (repo / ".agent").mkdir()
    (repo / ".agent" / "ai-assistant.sh").write_text("local\n")
    (repo / ".agent" / "custom.txt").write_text("keep\n")
    # the clean install staged the entry scripts but recorded no commit
    _git(repo, "add", "agent.sh", ".agent/ai-assistant.sh")
    git_config = tmp_path / "gitconfig-unborn"
    git_config.write_text(
        f'[url "{release_repo}"]\n'
        "\tinsteadOf = https://github.com/daveonche/ai_assistant.git\n"
    )
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(git_config))
    return repo


def test_update_on_unborn_head_records_initial_commit(unborn_consumer_repo):
    """A refresh in a repository with no commits yet completes instead of
    dying with "fatal: bad revision 'HEAD'".

    Regression test for the update path crashing when the consumer
    repository had no commits — the state right after a clean install
    into a fresh `git init` (place_files stages the entry scripts but
    records no commit). The preview diffs against the empty tree and the
    refresh is recorded as the repository's first commit.
    """
    result = run_installer(unborn_consumer_repo, None, "--yes")
    assert result.returncode == 0, result.stderr
    assert "no commits yet; all assistant files are new" in result.stdout
    assert "recorded the refresh as commit" in result.stdout

    # the refresh landed as the repository's first commit, scoped to the
    # assistant files
    count = _git(unborn_consumer_repo, "rev-list", "--count", "HEAD")
    assert count.stdout.strip() == "1"
    files = set(
        _git(
            unborn_consumer_repo, "show", "--name-only", "--format=", "HEAD"
        ).stdout.splitlines()
    )
    assert files == {
        ".agent/release.txt",
        ".agent/ai-assistant.sh",
        "agent.sh",
    }
    assert (
        _git(unborn_consumer_repo, "log", "-1", "--format=%s").stdout.strip()
        == "Update assistant files to v1.0.10"
    )
    # the untracked local customization survives the refresh untracked
    custom = unborn_consumer_repo / ".agent" / "custom.txt"
    assert custom.read_text() == "keep\n"
