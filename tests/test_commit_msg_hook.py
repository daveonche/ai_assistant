"""Behavior tests for the commit-msg gate (.githooks/commit-msg).

The assistant's commit-prompt asks for a Conventional Commits subject
(type(scope): summary, max 72 chars, plain text), yet chat prose has
repeatedly landed in history as commit subjects. The hook is the
mechanical gate: git invokes it with the message file and rejects the
commit on exit 1. Each test runs the hook directly on a temp message
file; the CI validate job runs the same script on the pushed tip
commit, so the gate also holds where core.hooksPath is not configured.
"""

from __future__ import annotations

import stat
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
HOOK = PROJECT_ROOT / ".githooks" / "commit-msg"


def run_hook(message: str, tmp_path: Path) -> subprocess.CompletedProcess:
    """Run the hook the way git does: bash <hook> <message-file>."""
    msg_file = tmp_path / "COMMIT_EDITMSG"
    msg_file.write_text(message, encoding="utf-8")
    return subprocess.run(
        ["bash", str(HOOK), str(msg_file)],
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_hook_is_executable_with_plain_shebang():
    text = HOOK.read_text(encoding="utf-8")
    assert text.startswith("#!/usr/bin/env bash\n")
    assert "set -euo pipefail" in text
    assert HOOK.stat().st_mode & stat.S_IXUSR, "hook must be executable"


@pytest.mark.parametrize(
    "subject",
    [
        "feat: add docker config sanitizer",
        "fix(agent): sanitize Docker config for in-container builds",
        "chore(release): bump pinned reference to v1.0.11",
        "test(audit): add docker config sanitizer audit tests",
        "fix(tests/s1-5-step5): update command-log path",
        "feat!: drop support for python 3.11",
        "fix(agent-socket)!: replace octal arithmetic",
        "docs(workflow-state): update Last completed hashes",
    ],
)
def test_conforming_subjects_are_accepted(tmp_path, subject):
    message = f"{subject}\n\nBody paragraph.\n# a comment line\n"
    result = run_hook(message, tmp_path)
    assert result.returncode == 0, result.stderr


def test_subject_at_the_72_char_limit_is_accepted(tmp_path):
    result = run_hook("fix: " + "x" * 67 + "\n", tmp_path)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "subject",
    [
        # Real leaked chat prose from this repository's history.
        "Let me know once the edits are applied and the verification "
        "tests have run.",
        "Applying the checkpoint edit now.",
        "Running the reproducers now:",
        # Format violations.
        "updated the launcher",
        "fix missing colon",
        "wip: half-done work",
        'feat: has "double quotes"',
        "feat: has `backticks`",
        "feat: " + "x" * 67,  # 73 chars: one over the cap
    ],
)
def test_prose_and_malformed_subjects_are_rejected(tmp_path, subject):
    result = run_hook(subject + "\n", tmp_path)
    assert result.returncode == 1
    assert result.stderr.strip(), "rejection reason must go to STDERR"


@pytest.mark.parametrize(
    "subject",
    [
        "Merge branch 'main' into feature",
        "Merge pull request #12 from daveonche/gate",
        "fixup! feat: add gate",
        "squash! feat: add gate",
        'Revert "feat: add gate"',
    ],
)
def test_git_generated_subjects_are_exempt(tmp_path, subject):
    result = run_hook(subject + "\n", tmp_path)
    assert result.returncode == 0, result.stderr


def test_empty_and_comment_only_messages_are_rejected(tmp_path):
    for message in ("", "\n", "# only a comment\n"):
        result = run_hook(message, tmp_path)
        assert result.returncode == 1, message


def test_missing_message_file_fails_closed(tmp_path):
    result = subprocess.run(
        ["bash", str(HOOK), str(tmp_path / "absent.txt")],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 1
    assert "cannot read" in result.stderr


def test_missing_argument_fails_closed():
    result = subprocess.run(
        ["bash", str(HOOK)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 1


def test_debug_flag_still_validates(tmp_path):
    msg = tmp_path / "m.txt"
    msg.write_text("feat: ok\n", encoding="utf-8")
    result = subprocess.run(
        ["bash", str(HOOK), "--debug", str(msg)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr


def test_release_bump_subject_format_is_accepted(tmp_path):
    """The release script's commit subject must pass the gate it ships."""
    result = run_hook(
        "chore(release): bump pinned reference to v9.9.9\n", tmp_path
    )
    assert result.returncode == 0, result.stderr


def test_readme_documents_hooks_path_activation():
    text = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    assert "git config core.hooksPath .githooks" in text


def test_ci_runs_the_hook_on_the_tip_commit():
    text = (
        PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
    ).read_text(encoding="utf-8")
    assert "bash .githooks/commit-msg" in text
