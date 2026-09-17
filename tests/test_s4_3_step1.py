"""Tests for Story S4.3 Step 1: corrected automatic-increment example.

Verifies that the README's `--auto` release example shows the version's
patch segment changing from one release to the next.
"""

import re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]

_AUTO_EXAMPLE_PATTERN = re.compile(
    r"patch segment\s*\(\s*`v(\d+)\.(\d+)\.(\d+)`"
    r"\s*->\s*`v(\d+)\.(\d+)\.(\d+)`\s*\)"
)


def _read(path: str) -> str:
    return (_REPO_ROOT / path).read_text(encoding="utf-8")


def _parse_patch(version: str) -> tuple[int, int, int]:
    match = re.fullmatch(r"v(\d+)\.(\d+)\.(\d+)", version)
    assert match is not None, f"expected a vX.Y.Z tag, got {version!r}"
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def _auto_example_pair() -> tuple[str, str]:
    """Extract the (before, after) versions from the README --auto example."""
    text = _read("README.md")
    match = _AUTO_EXAMPLE_PATTERN.search(text)
    assert match is not None, (
        "README.md must document the --auto increment with a version pair"
    )
    before = "v{}.{}.{}".format(*match.groups()[:3])
    after = "v{}.{}.{}".format(*match.groups()[3:])
    return before, after


def test_auto_increment_example_shows_patch_segment_changing():
    before, after = _auto_example_pair()
    before_major, before_minor, before_patch = _parse_patch(before)
    after_major, after_minor, after_patch = _parse_patch(after)

    assert (after_major, after_minor) == (before_major, before_minor), (
        "the --auto example must change only the patch segment"
    )
    assert after_patch == before_patch + 1, (
        "the --auto example must show the patch segment incrementing by one"
    )
