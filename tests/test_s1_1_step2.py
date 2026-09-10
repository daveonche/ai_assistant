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
