"""Step 3 tests for Story S3.3.

Verifies convention conformance (GFM rules from
.agent/.aider.conventions/references/github-flavored-markdown.md) for
both updated documents together: each test maps to one Step 3 Must
Support item. Content assertions live in the Step 1/Step 2 suites,
not here.
"""

from pathlib import Path

DOCUMENTS = (Path("docs/implementation_status.md"), Path("docs/tech_stack.md"))


def _load() -> dict[Path, list[str]]:
    return {doc: doc.read_text(encoding="utf-8").splitlines() for doc in DOCUMENTS}


def _inside_fence(lines: list[str]) -> set[int]:
    """Line numbers inside a fenced code block (interior lines only)."""
    fenced: set[int] = set()
    inside = False
    for lineno, line in enumerate(lines, start=1):
        if line.lstrip().startswith("```"):
            inside = not inside
        elif inside:
            fenced.add(lineno)
    return fenced


def _headings(lines: list[str]) -> list[tuple[int, int, str]]:
    """Return (lineno, hash-count, raw line) for each heading line."""
    fenced = _inside_fence(lines)
    found = []
    for lineno, line in enumerate(lines, start=1):
        if lineno in fenced or not line.lstrip().startswith("#"):
            continue
        found.append((lineno, len(line) - len(line.lstrip("#")), line))
    return found


def _setext_underlines(lines: list[str]) -> list[int]:
    """Line numbers of Setext underlines (pure '='/'-' runs directly
    below a non-blank line)."""
    flagged = []
    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or (set(stripped) not in ({"="}, {"-"})):
            continue
        if lineno > 1 and lines[lineno - 2].strip():
            flagged.append(lineno)
    return flagged


def _assert_clean(violations: list[str]) -> None:
    assert not violations, (
        "documentation convention violations found:\n  "
        + "\n  ".join(violations)
    )


def test_both_documents_single_h1_ordered_atx_headings():
    """Must Support 1+2: exactly one H1 per document, levels descend
    without skipping, ATX style only, space after the opening hashes,
    no closing hash sequences, maximum depth H6."""
    violations: list[str] = []
    for doc, lines in _load().items():
        for lineno in _setext_underlines(lines):
            violations.append(f"{doc}:{lineno}: Setext underline; use ATX")
        previous = 0
        for lineno, level, line in _headings(lines):
            where = f"{doc}:{lineno}"
            if level > 6:
                violations.append(f"{where}: heading deeper than H6")
                continue
            rest = line[level:]
            if not rest.startswith(" "):
                violations.append(f"{where}: missing space after hashes")
                continue
            if rest.strip().endswith("#"):
                violations.append(f"{where}: closing hash sequence")
            if previous == 0 and level != 1:
                violations.append(f"{where}: first heading must be H1")
            if previous > 0 and level > previous + 1:
                violations.append(f"{where}: skips from H{previous} to H{level}")
            previous = level
        level_1 = [h for h in _headings(lines) if h[1] == 1]
        if len(level_1) != 1:
            violations.append(f"{doc}: expected exactly one H1, found {len(level_1)}")
    _assert_clean(violations)
