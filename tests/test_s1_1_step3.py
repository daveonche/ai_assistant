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


def test_directories_and_placeholders_present_after_fresh_clone(tmp_path):
    # re-clone the repository into a fresh location
    clone_dir = tmp_path / "clone"
    result = subprocess.run(
        ["git", "clone", str(PROJECT_ROOT), str(clone_dir)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"clone failed: {result.stderr.strip()}"
    )

    # docs/, scripts/, and src/ all exist in the fresh clone
    for placeholder in PLACEHOLDERS:
        assert (clone_dir / placeholder).parent.is_dir(), (
            f"directory {(clone_dir / placeholder).parent.name!r} missing "
            "from fresh clone"
        )

    # each directory in the clone contains its placeholder file
    for placeholder in PLACEHOLDERS:
        assert (clone_dir / placeholder).is_file(), (
            f"placeholder {placeholder!r} missing from fresh clone"
        )
