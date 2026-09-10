import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

IGNORED_PATHS_BY_CATEGORY = {
    "logs": (
        "debug.log",
        "logs/app.log",
        "npm-debug.log",
        "yarn-error.log",
    ),
    "secret/credential files": (
        ".env",
        ".env.local",
        "server.pem",
        "server.key",
        "id_rsa",
        "id_ed25519",
        "credentials.json",
        "secrets/api_key.txt",
    ),
    "container runtime output": (
        ".aider.chat.history",
        ".aider.input.history",
        ".aider.tags.cache.v4",
        ".aider.llm.history",
    ),
}


def _ignored_paths(paths: tuple[str, ...]) -> set[str]:
    result = subprocess.run(
        ["git", "-C", str(PROJECT_ROOT), "check-ignore", "--", *paths],
        capture_output=True,
        text=True,
    )
    return set(result.stdout.splitlines())


def test_exclusion_rules_cover_transient_artifact_categories():
    all_paths = tuple(
        path for paths in IGNORED_PATHS_BY_CATEGORY.values() for path in paths
    )
    ignored = _ignored_paths(all_paths)

    # every representative transient artifact path is excluded by the rules
    for category, paths in IGNORED_PATHS_BY_CATEGORY.items():
        for path in paths:
            assert path in ignored, (
                f"{category} artifact {path!r} is not excluded by .gitignore"
            )


SAMPLE_TRANSIENT_FILES = {
    "sample log file": "sample.log",
    "sample credentials file": "credentials.json",
    "sample container output file": ".aider.chat.history",
}


def test_sample_transient_files_not_reported_as_pending_changes():
    created = []
    try:
        # create the three manual-verification sample files in the working tree
        for description, path in SAMPLE_TRANSIENT_FILES.items():
            sample = PROJECT_ROOT / path
            assert not sample.exists(), (
                f"sample path {path!r} already exists; refusing to overwrite"
            )
            sample.write_text("transient sample content\n")
            created.append(sample)

        # the version control status reports none of them as pending
        # tracked changes
        result = subprocess.run(
            ["git", "-C", str(PROJECT_ROOT), "--no-pager", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
        )
        reported_paths = {
            line[3:] for line in result.stdout.splitlines() if len(line) > 3
        }
        for description, path in SAMPLE_TRANSIENT_FILES.items():
            assert path not in reported_paths, (
                f"{description} ({path!r}) reported as pending tracked changes"
            )
    finally:
        for sample in created:
            sample.unlink(missing_ok=True)


def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(PROJECT_ROOT), "--no-pager", *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def test_exclusion_rules_present_from_initial_commit_onward():
    # history begins with exactly one initial project commit
    root_commits = _git("rev-list", "--max-parents=0", "HEAD").splitlines()
    assert len(root_commits) == 1, (
        f"expected exactly one root commit, found {len(root_commits)}"
    )
    root_commit = root_commits[0]

    # the exclusion rules were tracked in the initial commit's tree
    # (active from the initial commit onward)
    root_tree = set(_git("ls-tree", "--name-only", root_commit).splitlines())
    assert ".gitignore" in root_tree, (
        f".gitignore missing from the initial commit {root_commit}"
    )

    # the exclusion rules remain tracked and non-empty in the working tree
    tracked = _git("ls-files").splitlines()
    assert ".gitignore" in tracked, ".gitignore is not currently tracked"
    assert (PROJECT_ROOT / ".gitignore").read_text().strip(), (
        ".gitignore is empty"
    )
