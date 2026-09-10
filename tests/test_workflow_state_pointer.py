"""Guard: docs/workflow_state.md must stay a pointer, not a log.

Enforces the Session State Persistence rules from .agent/AGENTS.md: the
state file stays short, and the "Last completed" line stays a one-line
summary of only the most recent step. Per-step details live in git commit
messages and the test files, never accumulated in the state file.
"""

from pathlib import Path

STATE_FILE = Path("docs/workflow_state.md")
MAX_FILE_LINES = 15
MAX_LAST_COMPLETED_CHARS = 400


def _state_lines() -> list[str] | None:
    if not STATE_FILE.is_file():
        return None
    return STATE_FILE.read_text(encoding="utf-8").splitlines()


def test_workflow_state_file_stays_short():
    lines = _state_lines()
    if lines is None:
        return  # nothing to guard while the state file does not exist
    assert len(lines) <= MAX_FILE_LINES, (
        f"{STATE_FILE} has {len(lines)} lines (max {MAX_FILE_LINES}); "
        "the state file is a pointer, not a log — condense it"
    )


def test_last_completed_line_stays_a_one_line_summary():
    lines = _state_lines()
    if lines is None:
        return  # nothing to guard while the state file does not exist
    matches = [l for l in lines if l.startswith("- Last completed:")]
    assert len(matches) <= 1, \
        "at most one '- Last completed:' line is expected"
    if not matches:
        return  # Active Workflow section cleared after workflow completion
    line = matches[0]
    assert len(line) <= MAX_LAST_COMPLETED_CHARS, (
        f"'- Last completed:' is {len(line)} characters "
        f"(max {MAX_LAST_COMPLETED_CHARS}); it must summarize only the most "
        "recent step — never accumulate per-step history"
    )
