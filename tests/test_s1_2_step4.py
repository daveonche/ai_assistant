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


PYPROJECT = PROJECT_ROOT / ".agent" / "pyproject.toml"


def _declared_python_minimum() -> str:
    """Return the minimum host Python version declared in pyproject.toml.

    Parsed with a regex instead of tomllib so the tests themselves stay
    compatible with the declared minimum (tomllib requires 3.11+).
    """
    match = re.search(
        r'^requires-python\s*=\s*"(.*?)"', PYPROJECT.read_text(), re.M
    )
    assert match, ".agent/pyproject.toml: requires-python not found"
    version = re.search(r">=\s*(\d+(?:\.\d+)*)", match.group(1))
    assert version, f"unsupported requires-python specifier: {match.group(1)}"
    return version.group(1)


def _entry_line(section: str, prerequisite: str) -> str:
    """Return the bullet line documenting `prerequisite`, or '' if absent."""
    for line in section.splitlines():
        if line.startswith("- ") and prerequisite in line:
            return line
    return ""


@pytest.mark.parametrize(
    "prerequisite, expected_fragments",
    [
        pytest.param("Docker", ("CLI", "Compose Plugin"),
                     id="docker-cli-compose"),
        pytest.param("Bash", ("entry scripts",),
                     id="bash-command-shell"),
        pytest.param("Python", (f">={_declared_python_minimum()}",),
                     id="python-host-minimum"),
    ],
)
def test_documented_set_matches_acceptance_criteria(
    prerequisite, expected_fragments
):
    """Each prerequisite entry matches the acceptance criteria.

    Maps to Step 4 Must Support: "The documented set matches the story's
    acceptance criteria: the container platform CLI with its compose
    plugin, the command shell, and the host runtime at its declared
    minimum version." The Python minimum is parsed live from
    `requires-python` in .agent/pyproject.toml rather than hardcoded.
    """
    line = _entry_line(_prerequisites_section(), prerequisite)
    assert line, (
        f"README.md Prerequisites section has no dedicated "
        f"entry for {prerequisite}"
    )
    for fragment in expected_fragments:
        assert fragment in line, (
            f"README.md entry for {prerequisite} missing "
            f"expected text: {fragment!r}"
        )


def _purpose_text(entry_line: str, prerequisite: str) -> str:
    """Return the purpose text after the 'Name: purpose' separator.

    Markdown link URLs (e.g., https://...) contain a colon too, so the
    separator is searched starting after the prerequisite name; the
    'https:' colon never matches because it is not followed by a space.
    """
    name_index = entry_line.index(prerequisite)
    separator_index = entry_line.find(": ", name_index)
    if separator_index == -1:
        return ""
    return entry_line[separator_index + 2:].strip()


@pytest.mark.parametrize("prerequisite", REQUIRED_PREREQUISITES)
def test_each_prerequisite_states_its_purpose(prerequisite):
    """Every documented prerequisite states what it is needed for.

    Maps to Step 4 Must Support: "Each prerequisite states its purpose
    (what it is needed for)." Documented assumption: the section uses a
    "Name: purpose" bullet format; the purpose is the non-empty text
    following the ': ' separator on the prerequisite's bullet line.
    """
    line = _entry_line(_prerequisites_section(), prerequisite)
    assert line, (
        f"README.md Prerequisites section has no dedicated "
        f"entry for {prerequisite}"
    )
    purpose = _purpose_text(line, prerequisite)
    assert purpose, (
        f"README.md entry for {prerequisite} states no purpose text"
    )
