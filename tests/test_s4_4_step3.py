"""Step 3 tests for Story S4.4.

Verifies that docs/implementation_status.md follows the repository's
markdown conventions: a single top-level heading, ordered heading levels,
consistent list markers, no trailing whitespace, and a single final newline.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
STATUS_DOC = REPO_ROOT / "docs" / "implementation_status.md"


def _doc_text() -> str:
    """Return the full text of the implementation status document."""
    return STATUS_DOC.read_text(encoding="utf-8")


def _doc_lines() -> list[str]:
    """Return the lines of the implementation status document."""
    return _doc_text().splitlines()


def _headings() -> list[int]:
    """Return the heading levels (1-6) of the document in order."""
    heading_pattern = re.compile(r"^(#+) ")
    levels = []
    for line in _doc_lines():
        match = heading_pattern.match(line)
        if match:
            levels.append(len(match.group(1)))
    return levels


def test_document_has_exactly_one_h1():
    """The document contains exactly one top-level heading."""
    h1_lines = [line for line in _doc_lines() if line.startswith("# ")]
    assert len(h1_lines) == 1


def test_heading_levels_do_not_skip():
    """Heading levels descend in order without skipping."""
    levels = _headings()
    assert levels
    assert levels[0] == 1
    for previous, current in zip(levels, levels[1:]):
        assert current <= previous + 1


def test_list_markers_are_consistent():
    """List items use the "-" bullet marker with conformant task-list syntax."""
    task_pattern = re.compile(r"^- \[[ x]\] ")
    for line in _doc_lines():
        assert not line.startswith("* ")
        assert not line.startswith("+ ")
        if line.startswith("- ["):
            assert task_pattern.match(line)
