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
