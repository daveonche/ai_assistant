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


def _here_document_body_lines(lines: list[str]) -> set[int]:
    """Return 0-based indices of lines inside a here-document body.

    The conventions sanction literal strings longer than 80 characters
    inside a here document, so those lines are exempt from the length
    check. The script has a single `cat <<EOF` block.
    """
    body: set[int] = set()
    delimiter: str | None = None
    for i, line in enumerate(lines):
        if delimiter is not None:
            if line.strip() == delimiter:
                delimiter = None
            else:
                body.add(i)
            continue
        if "<<" in line:
            tail = line.split("<<", 1)[1].lstrip("-").strip()
            if tail:
                delimiter = tail.split()[0]
    return body


def test_installer_follows_shell_conventions():
    """scripts/install.sh follows machine-checkable shell conventions.

    Maps to Step 6 Must Support: "The installer follows the project's
    script conventions." Only rules enforceable by inspecting the script
    text are checked: a plain `#!/usr/bin/env bash` shebang with no
    flags, the `set -euo pipefail` baseline as the first executable
    line, a top-level comment describing the script, 80-character
    maximum line length (here-document bodies exempt), and 2-space
    indentation with no tabs.
    """
    text = INSTALLER.read_text()
    lines = text.splitlines()

    # Plain shebang; flags on the shebang line are unreliable across
    # platforms.
    assert lines[0] == "#!/usr/bin/env bash", (
        f"{INSTALLER}: first line must be '#!/usr/bin/env bash' "
        "without flags"
    )

    # Baseline option set as the first executable statement. (Adapted
    # from the 'first 5 lines' check in test_s1_2_step3.py: install.sh
    # carries a multi-line header comment, and the convention only
    # requires the baseline at the top, before executable code.)
    first_code = next(
        (line.strip() for line in lines
         if line.strip() and not line.strip().startswith("#")),
        None,
    )
    assert first_code == "set -euo pipefail", (
        f"{INSTALLER}: first executable line must be 'set -euo pipefail', "
        f"found: {first_code!r}"
    )

    # Top-level comment briefly describing the contents.
    assert lines[1].startswith("#"), (
        f"{INSTALLER}: no top-level comment describing the script"
    )

    # Maximum line length is 80 characters; here-document bodies are
    # exempt (the conventions sanction long literal strings inside a
    # here document).
    heredoc = _here_document_body_lines(lines)
    for number, line in enumerate(lines, start=1):
        if (number - 1) in heredoc:
            continue
        assert len(line) <= 80, (
            f"{INSTALLER}: line {number} is {len(line)} chars (max 80)"
        )

    # Indent 2 spaces; tabs are forbidden.
    assert "\t" not in text, (
        f"{INSTALLER}: tab character found (use 2 spaces)"
    )
