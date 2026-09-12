"""Release script conformance with project quality checks.

Verifies that scripts/release.sh passes the project's standard static
checks for scripts (shellcheck), is executable, and follows the
machine-checkable rules from the project's shell-script conventions
reference, mirroring the installer checks in test_s2_1_step6.py.
The bump_refs, resolve_python, and preflight_tests functions are
additionally exercised against temporary layouts; a full release run
still stays manual (it mutates tracked files, records a commit, tags,
and pushes), guarded in CI by the release-tag-guard job.
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

    # The real release-file layout inside the sandbox: bump_refs runs
    # against the script's own readonly BUMP_FILES list (the driver must
    # not reassign a readonly constant), so the actual list is exercised
    # and any drift in it fails this test.
    release_files = [
        "scripts/install.sh",
        "README.md",
        "tests/test_s2_1_step1.py",
        "tests/test_s2_1_step2.py",
        "tests/test_s2_1_step3.py",
        "tests/test_s2_1_step4.py",
        "tests/test_s2_1_step5.py",
    ]
    for rel in release_files:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"pin v1.0.2 in {rel}\n")

    driver = tmp_path / "driver.sh"
    driver.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        f"source '{RELEASE}'\n"
        "OLD_REF='v1.0.2'\n"
        "NEW_REF='v1.0.3'\n"
        "VERBOSE=false\n"
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
    assert "bumped the pinned reference in 7 files" in result.stdout
    for rel in release_files:
        assert (tmp_path / rel).read_text() == f"pin v1.0.3 in {rel}\n"


def test_resolve_python_fails_before_any_mutation(tmp_path):
    """resolve_python fails before the bump when pytest is unavailable.

    Regression test: the release run previously reached the pytest gate
    only after bump_refs had rewritten all seven release files, so a
    missing pytest module aborted mid-run with a dirty work tree. The
    interpreter probe now runs before any file is modified.
    """
    stub_dir = tmp_path / "bin"
    stub_dir.mkdir()
    python_stub = stub_dir / "python3"
    # A python3 whose pytest probe fails, like a bare system interpreter.
    python_stub.write_text("#!/usr/bin/env bash\nexit 1\n")
    python_stub.chmod(0o755)

    driver = tmp_path / "driver.sh"
    driver.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        f"source '{RELEASE}'\n"
        "resolve_python\n"
    )

    env = os.environ.copy()
    env["PATH"] = f"{stub_dir}{os.pathsep}{env.get('PATH', '')}"
    env.pop("PYTHON_BIN", None)
    result = subprocess.run(
        ["bash", str(driver)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "no pytest-capable python interpreter found" in result.stderr


def test_resolve_python_falls_back_to_path_python3(tmp_path):
    """resolve_python skips a pytest-less .venv and uses PATH python3."""
    stub_dir = tmp_path / "bin"
    stub_dir.mkdir()
    python_stub = stub_dir / "python3"
    python_stub.write_text("#!/usr/bin/env bash\nexit 0\n")
    python_stub.chmod(0o755)
    # A project virtual environment without pytest: the probe fails and
    # the PATH interpreter is used instead.
    venv_python = tmp_path / ".venv" / "bin" / "python3"
    venv_python.parent.mkdir(parents=True)
    venv_python.write_text("#!/usr/bin/env bash\nexit 1\n")
    venv_python.chmod(0o755)

    driver = tmp_path / "driver.sh"
    driver.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        f"source '{RELEASE}'\n"
        "resolve_python\n"
    )

    env = os.environ.copy()
    env["PATH"] = f"{stub_dir}{os.pathsep}{env.get('PATH', '')}"
    env.pop("PYTHON_BIN", None)
    result = subprocess.run(
        ["bash", str(driver)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "test interpreter: python3" in result.stdout


def test_preflight_tests_validates_the_clean_tree(tmp_path):
    """preflight_tests runs the suite through the resolved interpreter.

    The preflight gate proves the environment can pass the full suite
    before bump_refs touches any file, so an environment gap (a missing
    module or tool such as shellcheck) aborts the release with a clean
    tree instead of after the bump.
    """
    stub_dir = tmp_path / "bin"
    stub_dir.mkdir()
    python_stub = stub_dir / "pytest-python"
    python_stub.write_text("#!/usr/bin/env bash\nexit 0\n")
    python_stub.chmod(0o755)

    driver = tmp_path / "driver.sh"
    driver.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        f"source '{RELEASE}'\n"
        f"PYTHON_BIN='{python_stub}'\n"
        "preflight_tests\n"
    )

    env = os.environ.copy()
    result = subprocess.run(
        ["bash", str(driver)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "preflight: validating the clean tree" in result.stdout


def test_preflight_tests_failure_reports_a_clean_tree(tmp_path):
    """preflight_tests failure says no files were modified."""
    stub_dir = tmp_path / "bin"
    stub_dir.mkdir()
    python_stub = stub_dir / "pytest-python"
    python_stub.write_text("#!/usr/bin/env bash\nexit 1\n")
    python_stub.chmod(0o755)

    driver = tmp_path / "driver.sh"
    driver.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        f"source '{RELEASE}'\n"
        f"PYTHON_BIN='{python_stub}'\n"
        "preflight_tests\n"
    )

    env = os.environ.copy()
    result = subprocess.run(
        ["bash", str(driver)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "no files were modified" in result.stderr
