"""Story S1.4 Step 4 — Enable AGENT.md workflow and context management rules.

Verifies the Must Support items of Step 4 from
docs/analysis/S1.4-story-steps.md:
- Creation of an AGENT.md file
- Definition of context management rules (e.g., read-only, drop)
- Definition of workflow instructions for staged execution
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AGENT_MD = REPO_ROOT / ".agent" / "AGENTS.md"


def test_agent_md_file_exists():
    """The AGENT.md file exists in the project (implemented at
    .agent/AGENTS.md) and is non-empty."""
    assert AGENT_MD.is_file(), f"missing AGENT.md file: {AGENT_MD}"
    assert AGENT_MD.read_text(encoding="utf-8").strip(), (
        "AGENT.md must not be empty"
    )


def _headings(text: str) -> list[str]:
    """ATX heading lines of the document."""
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip().startswith("#")
    ]


def test_defines_context_management_rules():
    """The document defines context management rules: a dedicated
    context-management section plus read-only and drop command
    definitions."""
    text = AGENT_MD.read_text(encoding="utf-8")
    context_headings = [
        h for h in _headings(text)
        if "context" in h.lower() and "management" in h.lower()
    ]
    assert context_headings, (
        "AGENT.md must have a section dedicated to context management"
    )
    assert "/read-only" in text, (
        "context management rules must define the read-only command"
    )
    assert "/drop" in text, (
        "context management rules must define the drop command"
    )


def test_defines_staged_execution_workflow_instructions():
    """The document defines workflow instructions for staged
    execution: a workflow section with [STEP n] stages, [STOP]
    points, and wait-for-user-input guidance."""
    text = AGENT_MD.read_text(encoding="utf-8")
    workflow_headings = [
        h for h in _headings(text) if "workflow" in h.lower()
    ]
    assert workflow_headings, (
        "AGENT.md must have a section dedicated to workflow instructions"
    )
    assert "[STEP" in text, (
        "workflow instructions must define staged execution steps"
    )
    assert "[STOP" in text, (
        "workflow instructions must define stop points that pause "
        "staged execution"
    )
    assert "wait" in text.lower(), (
        "workflow instructions must instruct the assistant to wait for "
        "user input at stop points"
    )
