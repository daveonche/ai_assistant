"""Tests for Story S4.2 Step 1: framework conventions delta files.

Name-agnostic by design: nothing here names a framework, a spec
document, or a directory. Packs are discovered structurally (a pack is
a .agent/specs/ subdirectory containing SKILL.md); flat delta files are
discovered by content signature (the file declares delta
conventions/guidance). The only literal filenames are the standard's
own structural markers (SKILL.md, SKILL.meta.md) — the convention's
mechanism, not specific targets. The canonical layout these tests
enforce is documented in
.agent/specs/references/spec-pack-standard.md.
"""

import re
from pathlib import Path

SPECS_DIR = Path(".agent", "specs")


def _file_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalized(path: Path) -> str:
    """Whitespace-normalized lowercase text, so line wraps inside a
    sentence cannot hide a phrase from the assertions."""
    return " ".join(_file_text(path).split()).lower()


def _pack_skill_files() -> tuple[Path, ...]:
    """A pack is any .agent/specs/ subdirectory containing SKILL.md."""
    return tuple(sorted(SPECS_DIR.glob("*/SKILL.md")))


def _is_delta_declaration(text: str) -> bool:
    lowered = " ".join(text.split()).lower()
    return "delta conventions" in lowered or "delta guidance" in lowered


def _flat_delta_files() -> tuple[Path, ...]:
    """Flat spec files declaring themselves framework delta
    conventions, by content signature (no name lists)."""
    return tuple(
        path
        for path in sorted(SPECS_DIR.glob("*.md"))
        if _is_delta_declaration(_file_text(path))
    )


PACK_SKILL_FILES = _pack_skill_files()
DELTA_FILES = PACK_SKILL_FILES + _flat_delta_files()
DOC_FILES = DELTA_FILES + tuple(
    skill.parent / "SKILL.meta.md"
    for skill in PACK_SKILL_FILES
    if (skill.parent / "SKILL.meta.md").is_file()
)


def test_delta_files_discovered():
    """Sanity: discovery finds at least one delta-conventions file;
    otherwise the structural/content discovery above is broken."""
    assert DELTA_FILES, "no framework delta-conventions files discovered"


def test_every_pack_skill_md_has_meta():
    """Pack standard: each SKILL.md has a sibling SKILL.meta.md, the
    same convention as .agent/workflows/**/SKILL.meta.md."""
    missing = [
        str(skill.parent / "SKILL.meta.md")
        for skill in PACK_SKILL_FILES
        if not (skill.parent / "SKILL.meta.md").is_file()
    ]
    assert not missing, f"SKILL.md files missing SKILL.meta.md: {missing}"


def test_pack_skill_files_carry_standard_markers():
    """Pack standard: each SKILL.md carries the Convention Check
    Reminder line and its sentinel comment."""
    for skill in PACK_SKILL_FILES:
        text = _file_text(skill)
        assert "Convention Check Reminder" in text, (
            f"{skill} missing Convention Check Reminder line"
        )
        assert "<!-- sentinel: specs/" in text, f"{skill} missing sentinel"


def test_files_declare_delta_only_scope():
    for path in DELTA_FILES:
        normalized = _normalized(path)
        assert "**scope:**" in normalized or "## scope" in normalized, (
            f"{path} missing Scope section"
        )
        assert "do not add general" in normalized, (
            f"{path} missing exclusion of general framework knowledge"
        )
        assert "api references" in normalized, (
            f"{path} missing exclusion of API references"
        )
        assert "tutorials" in normalized, f"{path} missing exclusion of tutorials"


def test_files_state_version_guidance_and_fallback():
    """Every delta-conventions file must state how version-specific
    guidance is handled and that the assistant continues on general
    knowledge when referenced material is absent; the mechanism
    (version directories, upgrade notes, ...) is pack-specific."""
    for path in DELTA_FILES:
        normalized = _normalized(path)
        assert "version-specific" in normalized, (
            f"{path} does not state how version-specific guidance is handled"
        )
        assert re.search(r"general( \w+)? knowledge", normalized), (
            f"{path} does not state the assistant continues on general "
            "knowledge when referenced material is absent"
        )


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


def _leading_spaces(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _cells(row: str) -> list[str]:
    """Split a stripped table row into cells, honoring backslash escapes."""
    inner = row[1:-1]
    cells, current, escaped = [], "", False
    for char in inner:
        if escaped:
            current += char
            escaped = False
        elif char == "\\":
            escaped = True
        elif char == "|":
            cells.append(current)
            current = ""
        else:
            current += char
    cells.append(current)
    return cells


def _table_blocks(lines: list[str], fenced: set[int]) -> list[list[str]]:
    blocks: list[list[str]] = []
    current: list[str] = []
    for lineno, line in enumerate(lines, start=1):
        if lineno in fenced:
            continue
        if line.strip().startswith("|"):
            current.append(line)
        elif current:
            blocks.append(current)
            current = []
    if current:
        blocks.append(current)
    return blocks


def test_files_follow_markdown_conventions():
    """Must Support: every discovered spec document (delta files and
    pack SKILL.meta.md files) follows the project's documentation
    conventions (GFM rules from
    .agent/specs/references/github-flavored-markdown.md):
    single ordered ATX headings, '-' list markers, blank lines around
    headings/lists/tables, no tabs or 4+ leading spaces, GFM table
    rules, single final newline, no trailing whitespace. Indented
    continuation lines inside a list item count as list content (GFM
    lazy continuation), not as the end of the list, and are exempt from
    the indented-code-block check."""
    violations: list[str] = []
    for doc in DOC_FILES:
        text = _file_text(doc)
        lines = text.splitlines()
        fenced = _inside_fence(lines)
        heading_linenos = {h[0] for h in _headings(lines)}

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

        in_list = in_table = False
        for lineno, line in enumerate(lines, start=1):
            if lineno in fenced:
                continue
            stripped = line.strip()
            blank = not stripped
            prev = lines[lineno - 2].strip() if lineno > 1 else ""
            nxt = lines[lineno].strip() if lineno < len(lines) else ""
            where = f"{doc}:{lineno}"
            is_item = (not blank) and (
                stripped.startswith("- ")
                or (in_list and _leading_spaces(line) > 0)
            )
            if "\t" in line:
                violations.append(f"{where}: tab character; use spaces")
            if not blank and _leading_spaces(line) >= 4 and not is_item:
                violations.append(
                    f"{where}: 4+ leading spaces render as an indented "
                    "code block; use a fenced block instead"
                )
            if blank and not prev:
                violations.append(f"{where}: extra blank line")
            if lineno in heading_linenos:
                if prev:
                    violations.append(f"{where}: missing blank line before heading")
                if nxt:
                    violations.append(f"{where}: missing blank line after heading")
            is_table_row = (not blank) and stripped.startswith("|")
            if is_item and not in_list and prev:
                violations.append(f"{where}: missing blank line before list")
            if not is_item and in_list and stripped:
                violations.append(f"{where}: missing blank line after list")
            if is_table_row and not in_table and prev:
                violations.append(f"{where}: missing blank line before table")
            if not is_table_row and in_table and stripped:
                violations.append(f"{where}: missing blank line after table")
            in_list, in_table = is_item, is_table_row
            if not stripped:
                continue
            if stripped.startswith(("* ", "+ ")):
                violations.append(
                    f"{where}: bullet marker {stripped[0]!r}; use '-' only"
                )
            if stripped[0].isdigit() and ")" in stripped.split(" ", 1)[0]:
                violations.append(
                    f"{where}: ordered list uses ')'; use '1.' style"
                )
            if (
                stripped.startswith("-")
                and not stripped.startswith("- ")
                and set(stripped.replace(" ", "")) != {"-"}
            ):
                violations.append(
                    f"{where}: needs exactly one space after '-' "
                    "('-item' is not a list item)"
                )
            if stripped.startswith(("- [ ]", "- [x]")):
                rest = stripped[5:]
                if rest and not rest.startswith(" "):
                    violations.append(
                        f"{where}: missing space after task-list checkbox"
                    )
                elif rest.startswith("  "):
                    violations.append(
                        f"{where}: multiple spaces after task-list checkbox"
                    )

        for block in _table_blocks(lines, fenced):
            rows = [row.strip() for row in block]
            for row in rows:
                if not (row.startswith("|") and row.endswith("|")):
                    violations.append(
                        f"{doc}: table row missing leading/trailing pipe: {row[:40]!r}"
                    )
            if len(rows) < 2 or not all(
                set(cell.strip()) <= {":", "-"} and "-" in cell
                for cell in _cells(rows[1])
            ):
                violations.append(
                    f"{doc}: table lacks a delimiter row: {rows[0][:40]!r}"
                )
                continue
            header_cells = len(_cells(rows[0]))
            if header_cells != len(_cells(rows[1])):
                violations.append(
                    f"{doc}: table header/delimiter cell count mismatch: {rows[0][:40]!r}"
                )
            for row in rows[2:]:
                if len(_cells(row)) != header_cells:
                    violations.append(
                        f"{doc}: table row cell count differs from header: {row[:40]!r}"
                    )

        if not text.endswith("\n"):
            violations.append(f"{doc}: missing final newline")
        elif text.endswith("\n\n"):
            violations.append(f"{doc}: more than one final newline")
        for lineno, line in enumerate(lines, start=1):
            if line != line.rstrip(" \t"):
                violations.append(f"{doc}:{lineno}: trailing whitespace")
    _assert_clean(violations)
