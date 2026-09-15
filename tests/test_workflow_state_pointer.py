"""Guard: docs/workflow_state.md must stay a pointer, not a log.

Enforces the Session State Persistence rules from .agent/AGENTS.md: the
state file stays short, the "Last completed" line stays a one-line
summary of only the most recent step, and the file never describes the
context window. Per-step details live in git commit messages and the
test files; a resuming session only needs the prescriptive
"Reload to resume" list, which cannot go stale the way a snapshot of
loaded files does after drops or /clear.
"""

from pathlib import Path

STATE_FILE = Path("docs/workflow_state.md")
MAX_FILE_LINES = 15
MAX_LAST_COMPLETED_CHARS = 400
SNAPSHOT_PREFIXES = (
    "- Files in context:",
    "- droppable",
    "- summaries only:",
)


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


def test_state_file_prescribes_reload_not_context_snapshot():
    """The state file records what to reload, never what was loaded.

    Regression guard: a descriptive "Files in context"/"droppable"
    snapshot is stale the moment files are dropped or the session is
    cleared, and an AI resuming from it wastes effort reconciling the
    mismatch. Only the prescriptive "- Reload to resume:" line is
    allowed; it cannot go stale the way a snapshot does.
    """
    lines = _state_lines()
    if lines is None:
        return  # nothing to guard while the state file does not exist
    snapshot_lines = [l for l in lines if l.startswith(SNAPSHOT_PREFIXES)]
    assert not snapshot_lines, (
        f"{STATE_FILE} must not describe the context window; found "
        f"{snapshot_lines[0].split(':')[0]!r}. Record only the minimal "
        "'- Reload to resume:' list — drops and adds never require a "
        "state-file rewrite"
    )
    reload_lines = [l for l in lines if l.startswith("- Reload to resume:")]
    assert len(reload_lines) <= 1, \
        "at most one '- Reload to resume:' line is expected"
    if not any(l.startswith("- Command:") for l in lines):
        return  # Active Workflow section cleared after workflow completion
    assert reload_lines, (
        f"{STATE_FILE} must contain a '- Reload to resume:' line listing "
        "the minimal files for the next action"
    )
