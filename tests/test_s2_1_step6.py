"""Story S2.1, Step 6: installer conformance with project quality checks.

Verifies that scripts/install.sh passes the project's standard static
checks for scripts (shellcheck) and follows the machine-checkable rules
from the project's shell-script conventions reference, per
docs/analysis/S2.1-story-steps.md Step 6.
"""

import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INSTALLER = PROJECT_ROOT / "scripts" / "install.sh"


def test_installer_passes_shellcheck():
    """scripts/install.sh passes shellcheck with zero warnings.

    Maps to Step 6 Must Support: "The installer passes the project's
    standard static checks for scripts." The default severity (style
    included) applies, so exit status 0 means a clean report.
    """
    result = subprocess.run(
        ["shellcheck", "--shell=bash", str(INSTALLER)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"{INSTALLER}: shellcheck reported issues:\n"
        f"{result.stdout}{result.stderr}"
    )
