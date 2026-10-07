"""Story S6.3, Step 4: no tracked file references the old names.

Repo-state suite: runs the story's project-wide searches itself and
asserts zero matches over tracked files. Documentation (README.md and
docs/) is excluded — those references are S6.5's single documentation
pass — and this suite is excluded because the keywords are the check's
mechanism, not old-name references.

Covered here:
- no tracked code or test file references the old repository URL
  (github.com/daveonche/ai_assistant);
- no tracked code or test file references the old module path
  (ai_assistant).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

OLD_REPO_URL_KEYWORD = "github.com/daveonche/ai_assistant"
OLD_MODULE_PATH_KEYWORD = "ai_assistant"

SELF = "tests/test_s6_3_step4.py"

# Documentation scope is S6.5's; the suite itself carries the keywords.
EXCLUDED_PATHS = (
    ":(exclude)docs",
    ":(exclude)README.md",
    f":(exclude){SELF}",
)


def _tracked_matches(keyword: str) -> list[str]:
    """Return tracked-file lines matching keyword ('' when none).

    git grep exit codes: 0 = matches found, 1 = no matches, anything
    else is a usage/pathspec error and is surfaced with stderr.
    """
    result = subprocess.run(
        [
            "git", "--no-pager", "grep", "-n", "-I", keyword,
            "--", ".", *EXCLUDED_PATHS,
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 1:
        return []
    if result.returncode != 0:
        raise AssertionError(
            f"git grep failed (exit {result.returncode}): {result.stderr}"
        )
    return result.stdout.splitlines()


def test_no_tracked_code_or_test_file_references_the_old_repository_url():
    """No tracked code or test file references the old repository URL.

    Maps to Step 4 Must Support: "A project-wide search over tracked
    code and test files reports no matches for the old repository URL".
    """
    matches = _tracked_matches(OLD_REPO_URL_KEYWORD)
    assert not matches, (
        "old repository URL still referenced by tracked files:\n"
        + "\n".join(matches)
    )


def test_no_tracked_code_or_test_file_references_the_old_module_path():
    """No tracked code or test file references the old module path.

    Maps to Step 4 Must Support: "A project-wide search over tracked
    code and test files reports no matches for the old module path".
    """
    matches = _tracked_matches(OLD_MODULE_PATH_KEYWORD)
    assert not matches, (
        "old module path still referenced by tracked files:\n"
        + "\n".join(matches)
    )
