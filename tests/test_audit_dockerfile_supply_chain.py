"""Reproducer tests for the Dockerfile.aider supply-chain audit findings.

Each test asserts the *secure* behavior; all three fail against the pre-fix
Dockerfile (remote script piped to bash, unverified ShellCheck tarball,
floating mermaid-cli range) and pass once the fixes are applied.
"""

import re
from pathlib import Path

DOCKERFILE = Path(__file__).resolve().parents[1] / ".agent" / "Dockerfile.aider"

SHELLCHECK_DIGESTS = (
    "6c881ab0698e4e6ea235245f22832860544f17ba386442fe7e9d629f8cbedf87",  # x86_64
    "324a7e89de8fa2aed0d0c28f3dab59cf84c6d74264022c00c22af665ed1a09bb",  # aarch64
    "1c89cb51e1412b580d7ba8aac240251ffb0b829788f83d2daa4a82da42d275e4",  # armv6hf
)


def _dockerfile_text() -> str:
    return DOCKERFILE.read_text(encoding="utf-8")


def test_finding1_no_remote_script_piped_to_shell():
    text = _dockerfile_text()
    assert (
        re.search(r"curl\s+-fsSL\s+\S+\s*\|\s*(ba)?sh\b", text) is None
    ), "remote script piped into a root shell (NodeSource setup_22.x)"
    assert "setup_22.x" not in text
    assert "nodesource.gpg" in text, "NodeSource must come from its signed apt repo"


def test_finding2_shellcheck_tarball_checksum_gated():
    text = _dockerfile_text()
    for arch in ("X86_64", "AARCH64", "ARMV6HF"):
        assert f"ARG SHELLCHECK_SHA256_{arch}=" in text
    for digest in SHELLCHECK_DIGESTS:
        assert digest in text
    download = text.find('curl -fsSL "https://github.com/koalaman/shellcheck')
    verify = text.find("sha256sum -c -")
    extract = text.find("tar -xJf /tmp/shellcheck.tar.xz")
    assert -1 not in (download, verify, extract), "download/verify/extract step missing"
    assert (
        download < verify < extract
    ), "checksum gate must run after the download and before extraction"


def test_finding3_mermaid_cli_exact_pinned():
    text = _dockerfile_text()
    assert "@mermaid-js/mermaid-cli@11.17.0" in text, "mermaid-cli must be exact-pinned"
    assert "@mermaid-js/mermaid-cli@^" not in text, "floating caret range must go"
