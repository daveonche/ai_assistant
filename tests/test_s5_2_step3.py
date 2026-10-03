"""S5.2 step 3 verification: markdown conventions for the edited sections.

Documentation-conventions suite: reads docs/implementation_status.md
directly and asserts the conventions the existing document-wide suites
(test_s3_3_step3.py, test_s4_4_step3.py) do not yet cover — balanced
inline code spans and balanced backtick code fences — over the two
sections this story edited: the Sprint 5 record section and the
Priority Order section. Pattern follows tests/test_s4_3_step3.py.
"""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

STATUS_DOC = PROJECT_ROOT / "docs" / "implementation_status.md"

SECTION_HEADINGS = (
    "Sprint 5",
    "Priority Order for Next Implementation Phase",
)


def _status_text() -> str:
    """Return the implementation status document's full text."""
    return STATUS_DOC.read_text(encoding="utf-8")


def _heading_span(text: str, heading: str) -> tuple[int, int]:
    """Return the (start, end) line indices of the named section: from
    its heading line to the next heading of the same or higher level.

    Raises AssertionError when the heading is absent, so a missing
    section fails loudly instead of returning an empty slice.
    """
    lines = text.splitlines()
    start = None
    level = 0
    for index, line in enumerate(lines):
        if line.startswith("#") and line.lstrip("#").strip() == heading:
            start = index
            level = len(line) - len(line.lstrip("#"))
            break
    assert start is not None, f"heading not found: {heading!r}"
    end = len(lines)
    for index in range(start + 1, len(lines)):
        line = lines[index]
        if line.startswith("#"):
            other = len(line) - len(line.lstrip("#"))
            if other <= level:
                end = index
                break
    return start, end


def _edited_sections() -> list[tuple[str, list[str]]]:
    """The (heading, lines) pairs of the two sections this story edited."""
    text = _status_text()
    sections: list[tuple[str, list[str]]] = []
    for heading in SECTION_HEADINGS:
        start, end = _heading_span(text, heading)
        sections.append((heading, text.splitlines()[start:end]))
    return sections


def test_edited_sections_have_balanced_inline_code_spans():
    """Every line in the two edited sections carries balanced inline
    code spans — an even backtick count, the S4.3 suite's check scoped
    to the sections this story edited."""
    for heading, lines in _edited_sections():
        for offset, line in enumerate(lines):
            assert line.count("`") % 2 == 0, (
                f"{heading}: unbalanced inline code spans on line "
                f"{offset + 1}: {line!r}"
            )
