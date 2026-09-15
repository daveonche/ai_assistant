"""Step 2 tests for Story S3.3.

Verifies the release-tooling references in the pin-philosophy
documentation (docs/tech_stack.md): each test maps to one Step 2
Must Support item. The Sprint 3 record (Step 1) and convention
conformance (Step 3) are covered by their own suites, not here.
"""

from pathlib import Path

DOC = Path("docs/tech_stack.md")
PIN_PHILOSOPHY_HEADING = "## Version Lock Rationale"


def _doc_text() -> str:
    return DOC.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    """Return text from `heading` up to the next same-level heading."""
    start = text.index(heading)
    nxt = text.find("\n## ", start + len(heading))
    return text[start:nxt if nxt != -1 else len(text)]


def _pin_philosophy() -> str:
    return _section(_doc_text(), PIN_PHILOSOPHY_HEADING)


def test_release_tooling_script_referenced_in_pin_philosophy():
    """Must Support 1: the release tooling script is referenced where
    the version-pinning philosophy is described."""
    section = _pin_philosophy()
    assert "scripts/release.sh" in section, (
        "the pin-philosophy section does not reference "
        "scripts/release.sh as the repeatable release entry point"
    )
