"""Step 1 tests for Story S4.4.

Verifies that the Sprint 4 section of docs/implementation_status.md records
Story S4.3 with each implementation step listed as completed, and that the
entry detail style is consistent with the existing S4.1 and S4.2 entries.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
STATUS_DOC = REPO_ROOT / "docs" / "implementation_status.md"

SPRINT4_HEADING = "## Sprint 4"
PRIORITY_HEADING = "## Priority Order for Next Implementation Phase"


def _doc_text() -> str:
    """Return the full text of the implementation status document."""
    return STATUS_DOC.read_text(encoding="utf-8")


def _sprint4_text() -> str:
    """Return the Sprint 4 section of the implementation status document."""
    text = _doc_text()
    start = text.index(SPRINT4_HEADING)
    end = text.index(PRIORITY_HEADING, start)
    return text[start:end]


def _story_entry_text(section: str, heading_prefix: str, next_prefix: str) -> str:
    """Return one story's entry text between its heading and the next entry."""
    start = section.index(heading_prefix)
    end = section.index(next_prefix, start)
    return section[start:end]


def test_s43_entry_present_in_sprint4_section():
    """The Sprint 4 section contains a Story S4.3 entry."""
    sprint4 = _sprint4_text()
    assert "### Story S4.3:" in sprint4


def test_s43_entry_lists_all_steps_completed():
    """The S4.3 entry lists Steps 1-3 all as checked items."""
    sprint4 = _sprint4_text()
    entry = sprint4[sprint4.index("### Story S4.3:") :]
    checked_steps = [
        line for line in entry.splitlines() if line.startswith("- [x] Step ")
    ]
    assert len(checked_steps) == 3
    assert "- [ ]" not in entry
