"""Story S2.1, Step 5: documented install and update procedures.

Verifies that README.md documents the one-command install, the
repeatable update path, and the pinned-reference caveat, per
docs/analysis/S2.1-story-steps.md Step 5.
"""

from pathlib import Path

README = Path("README.md")
INSTALL_COMMAND = (
    "curl -fsSL https://raw.githubusercontent.com/daveonche/ai_assistant/"
    "v1.0.0/scripts/install.sh | bash"
)


def _section(text: str, heading: str) -> str:
    """Return the text under a '#### <heading>' line, or '' if absent."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip() == f"#### {heading}":
            start = i + 1
            break
    if start is None:
        return ""
    section_lines = []
    for line in lines[start:]:
        if line.startswith("#"):
            break
        section_lines.append(line)
    return "\n".join(section_lines)


def test_readme_documents_one_command_install():
    """README documents the one-command install inside the target repo."""
    text = README.read_text(encoding="utf-8")
    section = _section(text, "One-command install")
    assert section, "README must have a 'One-command install' section"
    assert INSTALL_COMMAND in section, (
        "install section must contain the exact one-command curl line"
    )
    assert "target project" in section, (
        "install instructions must state the command runs from inside "
        "the target project's repository"
    )
