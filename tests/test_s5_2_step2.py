"""S5.2 step 2 verification: the Priority Order section.

Documentation-content suite: reads docs/implementation_status.md
directly and asserts the story's record requirements for the
"Priority Order for Next Implementation Phase" section — the
established pattern of the S3.3/S4.x/S5.x doc suites. No launcher
behavior is exercised here.

Covered here:
- the section states the Sprint 5 work is implemented and verified and
  names the host-side per-project configuration outcome (the trusted
  args file) as what Sprint 5 delivered;
- the section restates the post-Sprint-5 backlog state, notes the S5.2
  record-keeping story's completion, and names the next workflow step;
- every mention of root-config merging is framed as replaced or
  no-longer-current — no stale claim presents merging as active
  behavior.
"""

from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

STATUS_DOC = PROJECT_ROOT / "docs" / "implementation_status.md"

PRIORITY_ORDER_HEADING = "Priority Order for Next Implementation Phase"

# Framing that accompanies a legitimate mention of the removed merge
# behavior: it is being replaced or declared no longer current.
_MERGE_FRAMING = re.compile(r"replac(?:ed|ing)|no longer current", re.IGNORECASE)


def _status_text() -> str:
    """Return the implementation status document's full text."""
    return STATUS_DOC.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    """The text with every whitespace run collapsed to one space, so
    assertions match across the document's hard line wraps."""
    return re.sub(r"\s+", " ", text)


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


def _priority_order_section() -> str:
    """The Priority Order section's lines, joined with newlines."""
    text = _status_text()
    start, end = _heading_span(text, PRIORITY_ORDER_HEADING)
    return "\n".join(text.splitlines()[start:end])


def test_sprint5_stated_implemented_and_verified_with_args_file_outcome():
    """The section states the Sprint 5 work is implemented and verified
    and names the host-side per-project configuration outcome (the
    trusted args file) as what Sprint 5 delivered."""
    section = _normalized(_priority_order_section())
    assert "The Sprint 5 work is implemented and verified" in section
    assert "host-side per-project configuration" in section
    assert "args file" in section


def test_backlog_state_recorded_and_next_workflow_step_named():
    """The section notes the S5.2 record-keeping story's completion,
    restates the post-Sprint-5 backlog state, and names the next
    workflow step with a concrete value."""
    section = _normalized(_priority_order_section())
    # Record-keeping story completion noted alongside the Sprint 5 work.
    assert "S5.2 record-keeping story" in section
    # Post-Sprint-5 backlog state restated.
    assert "the backlog is empty" in section
    # Next workflow step named with a concrete (non-placeholder) value.
    match = re.search(r"Next workflow step: (\S+)", section)
    assert match, "no 'Next workflow step:' line found"
    assert match.group(1).strip("`"), "next workflow step value is empty"


def test_merge_mentions_framed_as_replaced_or_no_longer_current():
    """Every mention of root-config merging in the section is framed as
    replaced or no-longer-current — no stale claim presents merging as
    active behavior. Each mention is checked within a window of
    surrounding text, so framing across the document's hard line wraps
    still counts."""
    section = _normalized(_priority_order_section())
    mentions = list(re.finditer(r"merg\w*", section, re.IGNORECASE))
    assert mentions, "no merge mentions found to verify"
    for match in mentions:
        window = section[max(0, match.start() - 100):match.end() + 100]
        assert _MERGE_FRAMING.search(window), (
            f"merge mention not framed as replaced/no-longer-current: "
            f"...{window}..."
        )
