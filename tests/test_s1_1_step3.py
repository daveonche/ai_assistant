import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PLACEHOLDERS = ("docs/.gitkeep", "scripts/.gitkeep", "src/.gitkeep")


def _tracked_files() -> set[str]:
    result = subprocess.run(
        ["git", "--no-pager", "ls-files"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return set(result.stdout.splitlines())


def test_each_documented_directory_contains_tracked_placeholder():
    tracked = _tracked_files()

    # each documented directory contains its placeholder file
    for placeholder in PLACEHOLDERS:
        assert (PROJECT_ROOT / placeholder).is_file(), (
            f"placeholder {placeholder!r} is missing or not a file"
        )

    # each placeholder is tracked by git (this is what keeps the
    # empty directory in the repository)
    for placeholder in PLACEHOLDERS:
        assert placeholder in tracked, (
            f"placeholder {placeholder!r} is not tracked by git"
        )
