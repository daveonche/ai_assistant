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
