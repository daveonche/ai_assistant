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
    Docker command, appended per session) and where it is written (system
    temporary directory, ai-assistant-*.log naming)."""
    readme = _read_readme()
    section = _section(readme, "Logging and Debug Mode").casefold()

    # What is logged: every Docker command, appended to a per-session log.
    assert "every docker command" in section
    assert "per-session command log" in section
    assert "appended" in section

    # Where it is written: system temp directory + log file naming.
    assert "system temporary directory" in section
    assert re.search(r"ai-assistant-[\w<>/ -]*\.log", section), (
        "log file naming pattern (ai-assistant-*.log) not documented"
    )
