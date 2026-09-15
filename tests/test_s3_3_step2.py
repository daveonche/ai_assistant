"""Step 2 tests for Story S3.3.

Verifies the release-tooling references in the pin-philosophy
documentation (docs/tech_stack.md): each test maps to one Step 2
Must Support item. The Sprint 3 record (Step 1) and convention
conformance (Step 3) are covered by their own suites, not here.
"""

from pathlib import Path

DOC = Path("docs/tech_stack.md")
PIN_PHILOSOPHY_HEADING = "## Version Lock Rationale"
RELEASE_TOOLING_SENTENCE_PREFIX = "Release tooling enforces this philosophy:"
INSTALLER = Path("scripts/install.sh")


def _doc_text() -> str:
    return DOC.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    """Return text from `heading` up to the next same-level heading."""
    start = text.index(heading)
    nxt = text.find("\n## ", start + len(heading))
    return text[start:nxt if nxt != -1 else len(text)]


def _pin_philosophy() -> str:
    return _section(_doc_text(), PIN_PHILOSOPHY_HEADING)


def _normalized(text: str) -> str:
    """Collapse whitespace so markdown line wraps don't split phrases."""
    return " ".join(text.split())


def test_release_tooling_script_referenced_in_pin_philosophy():
    """Must Support 1: the release tooling script is referenced where
    the version-pinning philosophy is described."""
    section = _pin_philosophy()
    assert "scripts/release.sh" in section, (
        "the pin-philosophy section does not reference "
        "scripts/release.sh as the repeatable release entry point"
    )


def test_release_tag_guard_referenced_with_enforcement_mechanism():
    """Must Support 2: the release tag-guard job is referenced where the
    version-pinning philosophy is described, with how it enforces the
    pinned references."""
    section = _pin_philosophy()
    assert "release-tag-guard" in section, (
        "the pin-philosophy section does not reference the "
        "release-tag-guard CI job"
    )
    assert "DEFAULT_REF" in section and "scripts/install.sh" in section, (
        "the pin-philosophy section does not describe how the guard "
        "enforces the pinned reference (DEFAULT_REF in scripts/install.sh)"
    )
    assert "v*" in section, (
        "the pin-philosophy section does not state which pushes the "
        "guard enforces (v* tag pushes)"
    )


def test_release_tooling_references_integrate_without_duplication_or_contradiction():
    """Must Support 3: the release-tooling references integrate with the
    existing verified-pins narrative without duplication or contradiction."""
    # Integration: the reference lives inside the pin-philosophy narrative,
    # phrased as enforcing "this philosophy", with no new topic heading.
    assert RELEASE_TOOLING_SENTENCE_PREFIX in _normalized(_pin_philosophy()), (
        "the release-tooling reference does not sit inside the "
        "Version Lock Rationale narrative"
    )
    headings = [
        line for line in _pin_philosophy().splitlines() if line.startswith("#")
    ]
    assert all("release" not in h.lower() for h in headings), (
        "release tooling was given its own topic heading instead of "
        f"integrating with the existing narrative: {headings}"
    )
    # No duplication: the reference appears exactly once in the document.
    assert _normalized(_doc_text()).count(RELEASE_TOOLING_SENTENCE_PREFIX) == 1, (
        "the release-tooling reference is duplicated in docs/tech_stack.md"
    )
    # No contradiction: the enforcement mechanism the doc names exists
    # (value agreement stays delegated to tests/test_release_ref_consistency.py).
    assert "DEFAULT_REF=" in INSTALLER.read_text(encoding="utf-8"), (
        "scripts/install.sh does not define DEFAULT_REF, contradicting the "
        "documented enforcement mechanism"
    )
