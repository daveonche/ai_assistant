"""S1.8 Step 5: logging and debug documentation.

Must Support verified:
- Documentation of what is logged and where it is written (this test).
- Documentation of how to enable debug mode and what additional output
  appears (second test in this file).

Static content checks against README.md, following the README-section
testing pattern of tests/test_s1_2_step4.py. Behavioral accuracy of the
documented outputs is not re-tested here — it is already covered
end-to-end by the S1.8 Step 1-3 suites and tests/test_s1_3_step2.py.
"""

from __future__ import annotations

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _read_readme() -> str:
    return (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    """Return the section under the given H2 heading, up to the next H2."""
    start = text.index(f"## {heading}")
    next_heading = text.find("\n## ", start + 1)
    return text[start : next_heading if next_heading != -1 else len(text)]


def test_logging_section_documents_what_and_where():
    """The Logging and Debug Mode section documents what is logged (every
    Docker and git command, appended per session) and where it is written
    (the user's cache directory, ai-assistant-*.log naming)."""
    readme = _read_readme()
    section = _section(readme, "Logging and Debug Mode").casefold()

    # What is logged: every Docker and git command, appended to a
    # per-session log.
    assert "every docker and git command" in section
    assert "per-session command log" in section
    assert "appended" in section

    # Where it is written: the user's cache directory + log file naming.
    assert "user's cache directory" in section
    assert re.search(r"ai-assistant-[\w<>/ -]*\.log", section), (
        "log file naming pattern (ai-assistant-*.log) not documented"
    )


def _subsection(text: str, heading: str) -> str:
    """Return the content under an H3 heading, up to the next heading
    (H3 or H2, whichever comes first)."""
    start = text.index(f"### {heading}")
    next_h3 = text.find("\n### ", start + 1)
    next_h2 = text.find("\n## ", start + 1)
    candidates = [c for c in (next_h3, next_h2) if c != -1]
    end = min(candidates) if candidates else len(text)
    return text[start:end]


def test_debug_mode_documentation_matches_requirements():
    """The Enabling Debug Mode subsection documents the --debug flag with
    its -x short form and the enumerated additional stderr output; the
    Normal Mode subsection documents the no-debug contrast."""
    readme = _read_readme()
    enabling = _subsection(readme, "Enabling Debug Mode").casefold()
    normal = _subsection(readme, "Normal Mode").casefold()

    # How to enable debug mode: the flag and its short form.
    assert "--debug" in enabling
    assert "-x" in enabling

    # What additional output appears: enumerated stderr output.
    assert "stderr" in enabling
    assert "each docker and git command" in enabling
    assert "command log path" in enabling
    assert "last 10" in enabling

    # The normal-mode contrast: spinner feedback only, commands still
    # recorded.
    assert "spinner" in normal
    assert "command log" in normal
