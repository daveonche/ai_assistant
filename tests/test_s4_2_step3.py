"""Tests for Story S4.2 Step 3: framework-agnostic conventions recommendation.

The framework-conventions bullets live in the Framework Conventions
Routing section of
.agent/workflows/core/framework-detection/SKILL.md; the routing
table and routing rules remain in .agent/AGENTS.md."""

import re
from pathlib import Path

AGENTS_MD = Path(".agent", "AGENTS.md")
SKILL_MD = Path(
    ".agent", "workflows", "core", "framework-detection", "SKILL.md"
)
SPECS_DIR = Path(".agent", "specs")
FRAMEWORK_CONVENTIONS_HEADING = "## Framework Conventions Routing"


def _framework_conventions_bullets() -> str:
    """Return the 'Framework Conventions Routing' bullet block of the
    framework-detection SKILL.md, up to the next '## ' heading."""
    lines = SKILL_MD.read_text(encoding="utf-8").splitlines()
    start = lines.index(FRAMEWORK_CONVENTIONS_HEADING) + 1
    body: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        body.append(line)
    return "\n".join(body)


def _routing_rules() -> str:
    """Return the 'Routing rules:' numbered-list block of
    .agent/AGENTS.md, up to the next '## ' heading."""
    lines = AGENTS_MD.read_text(encoding="utf-8").splitlines()
    start = lines.index("Routing rules:") + 1
    body: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        body.append(line)
    return "\n".join(body)


def _routing_table() -> str:
    """Return the routing table block of the 'Conventions Reference
    Routing' section of .agent/AGENTS.md, up to the 'Routing rules:'
    line."""
    lines = AGENTS_MD.read_text(encoding="utf-8").splitlines()
    start = lines.index("## Conventions Reference Routing") + 1
    end = lines.index("Routing rules:")
    return "\n".join(lines[start:end])


def _pack_names() -> list[str]:
    """Pack directory names, discovered structurally: a pack is any
    .agent/specs/ subdirectory containing SKILL.md."""
    return sorted(path.parent.name for path in SPECS_DIR.glob("*/SKILL.md"))


def _normalized(text: str) -> str:
    """Whitespace-collapsed, lowercased text for phrase assertions."""
    return " ".join(text.replace("`", "").split()).lower()


def test_framework_conventions_discovered_by_scanning():
    """Must Support: the assistant discovers available framework
    conventions by scanning the framework-named files in
    .agent/specs/, rather than relying on a fixed
    framework-to-file mapping, so adding a new framework requires only
    adding its conventions file."""
    section = _normalized(_framework_conventions_bullets())
    assert "discovered by scanning the framework-named files" in section
    assert ".agent/specs/" in section
    assert "adding a new framework requires only adding its conventions file" in section
    assert "never a table edit" in section


def test_matching_framework_recommends_inline_read_only():
    """Must Support: when the detected framework matches an available
    conventions file, the assistant recommends loading that file via the
    /read-only command, outputting the command inline rather than
    executing it itself."""
    section = _normalized(_framework_conventions_bullets())
    assert "when the detected framework matches a framework-named file" in section
    assert "output the matching /read-only command inline" in section
    assert "per critical rules" in section
    assert "wait for the user to add it" in section


def test_version_specific_reference_recommended_when_identifiable():
    """Must Support: when the matched framework conventions file
    references version-specific conventions under the conventions
    reference directory and the project's framework version is
    identifiable, the assistant also recommends loading the matching
    version-specific reference."""
    section = _normalized(_framework_conventions_bullets())
    assert "points at version-specific conventions under" in section
    assert ".agent/specs/references/<framework>/<version>/" in section
    assert "the detected version is identifiable" in section
    assert "a matching directory exists" in section
    assert "recommend loading that reference too" in section


def test_recommendation_follows_routing_conventions():
    """Must Support: the recommendation follows the routing conventions
    established in the orchestration documentation."""
    rules = _normalized(_routing_rules())
    bullets = _normalized(_framework_conventions_bullets())
    mirrored = (
        "output the matching /read-only command inline "
        "(per critical rules) and wait for the user to add it"
    )
    # The framework bullet mirrors the routing rule's directive phrasing.
    assert mirrored in rules
    assert mirrored in bullets


def test_routing_table_has_framework_pack_matching_rule():
    """Must Support: the routing table in the orchestration
    documentation gains the framework-based routing rule as a generic
    pack-matching rule alongside the existing file-type rules. No
    framework or file names are hardcoded: the row's example packs are
    checked against packs discovered structurally from .agent/specs/."""
    rows = [
        _normalized(line)
        for line in _routing_table().splitlines()
        if line.strip().startswith("|")
    ]
    framework_rows = [
        row
        for row in rows
        if "a framework identified by project framework detection" in row
    ]
    assert framework_rows, "routing table lacks the framework row"
    assert any(
        "the matching framework pack's skill.md in .agent/specs/" in row
        for row in framework_rows
    ), "framework row does not route to a pack SKILL.md"
    # The row cites pack examples; every cited pack must exist, and the
    # names come from structural discovery, not from this test.
    cited = re.findall(r"[a-z0-9-]+/skill\.md", " ".join(framework_rows))
    assert cited, "framework row cites no pack SKILL.md example"
    packs = set(_pack_names())
    stale = [name for name in cited if name.split("/")[0] not in packs]
    assert not stale, f"framework row cites non-existent packs: {stale}"
    # Placed in the same table as the existing file-type rules: other
    # rows route tasks into the cross-cutting references directory.
    assert any(".agent/specs/references/" in row for row in rows), (
        "routing table lacks file-type reference rows"
    )


def test_no_matching_framework_makes_no_recommendation():
    """Must Support: when the detected framework has no matching
    conventions file, the assistant makes no recommendation and
    continues with existing default conventions."""
    section = _normalized(_framework_conventions_bullets())
    assert "when no framework-named file matches the detected framework" in section
    assert "make no recommendation" in section
    assert "continue with the existing conventions" in section
