"""Release script conformance with project quality checks.

Verifies that scripts/release.sh passes the project's standard static
checks for scripts (shellcheck), is executable, and follows the
machine-checkable rules from the project's shell-script conventions
reference, mirroring the installer checks in test_s2_1_step6.py.
Behavioural coverage stays manual: a release run mutates tracked files,
records a commit, tags, and pushes, so it is exercised with --dry-run
and guarded in CI by the release-tag-guard job.
"""

import os
import stat
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RELEASE = PROJECT_ROOT / "scripts" / "release.sh"


def test_release_script_passes_shellcheck():
    """scripts/release.sh passes shellcheck with zero warnings."""
    result = subprocess.run(
        ["shellcheck", "--shell=bash", str(RELEASE)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"{RELEASE}: shellcheck reported issues:\n"
        f"{result.stdout}{result.stderr}"
    )


def test_release_script_is_executable():
    """scripts/release.sh carries the exec bit on disk."""
    mode = RELEASE.stat().st_mode
    assert mode & stat.S_IXUSR, (
        f"{RELEASE} is not executable; fix with: chmod +x {RELEASE}"
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


def test_release_script_follows_shell_conventions():
    """scripts/release.sh follows machine-checkable shell conventions.

    Checked rules: a plain `#!/usr/bin/env bash` shebang with no flags,
    the `set -euo pipefail` baseline as the first executable line, a
    top-level comment describing the script, 80-character maximum line
    length (here-document bodies exempt), and 2-space indentation with
    no tabs.
    """
    text = RELEASE.read_text()
    lines = text.splitlines()

    assert lines[0] == "#!/usr/bin/env bash", (
        f"{RELEASE}: first line must be '#!/usr/bin/env bash' "
        "without flags"
    )

    first_code = next(
        (line.strip() for line in lines
         if line.strip() and not line.strip().startswith("#")),
        None,
    )
    assert first_code == "set -euo pipefail", (
        f"{RELEASE}: first executable line must be 'set -euo pipefail', "
        f"found: {first_code!r}"
    )

    assert lines[1].startswith("#"), (
        f"{RELEASE}: no top-level comment describing the script"
    )

    heredoc = _here_document_body_lines(lines)
    for number, line in enumerate(lines, start=1):
        if (number - 1) in heredoc:
            continue
        assert len(line) <= 80, (
            f"{RELEASE}: line {number} is {len(line)} chars (max 80)"
        )

    assert "\t" not in text, (
        f"{RELEASE}: tab character found (use 2 spaces)"
    )


def test_bump_refs_rewrites_the_pinned_reference(tmp_path):
    """bump_refs rewrites the pinned reference in every release file.

    Regression test: the sed invocation must run as
    `sed "${sed_args[@]}" ...` — it previously expanded the array as the
    command word and died with "-i: command not found" on the first
    release file, a runtime failure the static checks cannot see.
    """
    stub_dir = tmp_path / "bin"
    stub_dir.mkdir()
    git_stub = stub_dir / "git"
    # `git diff --quiet` must report changes (exit 1) so bump_refs
    # proceeds past its nothing-changed gate; no other git call is used.
    git_stub.write_text("#!/usr/bin/env bash\nexit 1\n")
    git_stub.chmod(0o755)

    pinned = tmp_path / "pinned.txt"
    pinned.write_text("pin v1.0.2 here\n")
    unpinned = tmp_path / "unpinned.txt"
    unpinned.write_text("no pin\n")

    driver = tmp_path / "driver.sh"
    driver.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        f"source '{RELEASE}'\n"
        "OLD_REF='v1.0.2'\n"
        "NEW_REF='v1.0.3'\n"
        "VERBOSE=false\n"
        f"BUMP_FILES=('{pinned}' '{unpinned}')\n"
        "bump_refs\n"
    )

    env = os.environ.copy()
    env["PATH"] = f"{stub_dir}{os.pathsep}{env.get('PATH', '')}"
    result = subprocess.run(
        ["bash", str(driver)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "bumped the pinned reference in 2 files" in result.stdout
    assert pinned.read_text() == "pin v1.0.3 here\n"
    assert unpinned.read_text() == "no pin\n"
