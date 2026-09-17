"""Tests for Story S4.2 Step 3: framework-agnostic conventions recommendation."""

from pathlib import Path

AGENTS_MD = Path(".agent", "AGENTS.md")
FRAMEWORK_CONVENTIONS_HEADING = "Framework conventions:"


def _framework_conventions_bullets() -> str:
    """Return the 'Framework conventions:' bullet block of
    .agent/AGENTS.md, up to the next '## ' heading."""
    lines = AGENTS_MD.read_text(encoding="utf-8").splitlines()
    start = lines.index(FRAMEWORK_CONVENTIONS_HEADING) + 1
    body: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        body.append(line)
    return "\n".join(body)


def _normalized(text: str) -> str:
    """Whitespace-collapsed, lowercased text for phrase assertions."""
    return " ".join(text.split()).lower()


def test_framework_conventions_discovered_by_scanning():
    """Must Support: the assistant discovers available framework
    conventions by scanning the framework-named files in
    .agent/.aider.conventions/, rather than relying on a fixed
    framework-to-file mapping, so adding a new framework requires only
    adding its conventions file."""
    section = _normalized(_framework_conventions_bullets())
    assert "discovered by scanning the framework-named files" in section
    assert ".agent/.aider.conventions/" in section
    assert "adding a new framework requires only adding its conventions file" in section
    assert "never a table edit" in section
