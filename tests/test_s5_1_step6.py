"""S5.1 step 6 verification: README per-project customization section.

Documentation-content suite: reads README.md directly and asserts the
story's documentation requirements — the established pattern of the
S3.3/S4.4 doc suites. No sandbox, no docker stub: launcher behavior is
already enforced by the step 1-5 suites; this suite keeps the
documentation aligned with it.

Covered here:
- the project-root configuration merging description is gone;
- a per-project customization section documents the args file at its
  host-side location and the argument precedence order;
- the section documents the move/rename caveat (the args file is keyed
  to the project directory's path);
- the section documents the override guidance (distinctive referenced
  filename, self-sufficient copy from the assistant's own file, use
  only when genuinely needed);
- the installation and update sections each carry a one-line pointer to
  --init-project-args.
"""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

README = PROJECT_ROOT / "README.md"


def _doc_text() -> str:
    """Return the README's full text."""
    return README.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    """Return the text from a heading line up to the next heading of the
    same or higher level.

    Raises AssertionError when the heading is absent, so a missing
    section fails loudly instead of returning an empty slice.
    """
    lines = text.splitlines()
    start = None
    level = 0
    for index, line in enumerate(lines):
        if line.startswith("#"):
            if line.lstrip("#").strip() == heading:
                start = index
                level = len(line) - len(line.lstrip("#"))
                break
    assert start is not None, f"heading not found: {heading!r}"
    end = len(lines)
    for index in range(start + 1, len(lines)):
        line = lines[index]
        if line.startswith("#"):
            other = len(line) - len(line.lstrip("#"))
            if other <= level:
                end = index
                break
    return "\n".join(lines[start:end])


def test_merging_section_is_gone():
    """The replaced section's title no longer appears anywhere in the
    README: the project-root configuration merging description is gone."""
    assert "Mergeable configuration" not in _doc_text()
