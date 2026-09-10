"""Tests for Story S1.7 Step 2: Enable prompt file creation."""

from pathlib import Path

PROMPT_DIR = Path(".agent/.aider.prompt")


def test_skill_md_exists_in_each_category():
    for category in ("code", "testing", "workflows"):
        skill_files = list((PROMPT_DIR / category).rglob("SKILL.md"))
        assert skill_files, (
            f"no SKILL.md file found under {PROMPT_DIR / category}"
        )
