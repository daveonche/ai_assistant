"""Story S2.1, Step 5: documented install and update procedures.

Verifies that README.md documents the one-command install, the
repeatable update path, and the pinned-reference caveat, per
docs/analysis/S2.1-story-steps.md Step 5.
"""

from pathlib import Path

README = Path("README.md")
INSTALL_COMMAND = (
    "curl -fsSL https://raw.githubusercontent.com/daveonche/ai_assistant/"
    "v1.0.17/scripts/install.sh | bash"
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


def test_readme_documents_update_path():
    """README documents the repeatable, git-based update path."""
    text = README.read_text(encoding="utf-8")
    section = _section(text, "Updating an existing install")
    assert section, (
        "README must have an 'Updating an existing install' section"
    )
    assert INSTALL_COMMAND in section, (
        "update section must show the same one-command invocation"
    )
    # The update path must be described as going through the project's
    # own git so the change is reviewable and revertable.
    assert "git" in section, (
        "update section must describe the git-based refresh"
    )
    assert "commit" in section, (
        "update section must state the refresh is recorded as a commit"
    )
    assert "re-apply" in section, (
        "update section must tell users to re-apply local customizations"
    )


def test_readme_documents_pinned_reference_caveat():
    """README explains the pinned-reference caveat and --ref override."""
    text = README.read_text(encoding="utf-8")
    section = _section(text, "Pinned-reference caveat")
    assert section, "README must have a 'Pinned-reference caveat' section"
    # The caveat must name the pinned tag and contrast it with main.
    assert "v1.0.0" in section, (
        "caveat must name the pinned release tag"
    )
    assert "main" in section, (
        "caveat must state the pinned tag is used instead of main"
    )
    assert "reproducible" in section, (
        "caveat must explain the reproducibility rationale"
    )
    # The override path must be shown with the --ref flag.
    assert "--ref" in section, (
        "caveat must document the --ref override"
    )
    assert "bash -s -- --ref" in section, (
        "caveat must show the piped --ref invocation form"
    )
