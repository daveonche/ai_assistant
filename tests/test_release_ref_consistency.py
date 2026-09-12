"""Release-reference consistency across installer, README, and step 5.

The one-command install is self-referential: the installer served at the
pinned tag's raw URL is the script consumers pipe into bash, and its
DEFAULT_REF decides which reference gets installed. Three places must
therefore name the same release reference:

- scripts/install.sh: DEFAULT_REF, plus the usage() example URLs
- README.md: every documented curl install URL
- tests/test_s2_1_step5.py: INSTALL_COMMAND, asserted against the README

Cutting a release bumps DEFAULT_REF first; a forgotten bump anywhere else
fails this suite, so a partial bump cannot be merged silently.
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INSTALLER = PROJECT_ROOT / "scripts" / "install.sh"
README = PROJECT_ROOT / "README.md"
STEP5 = PROJECT_ROOT / "tests" / "test_s2_1_step5.py"

# The release reference embedded in a documented install URL, e.g.
# .../ai_assistant/v1.0.0/scripts/install.sh -> 'v1.0.0'.
URL_REF = re.compile(r"ai_assistant/([^/\s\"']+)/scripts/install\.sh")


def _default_ref() -> str:
    """Return DEFAULT_REF as recorded in scripts/install.sh."""
    text = INSTALLER.read_text(encoding="utf-8")
    match = re.search(r'^readonly DEFAULT_REF="([^"]+)"$', text, re.M)
    assert match, "scripts/install.sh must define readonly DEFAULT_REF"
    return match.group(1)


def test_readme_install_urls_pin_the_default_ref():
    """Every install URL documented in README.md pins DEFAULT_REF.

    The --ref override example in the pinned-reference caveat may keep
    an older tag as its argument; only the URL itself is checked here.
    """
    refs = URL_REF.findall(README.read_text(encoding="utf-8"))
    assert refs, "README.md must document the install URL"
    expected = _default_ref()
    assert set(refs) == {expected}, (
        f"README.md pins {sorted(set(refs))} but install.sh pins "
        f"{expected!r}; bump every curl URL to {expected} (the --ref "
        "example argument may keep an older tag)"
    )


def test_installer_usage_examples_pin_the_default_ref():
    """The usage() example URLs inside install.sh pin DEFAULT_REF."""
    refs = URL_REF.findall(INSTALLER.read_text(encoding="utf-8"))
    assert refs, "install.sh usage() must show the install URL"
    expected = _default_ref()
    assert set(refs) == {expected}, (
        f"install.sh usage examples pin {sorted(set(refs))} but "
        f"DEFAULT_REF is {expected!r}; bump the example URLs"
    )


def test_step5_install_command_pins_the_default_ref():
    """tests/test_s2_1_step5.py INSTALL_COMMAND pins DEFAULT_REF.

    That suite asserts the README contains this exact command, so the
    two must move together in the bump commit.
    """
    text = STEP5.read_text(encoding="utf-8")
    match = re.search(r'"([^"/]+)/scripts/install\.sh', text)
    assert match, "INSTALL_COMMAND fragment not found in test_s2_1_step5.py"
    pinned = match.group(1)
    expected = _default_ref()
    assert pinned == expected, (
        f"test_s2_1_step5.py INSTALL_COMMAND pins {pinned!r} but "
        f"DEFAULT_REF is {expected!r}; bump them in the same commit"
    )
