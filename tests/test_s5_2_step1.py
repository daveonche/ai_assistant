"""S5.2 step 1 verification: the Sprint 5 record section.

Documentation-content suite: reads docs/implementation_status.md and
docs/analysis/S5.1-story-steps.md directly and asserts the story's
record requirements — the established pattern of the S3.3/S4.4/S5.1
doc suites. No launcher behavior is exercised here: the S5.1 work
itself is verified by the suites the record cites; this suite keeps
the record aligned with the saved S5.1 analysis and the repository's
test files.

Covered here:
- the Sprint 5 section follows the Sprint 4 section and carries the
  record structure (story heading titled from the saved analysis,
  completed-step list with evidence annotations);
- every step title parsed from the saved S5.1 analysis appears verbatim
  in the record, in step order, as the seven completed-step entries;
- every entry cites at least one tests/ suite, and every cited suite
  exists on disk — so the record cannot cite retired suites.
"""

from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

STATUS_DOC = PROJECT_ROOT / "docs" / "implementation_status.md"
ANALYSIS_DOC = PROJECT_ROOT / "docs" / "analysis" / "S5.1-story-steps.md"


def _status_text() -> str:
    """Return the implementation status document's full text."""
    return STATUS_DOC.read_text(encoding="utf-8")


def _analysis_text() -> str:
    """Return the saved S5.1 analysis's full text."""
    return ANALYSIS_DOC.read_text(encoding="utf-8")


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


def _section(text: str, heading: str) -> str:
    """Return the named section's lines joined with newlines."""
    start, end = _heading_span(text, heading)
    return "\n".join(text.splitlines()[start:end])


def _analysis_story_title() -> str:
    """The S5.1 story title from the analysis's Story line."""
    for line in _analysis_text().splitlines():
        if line.startswith("Story: S5.1 - "):
            return line[len("Story: S5.1 - "):].strip()
    raise AssertionError("S5.1 Story line not found in the analysis")


def _analysis_step_titles() -> list[str]:
    """The step titles, parsed from the analysis's step headings."""
    titles: list[str] = []
    for line in _analysis_text().splitlines():
        match = re.match(r"^## Step (\d+)\. (.+)$", line)
        if match:
            titles.append(match.group(2).strip())
    assert len(titles) == 7, titles
    return titles


def _record_entries(section: str) -> list[tuple[int, str]]:
    """The record's completed-step entries as (step number, remainder
    after the 'Step N. ' prefix: the title plus evidence annotation)."""
    entries: list[tuple[int, str]] = []
    for line in section.splitlines():
        match = re.match(r"^- \[x\] Step (\d+)\. (.+)$", line)
        if match:
            entries.append((int(match.group(1)), match.group(2)))
    return entries


def test_sprint5_section_follows_sprint4_with_the_record_structure():
    """The Sprint 5 section sits after the Sprint 4 section and carries
    the record shape: a story heading titled from the saved analysis's
    Story line, and seven completed-step entries each carrying an
    evidence annotation."""
    text = _status_text()
    sprint4_start, _ = _heading_span(text, "Sprint 4")
    sprint5_start, _ = _heading_span(text, "Sprint 5")
    assert sprint4_start < sprint5_start

    section = _section(text, "Sprint 5")
    assert f"### Story S5.1: {_analysis_story_title()}" in section
    entries = _record_entries(section)
    assert [number for number, _ in entries] == [1, 2, 3, 4, 5, 6, 7]
    for number, remainder in entries:
        # Evidence annotation: a parenthetical after the title (the
        # analysis's step titles contain no parentheses).
        assert "(" in remainder and remainder.endswith(")"), (
            f"step {number} entry lacks an evidence annotation: {remainder!r}"
        )


def test_every_analysis_step_title_appears_verbatim_in_order():
    """Every step title parsed from the saved S5.1 analysis appears
    verbatim in the record, in step order, as the completed-step
    entries' titles — so the record cannot drift from the saved
    analysis or silently drop a scope element."""
    titles = _analysis_step_titles()
    section = _section(_status_text(), "Sprint 5")
    entries = _record_entries(section)
    assert [number for number, _ in entries] == [1, 2, 3, 4, 5, 6, 7]
    for (number, remainder), title in zip(entries, titles):
        # The entry opens with the analysis's title verbatim, then the
        # evidence annotation in parentheses.
        assert remainder.startswith(title + " ("), (
            f"step {number} entry does not carry the analysis title "
            f"{title!r}: {remainder!r}"
        )


def test_every_entry_cites_suites_that_exist_on_disk():
    """Every completed-step entry cites at least one tests/ suite, and
    every cited suite exists on disk — so the record cannot cite
    retired suites."""
    section = _section(_status_text(), "Sprint 5")
    entries = _record_entries(section)
    assert entries, "no completed-step entries found"
    suite_pattern = re.compile(r"tests/test_[A-Za-z0-9_]+\.py")
    for number, remainder in entries:
        cited = suite_pattern.findall(remainder)
        assert cited, (
            f"step {number} entry cites no verification suite: {remainder!r}"
        )
        for suite in cited:
            assert (PROJECT_ROOT / suite).is_file(), (
                f"step {number} entry cites a missing suite: {suite}"
            )
