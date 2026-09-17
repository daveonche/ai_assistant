"""Step 2 tests for Story S4.4.

Verifies that the Priority Order section of docs/implementation_status.md
reflects the new backlog state: no completed Sprint 4 feature story remains
listed as pending work, the remaining-work summary names only the S4.4
record-keeping story as outstanding, and the status narrative matches the
recorded completions.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
STATUS_DOC = REPO_ROOT / "docs" / "implementation_status.md"

PRIORITY_HEADING = "## Priority Order for Next Implementation Phase"


def _doc_text() -> str:
    """Return the full text of the implementation status document."""
    return STATUS_DOC.read_text(encoding="utf-8")


def _priority_text() -> str:
    """Return the Priority Order section of the implementation status document."""
    text = _doc_text()
    start = text.index(PRIORITY_HEADING)
    return text[start:]


def _narrative_text() -> str:
    """Return the narrative paragraph of the Priority Order section."""
    priority = _priority_text()
    start = priority.index(PRIORITY_HEADING) + len(PRIORITY_HEADING)
    end = priority.index("Priority 1 -", start)
    return priority[start:end]


def test_no_s43_pending_bullet_in_priority_order():
    """The Priority Order section no longer lists S4.3 as pending work."""
    priority = _priority_text()
    pending_bullets = [
        line for line in priority.splitlines() if line.startswith("- S4.3:")
    ]
    assert not pending_bullets


def test_feature_closure_priority_block_absent():
    """The removed Sprint 4 feature-closure priority block does not reappear."""
    priority = _priority_text()
    block_lines = [
        line for line in priority.splitlines() if "Sprint 4 feature closure" in line
    ]
    assert not block_lines


def test_only_s44_pending_bullet_remains():
    """The remaining-work summary names only the S4.4 record-keeping story."""
    priority = _priority_text()
    bullet_pattern = re.compile(r"^- S\d\.\d:")
    pending_bullets = [
        line for line in priority.splitlines() if bullet_pattern.match(line)
    ]
    assert len(pending_bullets) == 1
    assert pending_bullets[0].startswith("- S4.4:")


def test_narrative_names_feature_stories_implemented():
    """The narrative names S4.1, S4.2, and S4.3 as implemented and verified."""
    narrative = _narrative_text()
    assert "implemented and verified" in narrative
    for story_id in ("S4.1", "S4.2", "S4.3"):
        assert story_id in narrative
