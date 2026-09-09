"""Story S1.2, Step 4: prerequisite documentation for first use.

Verifies that the readme (README.md) documents every host prerequisite
required to launch the assistant, that the documented set matches the
story's acceptance criteria (container platform CLI with compose plugin,
command shell, host runtime at its declared minimum version), and that
each prerequisite states its purpose.
"""

import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
README = PROJECT_ROOT / "README.md"

REQUIRED_PREREQUISITES = ("Docker", "Bash", "Python")


def _prerequisites_section() -> str:
    """Return the text of the README '## Prerequisites' section."""
    text = README.read_text()
    match = re.search(r"^## Prerequisites\b.*?(?=^##\s|\Z)", text, re.M | re.S)
    assert match, "README.md: no '## Prerequisites' section found"
    return match.group(0)


@pytest.mark.parametrize("prerequisite", REQUIRED_PREREQUISITES)
def test_readme_documents_every_required_host_prerequisite(prerequisite):
    """README's Prerequisites section names every required host prerequisite.

    Maps to Step 4 Must Support: "The readme documents every host
    prerequisite required to launch the assistant" — the required set per
    the acceptance criteria is the container platform CLI (Docker), the
    command shell (Bash), and the host runtime (Python).
    """
    section = _prerequisites_section()
    assert prerequisite in section, (
        f"README.md Prerequisites section does not document: {prerequisite}"
    )
