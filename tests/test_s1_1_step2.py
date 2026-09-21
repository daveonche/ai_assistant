import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DOCUMENTED_DIRECTORIES = (".agent", "docs", "scripts", "src")


def test_top_level_layout_contains_documented_layers():
    # agent.sh exists as a file at the project root
    assert (PROJECT_ROOT / "agent.sh").is_file(), (
        "agent.sh is missing or not a file at the project root"
    )

    # each documented directory layer exists as a directory
    for layer in DOCUMENTED_DIRECTORIES:
        assert (PROJECT_ROOT / layer).is_dir(), (
            f"layer {layer!r} is missing or not a directory at the project root"
        )


ALLOWED_TOP_LEVEL_ENTRIES = {
    # documented layers (Must Support item 1)
    "agent.sh", ".agent", "docs", "scripts", "src",
    # commit message gate layer (documented in README.md)
    ".githooks",
    # test-suite layer established by the unit-testing workflow
    "tests",
    # recognized configuration files and directories
    ".gitignore", "pytest.ini", ".github",
    ".aider.conf.yml", ".aider.model.settings.yml", ".aiderignore",
    ".env.example", "Dockerfile.aider",
    # license/readme deliverables (Step 5)
    "LICENSE", "LICENSE.md", "README", "README.md",
}


def _tracked_top_level_entries() -> set[str]:
    result = subprocess.run(
        ["git", "--no-pager", "ls-files"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return {
        line.split("/", 1)[0]
        for line in result.stdout.splitlines()
        if line
    }


def test_no_undocumented_top_level_entries():
    entries = _tracked_top_level_entries()

    # every top-level entry is a documented layer or a recognized
    # configuration file
    undocumented = sorted(entries - ALLOWED_TOP_LEVEL_ENTRIES)
    assert not undocumented, (
        f"undocumented top-level entries: {undocumented}"
    )


ASSISTANT_CONFIG_ARTIFACTS = (
    "AGENTS.md",
    "ai-assistant.sh",
    "ai_assistant.py",
    ".aider.conf.yml",
    ".aider.model.settings.yml",
    ".aiderignore",
    ".aider.prompt",
    ".aider.conventions",
)

OTHER_DOCUMENTED_LAYERS = ("docs", "scripts", "src")


def test_agent_dir_is_single_assistant_configuration_home():
    agent_dir = PROJECT_ROOT / ".agent"

    # every assistant configuration artifact lives in .agent/
    for artifact in ASSISTANT_CONFIG_ARTIFACTS:
        assert (agent_dir / artifact).exists(), (
            f"assistant configuration artifact {artifact!r} is missing from .agent/"
        )

    # no assistant configuration artifact lives in another documented layer
    for layer in OTHER_DOCUMENTED_LAYERS:
        for artifact in ASSISTANT_CONFIG_ARTIFACTS:
            assert not (PROJECT_ROOT / layer / artifact).exists(), (
                f"assistant configuration artifact {artifact!r} found in {layer}/; "
                ".agent/ is the single home for assistant configuration"
            )

    # the assistant's runtime and prompt home are not duplicated at the top level
    for artifact in ("AGENTS.md", "ai-assistant.sh", "ai_assistant.py",
                     ".aider.prompt", ".aider.conventions"):
        assert not (PROJECT_ROOT / artifact).exists(), (
            f"assistant configuration artifact {artifact!r} found at the top level; "
            ".agent/ is the single home for assistant configuration"
        )
