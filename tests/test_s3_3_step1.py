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


S3_1_HEADING = "### Story S3.1: Release Reference Consistency Verification"
S3_2_HEADING = "### Story S3.2: Release Tag Guard Verification"
RELEASE_SCRIPT_HEADING = "### Release Script Work"
NARRATIVE_HEADING = "## Priority Order for Next Implementation Phase"
NARRATIVE_RELEASE_ITEMS = (
    "release-reference consistency",
    "release tag guard",
    "release script",
)


def _subsection(text: str, heading: str) -> str:
    """Return text from `heading` up to the next heading of the same level."""
    level = heading.split(" ")[0] + " "  # e.g. "### "
    start = text.index(heading)
    nxt = text.find("\n" + level, start + len(heading))
    return text[start:nxt if nxt != -1 else len(text)]


def _sprint3_section() -> str:
    return _section(_doc_text(), "## Sprint 3")


def _closing_narrative() -> str:
    return _section(_doc_text(), NARRATIVE_HEADING)


def _normalized(text: str) -> str:
    """Collapse whitespace so markdown line wraps don't split phrases."""
    return " ".join(text.split())


def _checkbox_lines(story_text: str) -> list[str]:
    return [
        line
        for line in story_text.splitlines()
        if line.lstrip().startswith("- [")
    ]


def test_sprint3_section_exists():
    """Must Support 1: a Sprint 3 section is present."""
    assert "## Sprint 3" in _doc_text()


def test_release_reference_consistency_steps_completed():
    """Must Support 2: the S3.1 release-reference consistency work is
    listed as completed steps in the Sprint 3 section."""
    sprint3 = _sprint3_section()
    assert S3_1_HEADING in sprint3, (
        "Sprint 3 section does not record the release-reference "
        "consistency verification story (S3.1)"
    )
    story = _subsection(sprint3, S3_1_HEADING)
    boxes = _checkbox_lines(story)
    assert boxes, "S3.1 story records no steps"
    unchecked = [line for line in boxes if "- [ ]" in line]
    assert not unchecked, f"S3.1 has unchecked steps: {unchecked}"


def test_release_tag_guard_steps_completed():
    """Must Support 3: the S3.2 release tag-guard verification work is
    listed as completed steps in the Sprint 3 section."""
    sprint3 = _sprint3_section()
    assert S3_2_HEADING in sprint3, (
        "Sprint 3 section does not record the release tag-guard "
        "verification story (S3.2)"
    )
    story = _subsection(sprint3, S3_2_HEADING)
    boxes = _checkbox_lines(story)
    assert boxes, "S3.2 story records no steps"
    unchecked = [line for line in boxes if "- [ ]" in line]
    assert not unchecked, f"S3.2 has unchecked steps: {unchecked}"


def test_release_script_work_completed():
    """Must Support 4: the release-script work is listed as completed
    steps in the Sprint 3 section."""
    sprint3 = _sprint3_section()
    assert RELEASE_SCRIPT_HEADING in sprint3, (
        "Sprint 3 section does not record the release-script work"
    )
    work = _subsection(sprint3, RELEASE_SCRIPT_HEADING)
    boxes = _checkbox_lines(work)
    assert boxes, "Release Script Work records no steps"
    unchecked = [line for line in boxes if "- [ ]" in line]
    assert not unchecked, f"Release Script Work has unchecked steps: {unchecked}"


def test_closing_narrative_records_release_verification():
    """Must Support 5: the closing status narrative reflects that the
    release work is verified and recorded, and presents no release
    work as pending."""
    assert NARRATIVE_HEADING in _doc_text(), (
        "closing status narrative section is missing"
    )
    narrative = _normalized(_closing_narrative())
    assert "verified and recorded" in narrative, (
        "closing narrative does not state the release work is "
        "verified and recorded"
    )
    missing = [item for item in NARRATIVE_RELEASE_ITEMS if item not in narrative]
    assert not missing, (
        f"closing narrative does not mention the release work item(s): {missing}"
    )
    unchecked = [
        line
        for line in _checkbox_lines(_sprint3_section())
        if "- [ ]" in line
    ]
    assert not unchecked, (
        f"Sprint 3 section still presents release work as pending: {unchecked}"
    )
