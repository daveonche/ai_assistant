import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DOCUMENTED_LAYERS = ("agent.sh", ".agent", "docs", "scripts", "src")


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


def test_project_files_tracked_from_initial_commit():
    # history begins with exactly one initial project commit
    root_commits = _git("rev-list", "--max-parents=0", "HEAD").splitlines()
    assert len(root_commits) == 1, (
        f"expected exactly one root commit, found {len(root_commits)}"
    )
    root_commit = root_commits[0]

    # the initial commit tracks project files (non-empty tree)
    root_tree = _git("ls-tree", "--name-only", root_commit).splitlines()
    assert root_tree, (
        f"initial commit {root_commit} tracks no project files"
    )

    # the documented layers are tracked in the working tree
    # (project files tracked from the initial commit onward)
    tracked = _git("ls-files").splitlines()
    for layer in DOCUMENTED_LAYERS:
        assert any(
            entry == layer or entry.startswith(f"{layer}/")
            for entry in tracked
        ), f"layer {layer!r} is not currently tracked"
