"""Story S6.3, Step 2: installer display strings use the new title.

Verifies that scripts/install.sh presents the product as "Agentic AI
Development-Workflow" in its header comment and usage text, and no
longer carries the old "AIAssistant" title, per
docs/analysis/S6.3-story-steps.md Step 2. The "ai-assistant" remote
identifier is deliberately not asserted here: it is an identifier, not
a display string, and its behavior is pinned by the update-mode suites
(tests/test_s2_1_step3.py).
"""

import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INSTALLER = PROJECT_ROOT / "scripts" / "install.sh"

NEW_TITLE = "Agentic AI Development-Workflow"
OLD_TITLE = "AIAssistant"


def test_installer_header_comment_uses_new_product_title():
    """The top-level comment names the new product title.

    Maps to Step 2 Must Support: "The scripts/install.sh header comment
    reads 'Agentic AI Development-Workflow' instead of 'AIAssistant'".
    Line 2 is the top-level comment whose presence the installer
    conformance suite (tests/test_s2_1_step6.py) already asserts.
    """
    lines = INSTALLER.read_text(encoding="utf-8").splitlines()
    assert NEW_TITLE in lines[1], (
        f"{INSTALLER}: header comment (line 2) must contain "
        f"{NEW_TITLE!r}; found: {lines[1]!r}"
    )


def test_installer_usage_text_uses_new_product_title():
    """The usage text names the new product title.

    Maps to Step 2 Must Support: "The scripts/install.sh usage text
    reads 'Agentic AI Development-Workflow' instead of 'AIAssistant'".
    --help exits inside parse_args before any git call, so the run is
    hermetic.
    """
    result = subprocess.run(
        [shutil.which("bash"), str(INSTALLER), "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert NEW_TITLE in result.stdout, (
        f"{INSTALLER}: usage text must contain {NEW_TITLE!r}"
    )


def test_installer_does_not_use_old_product_title():
    """The old product title appears nowhere in the installer.

    Maps to Step 2 Must Support: the display strings read the new title
    "instead of 'AIAssistant'".
    """
    text = INSTALLER.read_text(encoding="utf-8")
    assert OLD_TITLE not in text, (
        f"{INSTALLER}: old product title {OLD_TITLE!r} still present"
    )
