"""Step 1 tests for Story S3.3.

Verifies the Sprint 3 record in docs/implementation_status.md:
each test maps to one Step 1 Must Support item. The tech_stack.md
references (Step 2) and convention conformance (Step 3) are covered
by their own suites, not here.
"""

from pathlib import Path

DOC = Path("docs/implementation_status.md")


def _doc_text() -> str:
    return DOC.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    """Return text from `heading` up to the next same-level heading."""
    start = text.index(heading)
    nxt = text.find("\n## ", start + len(heading))
    return text[start:nxt if nxt != -1 else len(text)]


def test_sprint3_section_exists():
    """Must Support 1: a Sprint 3 section is present."""
    assert "## Sprint 3" in _doc_text()
