"""Story S1.2, Step 3: executable entry scripts that pass static checks.

Verifies that both entry scripts (`agent.sh` and
`.agent/ai-assistant.sh`) are marked executable so they run directly,
pass the project's shell-script static checks (shellcheck) with no
warnings, and follow the machine-checkable rules from the project's
shell-script conventions reference.
"""

import stat
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

ENTRY_SCRIPTS = (
    PROJECT_ROOT / "agent.sh",
    PROJECT_ROOT / ".agent" / "ai-assistant.sh",
)


@pytest.mark.parametrize("script", ENTRY_SCRIPTS, ids=lambda p: p.name)
def test_entry_scripts_are_executable(script):
    """Both entry scripts run directly: X bits set for u/g/o.

    Git records the mode bit, so a working-tree check proves a fresh
    clone preserves executability.
    """
    mode = script.stat().st_mode
    assert mode & stat.S_IXUSR, f"{script}: not executable by user"
    assert mode & stat.S_IXGRP, f"{script}: not executable by group"
    assert mode & stat.S_IXOTH, f"{script}: not executable by other"


@pytest.mark.parametrize("script", ENTRY_SCRIPTS, ids=lambda p: p.name)
def test_entry_scripts_pass_shellcheck(script):
    """Both entry scripts pass shellcheck with zero warnings.

    Maps to Step 3 Must Support: "Both scripts pass the project's
    shell-script static checks with no warnings." The default severity
    (style included) applies, so exit status 0 means a clean report.
    """
    result = subprocess.run(
        ["shellcheck", "--shell=bash", str(script)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"{script}: shellcheck reported issues:\n"
        f"{result.stdout}{result.stderr}"
    )
