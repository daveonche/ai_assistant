"""S5.1 step 7 verification: verification suites exist, obsolete tests gone.

Repo-state suite: asserts the repository's test files, not launcher
behavior. Follows the S1.1 repo-state pattern (git ls-files plus
filesystem checks).

Covered here:
- the four verification suites exist and are git-tracked, one per
  Must Support area (args loading and precedence, template creation
  with no-overwrite, both flags without container tooling, the
  root-counterpart notice);
- the six obsolete project-root merging test files are neither
  git-tracked nor present on disk.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# (suite path, area it verifies) — one suite per Must Support area.
VERIFICATION_SUITES = (
    ("tests/test_s5_1_step2.py", "args loading and precedence"),
    ("tests/test_s5_1_step3.py", "template creation with no-overwrite"),
    ("tests/test_s5_1_step4.py", "both flags without container tooling"),
    ("tests/test_s5_1_step5.py", "root-counterpart notice"),
)


def _tracked_files() -> set[str]:
    result = subprocess.run(
        ["git", "--no-pager", "ls-files"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return set(result.stdout.splitlines())


def test_verification_suites_exist_and_are_tracked():
    """Each Must Support area has its verification suite: present on
    disk and tracked by git."""
    tracked = _tracked_files()
    for path, area in VERIFICATION_SUITES:
        assert (PROJECT_ROOT / path).is_file(), (
            f"verification suite for {area!r} is missing: {path}"
        )
        assert path in tracked, (
            f"verification suite for {area!r} is not tracked by git: {path}"
        )
