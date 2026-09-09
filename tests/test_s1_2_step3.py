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


@pytest.mark.parametrize("script", ENTRY_SCRIPTS, ids=lambda p: p.name)
def test_entry_scripts_follow_shell_conventions(script):
    """Both entry scripts follow machine-checkable shell conventions.

    Maps to Step 3 Must Support: "Script style follows the project's
    shell-script conventions reference." Only rules enforceable by
    inspecting the script text are checked: a plain
    `#!/usr/bin/env bash` shebang with no flags, the
    `set -euo pipefail` baseline option set, a top-level comment
    describing the script, 80-character maximum line length, and
    2-space indentation with no tabs.
    """
    text = script.read_text()
    lines = text.splitlines()

    # Plain shebang; flags on the shebang line are unreliable across platforms.
    assert lines[0] == "#!/usr/bin/env bash", (
        f"{script}: first line must be '#!/usr/bin/env bash' without flags"
    )

    # Baseline option set present near the top of the script.
    assert "set -euo pipefail" in lines[:5], (
        f"{script}: 'set -euo pipefail' missing from the first 5 lines"
    )

    # Top-level comment briefly describing the contents.
    assert lines[1].startswith("#"), (
        f"{script}: line 2 must be a top-level comment describing the script"
    )

    # Maximum line length is 80 characters.
    for number, line in enumerate(lines, start=1):
        assert len(line) <= 80, (
            f"{script}: line {number} is {len(line)} chars (max 80)"
        )

    # Indent 2 spaces; tabs are forbidden.
    assert "\t" not in text, f"{script}: tab character found (use 2 spaces)"
