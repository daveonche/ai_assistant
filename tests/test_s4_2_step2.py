"""Tests for Story S4.2 Step 2: project framework detection guidance."""

from pathlib import Path

AGENTS_MD = Path(".agent", "AGENTS.md")
SECTION_HEADING = "## Project Framework Detection"


def _detection_section() -> str:
    """Return the body of the 'Project Framework Detection' section of
    .agent/AGENTS.md, up to the next '## ' heading."""
    lines = AGENTS_MD.read_text(encoding="utf-8").splitlines()
    start = lines.index(SECTION_HEADING) + 1
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
