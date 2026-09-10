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


def _ignore_patterns() -> list[str]:
    """Non-comment, non-empty lines of .aiderignore (the specified
    exclusion patterns)."""
    lines = AIDERIGNORE.read_text(encoding="utf-8").splitlines()
    return [
        line.strip()
        for line in lines
        if line.strip() and not line.strip().startswith("#")
    ]


def test_ignore_file_specifies_exclusion_patterns():
    """The ignore file specifies file patterns to exclude from Aider's
    context: at least one non-comment pattern line, each a non-empty
    glob-style pattern."""
    patterns = _ignore_patterns()
    assert patterns, (
        "ignore file must specify at least one exclusion pattern"
    )
    for pattern in patterns:
        assert pattern and not set(pattern) <= {"*", "?", "/", "."}, (
            f"pattern line must be a meaningful glob pattern: {pattern!r}"
        )


CATEGORY_PATTERNS = {
    "dependencies": (
        "node_modules/", "env/", "venv/", ".venv/", "__pycache__/",
        "*.egg-info/",
    ),
    "build artifacts": (
        "dist/", "build/", "*.zip", "*.tar.gz", "*.egg", "coverage/",
        "htmlcov/",
    ),
    "non-essential files": (
        "*.log", ".cache/", ".pytest_cache/", ".DS_Store", ".vscode/",
        ".idea/",
    ),
}


def test_patterns_exclude_dependencies_build_artifacts_and_non_essential_files():
    """The exclusion patterns cover dependencies, build artifacts, and
    non-essential files (Developer Notes focus)."""
    patterns = set(_ignore_patterns())
    for category, candidates in CATEGORY_PATTERNS.items():
        matched = patterns & set(candidates)
        assert matched, (
            f"ignore file must exclude {category}: expected at least one "
            f"of {sorted(candidates)}, found none"
        )
