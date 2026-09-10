"""Tests for Story S1.7 Step 4: Enable context management rules in AGENT.md."""

from pathlib import Path

AGENTS_MD = Path(".agent/AGENTS.md")


def _section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines) if line.strip() == heading)
    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i].startswith("#")),
        len(lines),
    )
    return "\n".join(lines[start:end])


def test_context_management_instructions_defined():
    assert AGENTS_MD.is_file(), f"{AGENTS_MD} does not exist"
    content = AGENTS_MD.read_text(encoding="utf-8")
    section = _section(content, "## Context Window Management")
    assert "load prompt files on demand" in section, (
        f"{AGENTS_MD} 'Context Window Management' section does not instruct "
        "loading prompt files on demand"
    )
    assert "output the corresponding command" in section, (
        f"{AGENTS_MD} 'Context Window Management' section does not instruct "
        "outputting the corresponding command"
    )


def test_read_only_and_drop_usage_specified():
    content = AGENTS_MD.read_text(encoding="utf-8")
    section = _section(content, "## Critical Rules")
    for command in ("/read-only", "/drop"):
        assert f"`{command}`" in section, (
            f"{AGENTS_MD} Critical Rules do not mention `{command}`"
        )
    assert "output the command inline as part of the sentence" in section, (
        f"{AGENTS_MD} Critical Rules do not specify outputting the command "
        "inline for the user to run"
    )
    assert "Do not execute these commands yourself" in section, (
        f"{AGENTS_MD} Critical Rules do not prohibit executing the commands"
    )
    assert "embed the exact command in the sentence" in section, (
        f"{AGENTS_MD} Critical Rules do not require embedding the exact "
        "command in the sentence"
    )
