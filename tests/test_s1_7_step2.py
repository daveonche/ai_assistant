"""Tests for Story S1.7 Step 2: Enable prompt file creation."""

from pathlib import Path

PROMPT_DIR = Path(".agent/.aider.prompt")


def test_skill_md_exists_in_each_category():
    for category in ("code", "testing", "workflows"):
        skill_files = list((PROMPT_DIR / category).rglob("SKILL.md"))
        assert skill_files, (
            f"no SKILL.md file found under {PROMPT_DIR / category}"
        )


def test_skill_md_files_define_prompt_instructions():
    skill_files = sorted(PROMPT_DIR.rglob("SKILL.md"))
    assert skill_files, (
        f"no SKILL.md files found under {PROMPT_DIR}"
    )
    for skill_file in skill_files:
        content = skill_file.read_text(encoding="utf-8")
        assert content.strip(), f"{skill_file} is empty"
        assert any(line.startswith("#") for line in content.splitlines()), (
            f"{skill_file} contains no markdown heading structure"
        )
