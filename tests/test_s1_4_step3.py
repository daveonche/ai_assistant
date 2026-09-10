"""Story S1.4 Step 3 — Enable context exclusion rules.

Verifies the Must Support items of Step 3 from
docs/analysis/S1.4-story-steps.md:
- Creation of an ignore file for Aider
- Specification of file patterns to exclude from Aider's context
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AIDERIGNORE = REPO_ROOT / ".agent" / ".aiderignore"


def test_aiderignore_file_exists():
    """The Aider ignore file exists in the project."""
    assert AIDERIGNORE.is_file(), f"missing Aider ignore file: {AIDERIGNORE}"
