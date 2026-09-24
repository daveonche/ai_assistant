"""Commit-msg hook body scan: reject SEARCH/REPLACE edit blocks.

Must Support verified:
- A capability to reject commit messages that embed an aider
  SEARCH/REPLACE edit block, regardless of the subject line.

The subject-format enforcement is covered by tests/test_commit_msg_hook.py;
this module covers only the edit-block body scan in .githooks/commit-msg.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
HOOK = PROJECT_ROOT / ".githooks" / "commit-msg"


def run_hook(message: str, tmp_path: Path) -> subprocess.CompletedProcess:
    """Write the message to a temp file and run the hook on it."""
    message_file = tmp_path / "COMMIT_EDITMSG"
    message_file.write_text(message, encoding="utf-8")
    return subprocess.run(
        ["bash", str(HOOK), str(message_file)],
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_rejects_search_replace_block_in_body(tmp_path: Path):
    """A conforming subject with an edit block in the body is rejected:
    the LLM misfire that produced such commits must fail the hook."""
    message = (
        "docs(status): record gate work\n"
        "\n"
        "<<<<<<< SEARCH\n"
        "old text\n"
        "=======\n"
        "new text\n"
        ">>>>>>> REPLACE\n"
    )
    result = run_hook(message, tmp_path)
    assert result.returncode == 1
    assert "SEARCH/REPLACE" in result.stderr


def test_rejects_block_even_for_exempt_subject(tmp_path: Path):
    """The body scan runs before the git-generated-subject exemption, so
    an exempt subject cannot smuggle an edit block through."""
    message = 'Revert "docs(status): record gate work"\n\n>>>>>>> REPLACE\n'
    result = run_hook(message, tmp_path)
    assert result.returncode == 1
    assert "SEARCH/REPLACE" in result.stderr


def test_accepts_prose_body(tmp_path: Path):
    """A plain prose body passes both the subject check and the scan."""
    message = (
        "docs(status): record gate work\n"
        "\n"
        "Records the commit-msg gate auto-activation work with commit\n"
        "hashes and the verifying test module.\n"
    )
    result = run_hook(message, tmp_path)
    assert result.returncode == 0, result.stderr


def test_accepts_lone_equals_separator_line(tmp_path: Path):
    """A lone '=======' line is a common text separator and must not
    trip the scan: only the SEARCH/REPLACE anchors are matched."""
    message = "docs(status): record gate work\n\nBefore\n=======\nAfter\n"
    result = run_hook(message, tmp_path)
    assert result.returncode == 0, result.stderr
