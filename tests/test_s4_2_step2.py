"""Tests for Story S4.2 Step 2: project framework detection guidance.

The detection guidance lives in
.agent/.aider.prompt/core/framework-detection/SKILL.md;
.agent/AGENTS.md keeps a pointer stub that loads it (guarded by the
last test in this file)."""

from pathlib import Path

AGENTS_MD = Path(".agent", "AGENTS.md")
SKILL_MD = Path(
    ".agent", ".aider.prompt", "core", "framework-detection", "SKILL.md"
)


def _detection_section() -> str:
    """Return the framework-detection guidance document: the SKILL.md
    that AGENTS.md's Project Framework Detection stub loads."""
    return SKILL_MD.read_text(encoding="utf-8")


def _agents_stub_section() -> str:
    """Return the body of the 'Project Framework Detection' section of
    .agent/AGENTS.md, up to the next '## ' heading."""
    lines = AGENTS_MD.read_text(encoding="utf-8").splitlines()
    start = lines.index("## Project Framework Detection") + 1
    body: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        body.append(line)
    return "\n".join(body)


def _normalized(text: str) -> str:
    """Whitespace-collapsed, lowercased text for phrase assertions."""
    return " ".join(text.split()).lower()


def test_detection_guidance_covers_source_directory_indicators():
    """Must Support: guidance instructs the assistant to inspect framework
    indicators under the project's source directory to identify the
    framework in use."""
    section = _normalized(_detection_section())
    assert "indicators under the source directory" in section
    assert "identify the project's framework" in section
    assert "framework-specific config files" in section
    assert "entry points" in section
    assert "module layout" in section


def test_detection_guidance_covers_root_manifests_and_configs():
    """Must Support: guidance instructs the assistant to inspect root
    manifests and configuration files as additional framework
    indicators."""
    section = _normalized(_detection_section())
    assert "root manifests and configuration files" in section
    assert "composer.json" in section
    assert "package.json" in section
    assert "go.mod" in section


def test_detection_guidance_captures_version_alongside_name():
    """Must Support: when the project indicators reveal the framework
    version, detection captures it alongside the framework name."""
    section = _normalized(_detection_section())
    assert "when the indicators reveal the framework version" in section
    assert "capture it alongside the framework name" in section
    assert "manifest constraints" in section
    assert "lock files" in section
    assert "version pins" in section


def test_detection_guidance_concludes_before_coding_guidance():
    """Must Support: detection concludes with an identified framework
    before coding guidance is offered."""
    section = _normalized(_detection_section())
    assert "conclude detection before offering coding guidance" in section
    assert "identify the project's framework" in section
    assert "by inspecting read-only indicators" in section


def test_detection_guidance_states_no_framework_identified_outcome():
    """Must Support: when no indicators are found, detection concludes
    that no framework is identified."""
    section = _normalized(_detection_section())
    assert "state that no framework was identified" in section
    assert "when no indicators are found" in section
    assert "announce the identified framework and version" in section


def test_agents_md_stub_loads_the_detection_skill():
    """The orchestrator's Project Framework Detection stub loads the
    SKILL.md carrying the detection guidance via the exact /read-only
    command."""
    section = _agents_stub_section()
    assert (
        "/read-only .agent/.aider.prompt/core/framework-detection/SKILL.md"
        in section
    )
