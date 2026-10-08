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

Exception: the legacy-URL migration intentionally matches the old URL
to rewrite it — the installer's LEGACY_REPO_URL constant and the S2.1
Step 3 regression tests pinning that migration. Those exact lines are
allowlisted (ALLOWED_MATCHES); any other match still fails.
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

# Intentional old-URL references: the legacy-URL migration matches the
# pre-rename URL exactly to rewrite it (scripts/install.sh
# LEGACY_REPO_URL), and the S2.1 Step 3 regression tests pin that
# migration. Each entry is (path prefix, line substring); a grep match
# is exempt only when both match, so a stale reference in any other
# file — or any other line — still fails.
ALLOWED_MATCHES = (
    ("scripts/install.sh:", "readonly LEGACY_REPO_URL="),
    (
        "tests/test_s2_1_step3.py:",
        '"REMOTE_URL": "https://github.com/daveonche/ai_assistant.git"',
    ),
    (
        "tests/test_s2_1_step3.py:",
        '" https://github.com/daveonche/ai_assistant.git to"',
    ),
    (
        "tests/test_s2_1_step3.py:",
        '"https://github.com/daveonche/ai_assistant.git",',
    ),
)


def _intentional(match: str) -> bool:
    """True when a grep match is an allowlisted intentional legacy
    reference (path prefix and line substring both match)."""
    return any(
        match.startswith(path_prefix) and needle in match
        for path_prefix, needle in ALLOWED_MATCHES
    )


def _tracked_matches(keyword: str) -> list[str]:
    """Return tracked-file lines matching keyword, minus the allowlisted
    intentional legacy references (empty list when none).

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
    return [
        line
        for line in result.stdout.splitlines()
        if not _intentional(line)
    ]


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
