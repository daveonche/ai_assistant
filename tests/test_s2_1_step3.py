"""Story S2.1, Step 3: repeatable updates through the project's own history.

Verifies that scripts/install.sh detects existing assistant files, refreshes
them through the consumer's own git (ai-assistant remote -> fetch -> preview
-> confirm -> gate configuration -> checkout -> commit) so the change is
recorded as one normal, reviewable, revertable project commit, and warns
before replacing local customizations. When the fetched reference ships the
commit-msg hook (.githooks/commit-msg), the update also enables the commit
message gate (core.hooksPath=.githooks) unless core.hooksPath is already
set; a reference predating the gate skips the gate entirely.

Two layers keep the suite hermetic:
- stub-git tests log the exact command sequence and emulate the update-path
  git operations (with DIFF_RC / FAIL_FETCH knobs), so routing, ordering,
  the no-op path, and the failure ordering run without network;
- real-git tests run fully offline against a local release repository
  (git's insteadOf rewrite redirects the canonical assistant URL there, so
  no network is touched) and prove the recorded commit is scoped to the
  assistant files (.agent/, agent.sh, and .githooks/commit-msg when the
  release ships the gate) and reverts cleanly, including on a repository
  with no commits yet (unborn HEAD).
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
    against HEAD. The emulated release ships .githooks/commit-msg, so the
    installer's hook probes (cat-file) succeed and the gate is configured.

    Knobs read from the environment by the stub:
    - DIFF_RC=0  no-op probe reports no changes ("already up to date")
    - FAIL_FETCH=1  the fetch fails, aborting the update after the warning
    - NO_GITHOOKS=1  the fetched reference predates the commit-msg gate:
      the cat-file probe fails and checkout stages no .githooks/ files
    - HOOKSPATH=<value>  core.hooksPath is already set to <value>
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
        "  cat-file)\n"
        "    # hook probe: the emulated release ships the commit-msg\n"
        "    # hook unless NO_GITHOOKS=1 (an older reference)\n"
        '    if [[ "${2:-}" == "-e" ]]; then\n'
        '      if [[ -n "${NO_GITHOOKS:-}" ]]; then\n'
        "        exit 1\n"
        "      fi\n"
        "      exit 0\n"
        "    fi\n"
        "    ;;\n"
        "  config)\n"
        '    if [[ "${2:-}" == "--get" ]]; then\n'
        "      # query form: report a pre-existing hooksPath, if any\n"
        '      if [[ -n "${HOOKSPATH:-}" ]]; then\n'
        "        printf '%s\\n' \"${HOOKSPATH}\"\n"
        "        exit 0\n"
        "      fi\n"
        "      exit 1\n"
        "    fi\n"
        "    ;;\n"
        "  checkout)\n"
        "    # emulate staging the release content into the worktree\n"
        "    mkdir -p .agent\n"
        "    printf 'release\\n' > .agent/ai-assistant.sh\n"
        "    printf 'release\\n' > agent.sh\n"
        '    if [[ -z "${NO_GITHOOKS:-}" ]]; then\n'
        "      mkdir -p .githooks\n"
        "      printf 'hook\\n' > .githooks/commit-msg\n"
        "    fi\n"
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
        " from ref v1.0.15" in result.stdout
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
    the incoming-change preview (HEAD resolution probe, hook probe, stat
    against HEAD..FETCH_HEAD, then the uncommitted-local-changes probe
    and its stat), gate configuration (hooksPath query, then the enable),
    checkout of .agent + agent.sh + .githooks, explicit executability
    recording for the entry scripts and the hook (update-index
    --chmod=+x), no-op probe, scoped commit with the gate-conforming
    subject, and the short-hash lookup for the progress message. --yes
    skips the confirmation prompt, which needs a terminal.
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
        "v1.0.15",
        "rev-parse",
        "--verify",
        "--quiet",
        "HEAD",
        "cat-file",
        "-e",
        "FETCH_HEAD:.githooks/commit-msg",
        "--no-pager",
        "diff",
        "--stat",
        "HEAD",
        "FETCH_HEAD",
        "--",
        ".agent",
        "agent.sh",
        ".githooks",
        "diff",
        "--quiet",
        "--",
        ".agent",
        "agent.sh",
        ".githooks",
        "--no-pager",
        "diff",
        "--stat",
        "--",
        ".agent",
        "agent.sh",
        ".githooks",
        "cat-file",
        "-e",
        "FETCH_HEAD:.githooks/commit-msg",
        "config",
        "--get",
        "core.hooksPath",
        "config",
        "core.hooksPath",
        ".githooks",
        "cat-file",
        "-e",
        "FETCH_HEAD:.githooks/commit-msg",
        "checkout",
        "FETCH_HEAD",
        "--",
        ".agent",
        "agent.sh",
        ".githooks",
        "update-index",
        "--chmod=+x",
        "agent.sh",
        ".agent/ai-assistant.sh",
        "cat-file",
        "-e",
        "FETCH_HEAD:.githooks/commit-msg",
        "update-index",
        "--chmod=+x",
        ".githooks/commit-msg",
        "diff",
        "--cached",
        "--quiet",
        "--",
        ".agent",
        "agent.sh",
        ".githooks",
        "commit",
        "--quiet",
        "-m",
        "chore(agent): update assistant files to v1.0.15",
        "--",
        ".agent",
        "agent.sh",
        ".githooks",
        "rev-parse",
        "--short",
        "HEAD",
    ]


def test_update_enables_commit_gate_before_its_own_commit(sandbox, git_stub):
    """The gate is enabled before the refresh commit is recorded.

    The installer's own commit must pass through the gate it installs, so
    the enable must appear in the log ahead of the commit.
    """
    stub_dir, log = git_stub

    (sandbox / ".agent").mkdir()
    result = run_installer(sandbox, stub_dir, "--yes")
    assert result.returncode == 0, result.stderr
    assert "commit message gate enabled" in result.stdout
    assert "core.hooksPath=.githooks" in result.stdout

    lines = log.read_text().splitlines()
    assert lines.index("config") < lines.index("commit")


def test_update_preserves_foreign_hooks_path(sandbox, git_stub):
    """An existing core.hooksPath value is never clobbered.

    A consumer running another hook framework (for example husky) keeps
    its configuration: the installer warns and leaves the setting
    untouched, while the hook files themselves are still shipped.
    """
    stub_dir, log = git_stub

    (sandbox / ".agent").mkdir()
    result = run_installer(
        sandbox, stub_dir, "--yes", extra_env={"HOOKSPATH": ".husky"}
    )
    assert result.returncode == 0, result.stderr
    assert "commit message gate enabled" not in result.stdout
    assert "core.hooksPath is already set to .husky" in result.stderr
    assert "leaving it untouched" in result.stderr
    # the hook files ship regardless; only the configuration is preserved
    assert (sandbox / ".githooks" / "commit-msg").is_file()

    # no set-form configuration happened: the only core.hooksPath
    # invocation in the log is the --get query
    lines = log.read_text().splitlines()
    assert lines.count("core.hooksPath") == 1
    assert lines[lines.index("core.hooksPath") - 1] == "--get"


def test_update_reports_gate_already_active(sandbox, git_stub):
    """core.hooksPath already pointing at .githooks is reported, not
    reconfigured."""
    stub_dir, log = git_stub

    (sandbox / ".agent").mkdir()
    result = run_installer(
        sandbox, stub_dir, "--yes", extra_env={"HOOKSPATH": ".githooks"}
    )
    assert result.returncode == 0, result.stderr
    assert "commit message gate already active" in result.stdout
    assert "commit message gate enabled" not in result.stdout
    assert "core.hooksPath is already set" not in result.stderr

    lines = log.read_text().splitlines()
    assert lines.count("core.hooksPath") == 1


def test_update_from_ref_without_hook_skips_gate_config(sandbox, git_stub):
    """A fetched reference predating the gate triggers no configuration.

    Older pinned references ship no .githooks/commit-msg; the installer
    must not touch core.hooksPath and must keep the refresh scoped to the
    classic file set.
    """
    stub_dir, log = git_stub

    (sandbox / ".agent").mkdir()
    result = run_installer(
        sandbox, stub_dir, "--yes", extra_env={"NO_GITHOOKS": "1"}
    )
    assert result.returncode == 0, result.stderr
    assert "commit message gate" not in result.stdout

    lines = log.read_text().splitlines()
    # no gate configuration at all: not even the query
    assert "config" not in lines
    # the refresh stays scoped to .agent + agent.sh
    start = lines.index("commit")
    end = lines.index("rev-parse", start)
    assert ".githooks" not in lines[start:end]
    # and no hook files were staged into the worktree
    assert not (sandbox / ".githooks").exists()


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
    assert "already up to date at ref v1.0.15" in result.stdout
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
    assert "failed to retrieve the assistant ref v1.0.15" in result.stderr
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
    """Local release repository tagged v1.0.15 holding the assistant
    files and the real commit-msg gate, so the installer's own update
    commit and the later revert run through the actual hook."""
    repo = tmp_path / "release"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    (repo / ".agent").mkdir()
    (repo / ".agent" / "release.txt").write_text("release\n")
    (repo / ".agent" / "ai-assistant.sh").write_text("release\n")
    (repo / "agent.sh").write_text("release\n")
    hook = repo / ".githooks" / "commit-msg"
    hook.parent.mkdir()
    shutil.copy(PROJECT_ROOT / ".githooks" / "commit-msg", hook)
    hook.chmod(0o755)
    _git(repo, "add", ".agent", "agent.sh", ".githooks")
    _git(repo, "commit", "-m", "release v1.0.15")
    _git(repo, "tag", "v1.0.15")
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
    touching only .agent/, agent.sh, and .githooks/commit-msg, must leave
    the commit message gate enabled, and reverting it must restore the
    prior state — the revert itself passing the gate through the
    Revert "..." exemption.
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
        ".githooks/commit-msg",
    }
    assert (
        _git(consumer_repo, "log", "-1", "--format=%s").stdout.strip()
        == "chore(agent): update assistant files to v1.0.15"
    )
    # the gate is live in the consumer repository after the update
    hooks_path = _git(consumer_repo, "config", "--get", "core.hooksPath")
    assert hooks_path.stdout.strip() == ".githooks"
    # the release content replaced the entry script; local customizations
    # outside the release tree survive until the user re-applies them
    assert (consumer_repo / "agent.sh").read_text() == "release\n"
    assert (consumer_repo / ".agent" / "custom.txt").read_text() == "keep\n"

    # revertable: reverting the update commit restores the prior state;
    # the revert commit itself passes the gate via the Revert exemption
    _git(consumer_repo, "revert", "--no-edit", "HEAD")
    assert (consumer_repo / "agent.sh").read_text() == "local\n"
    assert not (consumer_repo / ".agent" / "release.txt").exists()
    assert not (consumer_repo / ".githooks" / "commit-msg").exists()


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
        ".githooks/commit-msg",
    }
    assert (
        _git(unborn_consumer_repo, "log", "-1", "--format=%s").stdout.strip()
        == "chore(agent): update assistant files to v1.0.15"
    )
    # the untracked local customization survives the refresh untracked
    custom = unborn_consumer_repo / ".agent" / "custom.txt"
    assert custom.read_text() == "keep\n"


@pytest.fixture
def legacy_release_repo(tmp_path: Path) -> Path:
    """Local release repository tagged v1.0.10 that predates the
    commit-msg gate: it holds the assistant files but no .githooks/."""
    repo = tmp_path / "legacy-release"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    (repo / ".agent").mkdir()
    (repo / ".agent" / "release.txt").write_text("legacy\n")
    (repo / ".agent" / "ai-assistant.sh").write_text("legacy\n")
    (repo / "agent.sh").write_text("legacy\n")
    _git(repo, "add", ".agent", "agent.sh")
    _git(repo, "commit", "-m", "release v1.0.10")
    _git(repo, "tag", "v1.0.10")
    return repo


@pytest.fixture
def legacy_consumer_repo(
    tmp_path: Path, legacy_release_repo: Path, monkeypatch
) -> Path:
    """Consumer project with an existing install whose assistant remote
    resolves to the legacy (pre-gate) release repository."""
    repo = tmp_path / "legacy-project"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    (repo / "agent.sh").write_text("local\n")
    (repo / ".agent").mkdir()
    (repo / ".agent" / "ai-assistant.sh").write_text("local\n")
    _git(repo, "add", ".agent", "agent.sh")
    _git(repo, "commit", "-m", "base")
    git_config = tmp_path / "gitconfig-legacy"
    git_config.write_text(
        f'[url "{legacy_release_repo}"]\n'
        "\tinsteadOf = https://github.com/daveonche/ai_assistant.git\n"
    )
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(git_config))
    return repo


def test_update_from_ref_without_hook_skips_gate(legacy_consumer_repo):
    """Updating from a reference that predates the gate leaves the
    repository configuration untouched.

    The legacy release ships no .githooks/commit-msg, so the installer
    must not enable core.hooksPath, must not stage .githooks/ files, and
    must still record a subject that conforms to the gate (a consumer
    with the gate already enabled stays compatible).
    """
    result = run_installer(
        legacy_consumer_repo, None, "--yes", "--ref", "v1.0.10"
    )
    assert result.returncode == 0, result.stderr
    assert "recorded the refresh as commit" in result.stdout
    assert "commit message gate" not in result.stdout

    # no gate configuration was written
    probe = subprocess.run(
        ["git", "config", "--get", "core.hooksPath"],
        cwd=legacy_consumer_repo,
        capture_output=True,
        text=True,
        check=False,
    )
    assert probe.returncode != 0  # unset
    assert probe.stdout.strip() == ""

    # the commit stays scoped to the classic file set
    files = set(
        _git(
            legacy_consumer_repo, "show", "--name-only", "--format=", "HEAD"
        ).stdout.splitlines()
    )
    assert files == {
        ".agent/release.txt",
        ".agent/ai-assistant.sh",
        "agent.sh",
    }
    assert (
        _git(legacy_consumer_repo, "log", "-1", "--format=%s").stdout.strip()
        == "chore(agent): update assistant files to v1.0.10"
    )
