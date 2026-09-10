"""Story S1.6 Step 1 — pipeline definition exists and runs automatically.

Verifies the Must Support item: "A pipeline definition at
.github/workflows/ci.yml that runs automatically on every push and pull
request".
"""

from pathlib import Path

import yaml

CI_WORKFLOW = Path(".github/workflows/ci.yml")


def _load_workflow() -> dict:
    data = yaml.safe_load(CI_WORKFLOW.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "workflow must parse as a YAML mapping"
    return data


def _triggers(workflow: dict) -> dict:
    # PyYAML parses the bare `on:` key as boolean True (YAML 1.1 quirk)
    return workflow.get("on") or workflow.get(True) or {}


def test_pipeline_definition_exists_and_runs_on_push_and_pull_request():
    assert CI_WORKFLOW.is_file(), ".github/workflows/ci.yml must exist"
    triggers = _triggers(_load_workflow())
    assert "push" in triggers, "pipeline must run automatically on push"
    assert "pull_request" in triggers, "pipeline must run automatically on pull requests"
    assert triggers["push"] in (None, {}), \
        "push trigger must be unfiltered so EVERY push runs the pipeline"
