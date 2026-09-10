"""Tests for Story S1.7 Step 3: Enable shorthand command mapping."""

from pathlib import Path

AGENTS_MD = Path(".agent/AGENTS.md")


def test_shorthand_command_syntax_defined():
    assert AGENTS_MD.is_file(), f"{AGENTS_MD} does not exist"
    content = AGENTS_MD.read_text(encoding="utf-8")
    assert "$<category>-<promptname>" in content, (
        f"{AGENTS_MD} does not define the shorthand syntax "
        "`$<category>-<promptname>`"
    )


def test_shorthand_commands_map_to_skill_md_files():
    content = AGENTS_MD.read_text(encoding="utf-8")
    for command in ("/read-only", "/drop"):
        mapping = (
            f"{command} .agent/.aider.prompt/<category>/<promptname>/SKILL.md"
        )
        assert mapping in content, (
            f"{AGENTS_MD} does not map shorthand commands to SKILL.md files "
            f"via `{mapping}`"
        )
