import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ARCHITECTURE_DOC = PROJECT_ROOT / "docs" / "architecture" / "architecture.md"


def _core_layers_section() -> str:
    text = ARCHITECTURE_DOC.read_text()
    marker = "## Core Layers"
    start = text.find(marker)
    assert start != -1, "architecture.md has no 'Core Layers' section"
    rest = text[start + len(marker):]
    end = rest.find("\n## ")
    return rest[:end] if end != -1 else rest


def _documented_layers() -> list[tuple[str, str]]:
    layers = []
    for line in _core_layers_section().splitlines():
        if not line.startswith("- **"):
            continue
        name, _, remainder = line[4:].partition("**")
        location_match = re.search(r"`([^`]+)`", remainder)
        assert location_match, f"layer {name!r} documents no repository location"
        layers.append((name.strip(), location_match.group(1)))
    return layers


def _location_resolves(location: str) -> bool:
    if location.endswith("/**"):
        base = PROJECT_ROOT / location[:-3]
        return base.is_dir() and any(base.iterdir())
    if "**" in location:
        return next(PROJECT_ROOT.glob(location), None) is not None
    if location.endswith("/"):
        return (PROJECT_ROOT / location).is_dir()
    return (PROJECT_ROOT / location).is_file()


def test_each_architecture_layer_has_repository_location():
    layers = _documented_layers()

    # the documented layer set is fully parsed (floor of 8, the current
    # documented count, guards against silent parsing regressions)
    assert len(layers) >= 8, (
        f"expected at least 8 documented layers, parsed {len(layers)}"
    )

    # each documented layer's location resolves in the repository
    for name, location in layers:
        assert _location_resolves(location), (
            f"architecture layer {name!r} has no repository location at {location!r}"
        )
