import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DOCKERFILE = PROJECT_ROOT / ".agent" / "Dockerfile.aider"

_DIGEST_PATTERN = re.compile(r"@sha256:([0-9a-f]{64})\b")

_MOVING_TAGS = {"latest", "dev", "main"}


def _from_references() -> list[str]:
    references = [
        line.split(None, 1)[1].strip()
        for line in DOCKERFILE.read_text().splitlines()
        if line.strip().startswith("FROM ")
    ]
    assert references, f"{DOCKERFILE} contains no FROM instruction"
    return references


def test_image_definition_pins_base_image_by_tag_and_digest():
    references = _from_references()

    # exactly one base image reference (single-stage build)
    assert len(references) == 1, (
        f"expected exactly one FROM instruction, found {len(references)}"
    )
    reference = references[0]

    # pinned by digest: @sha256:<64 hex chars>
    digest_match = _DIGEST_PATTERN.search(reference)
    assert digest_match, (
        f"base image reference {reference!r} carries no sha256 digest pin"
    )

    # pinned by a specific, non-floating tag before the digest
    image_ref = reference.split("@", 1)[0]
    image, _, tag = image_ref.partition(":")
    assert image and tag, (
        f"base image reference {reference!r} lacks an explicit tag"
    )
    assert tag not in _MOVING_TAGS, (
        f"base image tag {tag!r} is a moving tag, not a specific version"
    )
