"""Story S1.6 Step 1 — pipeline definition exists and runs automatically.

Verifies the Must Support item: "A pipeline definition at
.github/workflows/ci.yml that runs automatically on every push and pull
request".
"""

import re
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


def test_pipeline_permissions_explicit_and_read_only():
    workflow = _load_workflow()
    assert "permissions" in workflow, \
        "permissions block must be explicit (an unset block is a security finding)"
    assert workflow["permissions"] == {"contents": "read"}, \
        "pipeline permissions must be exactly contents: read (minimal, read-only)"
    jobs = workflow.get("jobs") or {}
    assert jobs, "workflow must define at least one job"
    for name, job in jobs.items():
        if isinstance(job, dict) and "permissions" in job:
            assert job["permissions"] == {"contents": "read"}, \
                f"job '{name}' must not grant permissions beyond read-only contents"


def test_action_references_pinned_to_full_sha_with_version_comment():
    text = CI_WORKFLOW.read_text(encoding="utf-8")
    references = []
    for line in text.splitlines():
        match = re.match(r"^\s*uses:\s*(\S+)(?:\s+(#.*))?$", line)
        if match:
            references.append((match.group(1), match.group(2)))
    assert references, "workflow must reference at least one reusable action"
    for value, comment in references:
        assert re.fullmatch(r"\S+@[0-9a-f]{40}", value), (
            f"'{value}' must be pinned to a full-length 40-character commit SHA "
            "(immutable identifier); mutable tags or branches are not allowed"
        )
        assert comment and re.match(r"#\s*v\d", comment), (
            f"'{value}' must carry a version comment recording the pinned "
            "version (e.g., '# v6.1.0')"
        )
