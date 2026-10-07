"""Story S6.4, Step 3: verification coverage for the legacy gate-path
migration.

Covers all three gate-path scenarios on both paths that apply the
rewrite:

- Launcher path (_ensure_commit_msg_gate, exercised through
  .agent/start.sh with the recording docker stub, the
  test_commit_msg_gate_activation.py pattern): the known-legacy
  core.hooksPath value .githooks is rewritten to .agent/githooks, any
  other pre-set value stays untouched, and an unset value enables the
  gate directly.
- Installer update path (configure_commit_gate, exercised through
  scripts/install.sh with real git end to end and the insteadOf rewrite
  to a local release repository, the test_s2_1_step4.py pattern): the
  same three scenarios, fully offline.

The gate's subject-format enforcement itself remains covered by
tests/test_commit_msg_hook.py; this module covers only the migration
behavior added in Steps 1 and 2.
"""

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INSTALLER = PROJECT_ROOT / "scripts" / "install.sh"
HOOK_PATH = ".agent/githooks/commit-msg"
LEGACY_HOOKS_PATH = ".githooks"
CURRENT_HOOKS_PATH = ".agent/githooks"

SESSION_ID = "s6-4-step3"

# Same recording docker stub as tests/test_commit_msg_gate_activation.py:
# every invocation is appended to $DOCKER_STUB_LOG as a JSON argv array and
# exits 0, so the launcher chain runs to completion without a real daemon.
DOCKER_STUB = """\
#!/usr/bin/env bash
set -euo pipefail
json="["
for arg in "$@"; do
  esc=${arg//\\\\/\\\\\\\\}
  esc=${esc//\\"/\\\\\\\"}
  json+="\\"$esc\\","
done
printf '%s\\n' "${json%,}]" >> "$DOCKER_STUB_LOG"
exit 0
"""


# ---------------------------------------------------------------------------
# Launcher path (pattern: tests/test_commit_msg_gate_activation.py)
# ---------------------------------------------------------------------------


def _git_env(sandbox: Path) -> dict[str, str]:
    """Return an env that isolates git config to the sandbox."""
    env = os.environ.copy()
    env["HOME"] = str(sandbox)
    env["GIT_CONFIG_GLOBAL"] = str(sandbox / ".gitconfig")
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    return env


def _make_git_sandbox(tmp_path: Path) -> Path:
    """Create an isolated git-repo sandbox cwd and HOME for the launcher."""
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir()
    (sandbox / ".agent").mkdir()
    subprocess.run(
        ["git", "init", "-q", str(sandbox)],
        check=True,
        capture_output=True,
        env=_git_env(sandbox),
    )
    return sandbox


def _write_commit_msg_gate(sandbox: Path) -> None:
    """Ship the gate files the launcher looks for under .agent/."""
    hook = sandbox / ".agent" / "githooks" / "commit-msg"
    hook.parent.mkdir(parents=True)
    hook.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    hook.chmod(0o755)


def _write_docker_stub(stub_dir: Path) -> Path:
    stub = stub_dir / "docker"
    stub.write_text(DOCKER_STUB)
    stub.chmod(0o755)
    return stub


def run_chain(
    sandbox: Path,
    stub_dir: Path,
    args: list[str],
) -> subprocess.CompletedProcess:
    """Run .agent/start.sh from the sandbox with the docker stub on PATH."""
    env = _git_env(sandbox)
    env["PATH"] = f"{stub_dir}{os.pathsep}{env['PATH']}"
    env["DOCKER_STUB_LOG"] = str(sandbox / "docker-stub.log")
    env["AI_ASSISTANT_SESSION_ID"] = SESSION_ID
    return subprocess.run(
        ["bash", str(PROJECT_ROOT / ".agent" / "start.sh"), *args],
        cwd=sandbox,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )


def _hooks_path(sandbox: Path) -> str | None:
    """Return the sandbox repo's core.hooksPath, or None when unset."""
    result = subprocess.run(
        ["git", "-C", str(sandbox), "config", "core.hooksPath"],
        capture_output=True,
        text=True,
        env=_git_env(sandbox),
    )
    return result.stdout.strip() if result.returncode == 0 else None


def _set_hooks_path(sandbox: Path, value: str) -> None:
    """Pre-set core.hooksPath in the sandbox repo."""
    subprocess.run(
        ["git", "-C", str(sandbox), "config", "core.hooksPath", value],
        check=True,
        capture_output=True,
        env=_git_env(sandbox),
    )


def test_launcher_migrates_legacy_hooks_path(tmp_path: Path):
    """A launch rewrites exactly the known-legacy value .githooks to
    .agent/githooks, so a pre-relocation configuration keeps a working
    gate after updating .agent/."""
    sandbox = _make_git_sandbox(tmp_path)
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_docker_stub(stub_dir)
    _write_commit_msg_gate(sandbox)
    _set_hooks_path(sandbox, LEGACY_HOOKS_PATH)

    result = run_chain(sandbox, stub_dir, args=[])
    assert result.returncode == 0, result.stderr
    assert _hooks_path(sandbox) == CURRENT_HOOKS_PATH


def test_launcher_leaves_other_preset_value_untouched(tmp_path: Path):
    """A pre-set non-legacy core.hooksPath (another hook manager) survives
    a launch unchanged: only the exact legacy value is rewritten."""
    sandbox = _make_git_sandbox(tmp_path)
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_docker_stub(stub_dir)
    _write_commit_msg_gate(sandbox)
    _set_hooks_path(sandbox, ".husky")

    result = run_chain(sandbox, stub_dir, args=[])
    assert result.returncode == 0, result.stderr
    assert _hooks_path(sandbox) == ".husky"


def test_launcher_unset_enables_gate_directly(tmp_path: Path):
    """With no core.hooksPath set the launcher enables the gate directly;
    the migration adds no extra step to the unset scenario."""
    sandbox = _make_git_sandbox(tmp_path)
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_docker_stub(stub_dir)
    _write_commit_msg_gate(sandbox)

    result = run_chain(sandbox, stub_dir, args=[])
    assert result.returncode == 0, result.stderr
    assert _hooks_path(sandbox) == CURRENT_HOOKS_PATH


# ---------------------------------------------------------------------------
# Installer update path (pattern: tests/test_s2_1_step4.py)
# ---------------------------------------------------------------------------


def _default_ref() -> str:
    """Return the pinned DEFAULT_REF from scripts/install.sh.

    The local release repository must be tagged with exactly the ref the
    installer fetches (DEFAULT_REF). Reading the pin instead of hardcoding
    it keeps this module passing across the release bump: the post-bump
    validation run sees the new pin before that tag exists on any remote.
    """
    match = re.search(
        r'^readonly DEFAULT_REF="(v\d+\.\d+\.\d+)"$',
        INSTALLER.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    if match is None:
        raise RuntimeError(
            "could not read DEFAULT_REF from scripts/install.sh"
        )
    return match.group(1)


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    """Run a real git command in repo, failing loudly on errors."""
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )


def run_installer(
    sandbox: Path,
    *args: str,
) -> subprocess.CompletedProcess:
    """Run install.sh in update mode with cwd inside the sandbox repo."""
    env = os.environ.copy()
    return subprocess.run(
        [shutil.which("bash"), str(INSTALLER), *args],
        cwd=sandbox,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture
def release_repo(tmp_path: Path) -> Path:
    """Local release repository tagged with the pinned DEFAULT_REF,
    shipping the gate inside .agent/ (mirrors tests/test_s2_1_step4.py)."""
    ref = _default_ref()
    repo = tmp_path / "release"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    (repo / ".agent").mkdir()
    (repo / ".agent" / "release.txt").write_text("release\n")
    (repo / ".agent" / "start.sh").write_text("release\n")
    hook = repo / HOOK_PATH
    hook.parent.mkdir()
    shutil.copy(PROJECT_ROOT / HOOK_PATH, hook)
    for path in (".agent/start.sh", HOOK_PATH):
        (repo / path).chmod(0o755)
    _git(repo, "add", ".agent")
    _git(repo, "commit", "-m", f"release {ref}")
    _git(repo, "tag", ref)
    return repo


@pytest.fixture
def consumer_repo(tmp_path: Path, release_repo: Path, monkeypatch) -> Path:
    """Consumer project with an existing install; GIT_CONFIG_GLOBAL
    rewrites the canonical assistant URL to the local release repo so the
    update stays fully offline."""
    repo = tmp_path / "project"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    (repo / ".agent").mkdir()
    (repo / ".agent" / "custom.txt").write_text("keep\n")
    _git(repo, "add", ".agent")
    _git(repo, "commit", "-m", "base")
    git_config = tmp_path / "gitconfig"
    git_config.write_text(
        f'[url "{release_repo}"]\n'
        "\tinsteadOf = https://github.com/daveonche/dev-orchestrator.git\n"
    )
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(git_config))
    return repo


def test_installer_migrates_legacy_gate_path(consumer_repo):
    """An update run repairs the legacy gate path without manual
    intervention: .githooks is rewritten to .agent/githooks, the migration
    is announced, and the refresh still completes as a commit."""
    _git(consumer_repo, "config", "core.hooksPath", LEGACY_HOOKS_PATH)

    result = run_installer(consumer_repo, "--yes")
    assert result.returncode == 0, result.stderr
    assert "migrated legacy gate path" in result.stdout
    assert "recorded the refresh as commit" in result.stdout

    hooks = _git(consumer_repo, "config", "--get", "core.hooksPath")
    assert hooks.stdout.strip() == CURRENT_HOOKS_PATH


def test_installer_leaves_other_preset_value_untouched(consumer_repo):
    """A pre-set non-legacy core.hooksPath survives the update unchanged,
    with the existing warning; only the exact legacy value is rewritten."""
    _git(consumer_repo, "config", "core.hooksPath", ".husky")

    result = run_installer(consumer_repo, "--yes")
    assert result.returncode == 0, result.stderr
    assert "already set to .husky" in result.stderr

    hooks = _git(consumer_repo, "config", "--get", "core.hooksPath")
    assert hooks.stdout.strip() == ".husky"


def test_installer_unset_enables_gate_directly(consumer_repo):
    """With no core.hooksPath set the update enables the gate directly;
    the migration adds no extra step to the unset scenario."""
    result = run_installer(consumer_repo, "--yes")
    assert result.returncode == 0, result.stderr

    hooks = _git(consumer_repo, "config", "--get", "core.hooksPath")
    assert hooks.stdout.strip() == CURRENT_HOOKS_PATH
