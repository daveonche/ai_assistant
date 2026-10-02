# Github Flavored Markdown Spec

Applies to every `.md` file in this repository. Based on the
[GitHub Flavored Markdown Spec](https://github.github.com/gfm/)
(Version 0.29-gfm, 2019-04-06), a strict superset of CommonMark.
Extensions in use: tables, task lists, strikethrough, extended
autolinks, and the disallowed-raw-HTML filter (tagfilter).

Use these rules as review criteria when creating or reviewing Markdown files.

## Document structure

- Exactly one H1 (`#`) per document; descend heading levels in order without skipping.
- Use ATX headings only (`## Title`). Never use Setext underlines (`===` / `---`).
- Put a blank line before and after every heading, paragraph, list, code block, table, and block quote.
- Separate blocks with a single blank line; extra blank lines add noise, not structure.
- Do not indent body text: 4+ leading spaces turns a line into an indented code block.
- Use spaces, never tabs, for indentation (tabs are treated as 4-space tab stops when computing block structure).
- End files with a single newline; no trailing whitespace on any line.

## Headings

- A space is required after the opening `#`s: `# Title`, not `#Title`.
- No closing `#` sequence; maximum depth is `######` (H6).

## Paragraphs and line breaks

- Be consistent about wrapping lines within a file; soft line breaks render as spaces.
- For a hard line break, end the line with a backslash `\` (preferred) instead of two trailing spaces.
- Neither hard-break syntax works at the very end of a block.

## Lists

- Bullet marker: `-` everywhere. Mixing `-`, `*`, `+` starts separate lists.
- Ordered marker: `1.` style. Rendering follows the first item's number; keep later numbers sequential for readability.
- Exactly one space after the marker (`- item`); `-item` is not a list.
- Nest sublists by indenting to align with the parent item's content (2 spaces for `-`), not a fixed 4.
- Keep lists tight (no blank lines between items) unless an item contains multiple blocks.
- Only a list whose first item starts with `1` may interrupt a paragraph; otherwise precede lists with a blank line.

### Task lists

- `- [ ]` unchecked, `- [x]` checked; one space after the bracket pair before the text.

## Code

- Always use fenced code blocks with backticks; never indented code blocks.
- Put the language identifier as the first word of the info string ` ```python, ```bash, ```markdown ` use ` ```text ` for non-code literals.
- Closing fence: same character, at least as long as the opening fence, no info string.
- If the block contains triple backticks, open with four or more.
- Keep fences unindented (0–3 spaces allowed; 4 makes them content of an indented code block).
- Wrap filenames and file paths in inline code spans (backticks) — e.g., `agent.sh`, `docs/tech_stack.md`. Recommended for readability, not mandatory.

## Tables

- Header row and delimiter row must have the same number of cells, or no table is parsed.
- Use leading and trailing pipes on every row.
- Align columns with colons in the delimiter row: `| :--- |` left, `| :---: |` center, `| ---: |` right.
- Escape literal pipes inside cells as `\|`, including inside code spans.
- A blank line or any block-level element ends the table.

## Block quotes

- Prefix every line with `>`, including blank lines inside the quote (a lone `>` keeps it open).

## Emphasis and strikethrough

- Emphasis `*text*`, strong `**text**`. Prefer `*` over `_`: underscores do not emphasize inside words.
- Strikethrough: `~~text~~` (one or two tildes; three or more is literal).

## Links, images, autolinks

- Inline links: `[text](https://example.com "optional title")`. No space between `]` and `(`.
- Use reference definitions (`[text][label]` + `[label]: url`) only when the same URL repeats; the first definition wins and labels are case-insensitive.
- No whitespace between link text and its label or `[]`.
- Links cannot contain links. Images are links prefixed with `!`; alt text should be plain, descriptive text.
- Bare URLs (`https://…`, `www…`, email addresses) are auto-linked; trailing punctuation is excluded. Use `<https://…>` when you need explicit delimiting.
- Escape brackets that are not meant to be links: `\[foo]`.

## Raw HTML

- Avoid raw HTML; prefer GFM constructs.
- When unavoidable, remember HTML blocks end at the first blank line; keep tags on their own lines with blank lines around them.
- These tags are escaped by the tagfilter even when written literally: `title`, `textarea`, `style`, `xmp`, `iframe`, `noembed`, `noframes`, `script`, `plaintext`.

## Escaping and character references

- Backslash-escape ASCII punctuation only (`\*`, `\_`, `\#`, …). Escapes do not work inside code spans, code blocks, autolinks, or raw HTML.
- HTML entities (`&amp;`, `&#42;`) work outside code constructs but can never stand in for structural characters (emphasis delimiters, list markers, line breaks).
- Write `<` and `&` as `\<`/`&lt;` and `&amp;` in prose to avoid accidental tag or entity parsing.

## Gotchas

- Text immediately followed by a line of `---` parses as an H2 Setext heading, not a paragraph plus thematic break. Always put a blank line before `---`.
- Four leading spaces = indented code block. Watch continuation lines inside list items: indent relative to the item's content, and never 4+ beyond it unintentionally.
- An unclosed fence swallows everything to the end of the document (or container). Balance fences before committing.
- A backtick-fence info string may not contain backticks.
- Changing the bullet character or ordered delimiter (`.` ↔ `)`) mid-list silently starts a second list.
- A table whose delimiter-row cell count differs from the header renders as plain text.
- Link reference definitions cannot interrupt a paragraph; one glued to the preceding paragraph becomes paragraph text.

## Validation

Before committing documentation changes, verify rendering with a GFM-compliant renderer (e.g., cmark-gfm or the GitHub preview) and re-check every construct listed under Gotchas.
