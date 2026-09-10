"""Story S1.6 Step 2 — launcher source code validation in the pipeline.

Verifies the Must Support items: "Automated syntax and style validation of
.agent/ai_assistant.py on every pipeline run", "Validation performed with the
language's built-in checking capability alone, requiring no additional
packages", and "A detected validation error marks the overall pipeline run as
failed".
"""

from pathlib import Path

import yaml

CI_WORKFLOW = Path(".github/workflows/ci.yml")
LAUNCHER = ".agent/ai_assistant.py"
EXPECTED_CHECK = f"python3 -m py_compile {LAUNCHER}"


def _load_workflow() -> dict:
    data = yaml.safe_load(CI_WORKFLOW.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "workflow must parse as a YAML mapping"
    return data


def _validate_job() -> dict:
    jobs = _load_workflow().get("jobs") or {}
    job = jobs.get("validate")
    assert isinstance(job, dict), "workflow must define a 'validate' job"
    return job


def _launcher_validation_steps() -> list[dict]:
    steps = _validate_job().get("steps") or []
    return [
        s for s in steps
        if isinstance(s, dict) and LAUNCHER in (s.get("run") or "")
    ]


def test_launcher_syntax_validation_is_dedicated_pipeline_stage():
    job = _validate_job()
    assert not job.get("if"), \
        "the validate job must run on every pipeline run (no 'if' condition)"
    steps = _launcher_validation_steps()
    assert len(steps) == 1, \
        "exactly one validate-job step must target the launcher"
    step = steps[0]
    assert step.get("name"), \
        "the launcher validation step must be named so a failure is easy " \
        "to attribute in the run summary"
    assert not step.get("if"), \
        "the launcher validation step must run on every pipeline run"
    assert (step.get("run") or "").strip() == EXPECTED_CHECK, (
        "launcher validation must be its own dedicated stage running exactly "
        f"'{EXPECTED_CHECK}'; other validations must not share the step"
    )
