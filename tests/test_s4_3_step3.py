"""Tests for Story S4.3 Step 3: documentation-conventions conformance.

Verifies that the edited release documentation -- the `--auto` example
paragraph and its adjacent code fences in the README's "Cutting a
release" subsection -- conforms to the project's markdown conventions.
"""

import re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]

_SECTION_HEADING = "Cutting a release"

_HEADING_PATTERN = re.compile(r"^(#+)\s")

_VERSION_PAIR_PATTERN = re.compile(
    r"`v\d+\.\d+\.\d+`\s*->\s*`v\d+\.\d+\.\d+`"
)


def _read(path: str) -> str:
    return (_REPO_ROOT / path).read_text(encoding="utf-8")


def _is_fence(line: str) -> bool:
    return line.lstrip().startswith("```")


def _release_section() -> list[str]:
    """Extract the body of the README 'Cutting a release' subsection."""
    lines = _read("README.md").splitlines()
    start = None
    heading_level = 0
    in_fence = False
    for index, line in enumerate(lines):
        if _is_fence(line):
            in_fence = not in_fence
        elif not in_fence:
            match = _HEADING_PATTERN.match(line)
            if match and _SECTION_HEADING in line:
                start = index + 1
                heading_level = len(match.group(1))
                break
    assert start is not None, (
        "README.md must contain a 'Cutting a release' subsection"
    )
    end = len(lines)
    for index in range(start, len(lines)):
        line = lines[index]
        if _is_fence(line):
            in_fence = not in_fence
        elif not in_fence:
            match = _HEADING_PATTERN.match(line)
            if match and len(match.group(1)) <= heading_level:
                end = index
                break
    return lines[start:end]


def _paragraph_containing_auto_example(
    section: list[str],
) -> tuple[int, int]:
    """Locate the --auto example paragraph; return its (start, end) bounds."""
    anchor = None
    for index, line in enumerate(section):
        if _VERSION_PAIR_PATTERN.search(line):
            anchor = index
            break
    assert anchor is not None, (
        "the 'Cutting a release' subsection must document the --auto "
        "increment with a version pair"
    )
    start = anchor
    while start > 0 and section[start - 1].strip():
        start -= 1
    end = anchor + 1
    while end < len(section) and section[end].strip():
        end += 1
    return start, end


def test_edited_release_section_conforms_to_markdown_conventions():
    section = _release_section()
    paragraph_start, paragraph_end = _paragraph_containing_auto_example(section)

    # Structure: the edited paragraph is blank-line separated from the
    # blocks around it.
    assert paragraph_start > 0 and not section[paragraph_start - 1].strip(), (
        "the --auto example paragraph must be preceded by a blank line"
    )
    assert paragraph_end == len(section) or not section[paragraph_end].strip(), (
        "the --auto example paragraph must be followed by a blank line"
    )

    # Fencing: balanced backtick fences, a bare closer before the example,
    # and a bash opener after it.
    fence_indexes = [
        index for index, line in enumerate(section) if _is_fence(line)
    ]
    assert len(fence_indexes) % 2 == 0, (
        "code fences in the subsection must be balanced"
    )
    for index, line in enumerate(section):
        assert not line.lstrip().startswith("~~~"), (
            "fences must use the same backtick character, not tildes"
        )
    before = [index for index in fence_indexes if index < paragraph_start]
    after = [index for index in fence_indexes if index >= paragraph_end]
    assert before, "the example paragraph must follow a code fence"
    assert after, "the example paragraph must precede a code fence"
    assert section[before[-1]].strip() == "```", (
        "the fence before the example must be a bare closing fence"
    )
    opening_info = section[after[0]].strip()[3:].split()
    assert opening_info and opening_info[0] == "bash", (
        "the fence after the example must carry the bash language identifier"
    )

    # Line style: no trailing whitespace or tabs, and balanced inline code
    # spans in the edited paragraph.
    for index, line in enumerate(section):
        assert line == line.rstrip(), (
            f"subsection line {index + 1} has trailing whitespace"
        )
        assert "\t" not in line, (
            f"subsection line {index + 1} uses a tab character"
        )
    for offset, line in enumerate(section[paragraph_start:paragraph_end]):
        assert line.count("`") % 2 == 0, (
            "inline code spans must be balanced in paragraph line "
            f"{paragraph_start + offset + 1}"
        )
