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
    return " ".join(text.replace("`", "").split()).lower()


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


def test_matching_framework_recommends_inline_read_only():
    """Must Support: when the detected framework matches an available
    conventions file, the assistant recommends loading that file via the
    /read-only command, outputting the command inline rather than
    executing it itself."""
    section = _normalized(_framework_conventions_bullets())
    assert "when the detected framework matches a framework-named file" in section
    assert "output the matching /read-only command inline" in section
    assert "per critical rules" in section
    assert "wait for the user to add it" in section


def test_version_specific_reference_recommended_when_identifiable():
    """Must Support: when the matched framework conventions file
    references version-specific conventions under the conventions
    reference directory and the project's framework version is
    identifiable, the assistant also recommends loading the matching
    version-specific reference."""
    section = _normalized(_framework_conventions_bullets())
    assert "points at version-specific conventions under" in section
    assert ".agent/.aider.conventions/references/<framework>/<version>/" in section
    assert "the detected version is identifiable" in section
    assert "a matching directory exists" in section
    assert "recommend loading that reference too" in section
