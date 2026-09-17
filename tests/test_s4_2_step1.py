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


def _file_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_files_declare_delta_only_scope():
    for path in SEEDED_FILES:
        text = _file_text(path)
        assert "delta guidance" in text.lower(), (
            f"{path} does not declare delta-only guidance"
        )
        assert "## Scope" in text, f"{path} missing Scope section"
        assert "Do not add general" in text, (
            f"{path} missing exclusion of general framework knowledge"
        )
        assert "API references" in text, f"{path} missing exclusion of API references"
        assert "tutorials" in text, f"{path} missing exclusion of tutorials"
