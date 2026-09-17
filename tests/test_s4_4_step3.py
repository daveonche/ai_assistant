"""Step 3 tests for Story S4.4.

Verifies that docs/implementation_status.md follows the repository's
markdown conventions: a single top-level heading, ordered heading levels,
consistent list markers, no trailing whitespace, and a single final newline.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
STATUS_DOC = REPO_ROOT / "docs" / "implementation_status.md"


def _doc_text() -> str:
    """Return the full text of the implementation status document."""
    return STATUS_DOC.read_text(encoding="utf-8")


def _doc_lines() -> list[str]:
    """Return the lines of the implementation status document."""
    return _doc_text().splitlines()


def test_document_has_exactly_one_h1():
    """The document contains exactly one top-level heading."""
    h1_lines = [line for line in _doc_lines() if line.startswith("# ")]
    assert len(h1_lines) == 1
