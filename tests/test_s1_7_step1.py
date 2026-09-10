"""Tests for Story S1.7 Step 1: Enable prompt directory structure."""

from pathlib import Path

PROMPT_DIR = Path(".agent/.aider.prompt")


def test_prompt_directory_exists():
    assert PROMPT_DIR.is_dir(), (
        f"{PROMPT_DIR} does not exist or is not a directory"
    )
