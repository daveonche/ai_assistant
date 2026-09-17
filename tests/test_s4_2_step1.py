"""Tests for Story S4.2 Step 1: seeded framework conventions delta files."""

from pathlib import Path

CONVENTIONS_DIR = Path(".agent", ".aider.conventions")
SEEDED_FILES = (
    CONVENTIONS_DIR / "ELGG.md",
    CONVENTIONS_DIR / "RAILS.md",
)


def test_seeded_conventions_files_exist():
    for path in SEEDED_FILES:
        assert path.is_file(), f"missing seeded conventions file: {path}"
