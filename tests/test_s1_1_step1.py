import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", "--no-pager", *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def test_project_root_is_version_controlled_repository():
    # .git metadata exists at the project root
    assert (PROJECT_ROOT / ".git").exists(), (
        "project root has no .git metadata"
    )

    # the working tree is a version-controlled repository
    inside = _git("rev-parse", "--is-inside-work-tree")
    assert inside == "true", "project root is not inside a git work tree"

    # the repository is rooted at the project root (Developer Note:
    # keep the repository rooted at the project root)
    toplevel = Path(_git("rev-parse", "--show-toplevel")).resolve()
    assert toplevel == PROJECT_ROOT.resolve(), (
        f"repo toplevel {toplevel} != project root {PROJECT_ROOT.resolve()}"
    )
