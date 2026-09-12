"""Tests for S2.2 Step 4: resolved-status annotations in the sprint 1 stories."""

from pathlib import Path

STORY_FILE = Path("docs/sprints/sprint_1_stories.md")


def _story_lines() -> list[str]:
    return STORY_FILE.read_text(encoding="utf-8").splitlines()


def test_s1_2_flag_resolved():
    matches = [
        line
        for line in _story_lines()
        if "Python >=3.8 is a minimum constraint" in line
    ]
    assert matches, "S1.2 developer-note line not found"
    line = matches[0]
    assert "⚠ FLAGGED" not in line
    assert "✓ RESOLVED" in line


def test_s1_4_flag_resolved():
    matches = [
        line
        for line in _story_lines()
        if 'requires-python = ">=3.8"' in line
    ]
    assert matches, "S1.4 acceptance-criterion line not found"
    line = matches[0]
    assert "⚠ FLAGGED" not in line
    assert "✓ RESOLVED" in line


def test_resolved_annotations_reference_tech_stack():
    resolved = [line for line in _story_lines() if "✓ RESOLVED" in line]
    assert len(resolved) >= 3, (
        "expected resolved annotations for S1.2, S1.4, and S1.5"
    )
    for line in resolved:
        assert "docs/tech_stack.md" in line, (
            f"resolved annotation does not point at docs/tech_stack.md: {line}"
        )
