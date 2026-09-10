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
