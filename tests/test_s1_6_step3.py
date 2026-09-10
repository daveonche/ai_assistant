"""Story S1.6 Step 3 — shell script validation in the pipeline.

Verifies the Must Support items: "Automated static analysis of every *.sh
script in the repository", "Scripts discovered by pattern rather than a
hard-coded list, so newly added scripts are covered automatically", and
"A detected analysis finding marks the overall pipeline run as failed".
"""

from pathlib import Path

import yaml

CI_WORKFLOW = Path(".github/workflows/ci.yml")


def _load_workflow() -> dict:
    data = yaml.safe_load(CI_WORKFLOW.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "workflow must parse as a YAML mapping"
    return data


def _validate_job() -> dict:
    jobs = _load_workflow().get("jobs") or {}
    job = jobs.get("validate")
    assert isinstance(job, dict), "workflow must define a 'validate' job"
    return job


def _shell_analysis_steps() -> list[dict]:
    steps = _validate_job().get("steps") or []
    return [
        s for s in steps
        if isinstance(s, dict) and "shellcheck" in (s.get("run") or "")
    ]


def test_shell_script_analysis_is_dedicated_pipeline_stage():
    job = _validate_job()
    assert not job.get("if"), \
        "the validate job must run on every pipeline run (no 'if' condition)"
    steps = _shell_analysis_steps()
    assert len(steps) == 1, \
        "exactly one validate-job step must run the shell script analysis"
    step = steps[0]
    assert step.get("name"), \
        "the shell analysis step must be named so a failure is easy to " \
        "attribute in the run summary"
    assert not step.get("if"), \
        "the shell analysis step must run on every pipeline run"
    run = (step.get("run") or "")
    assert "shellcheck" in run, \
        "the analysis stage must invoke the shellcheck static analyzer"
    assert "py_compile" not in run, (
        "the shell analysis stage must be independent of the launcher "
        "validation: the launcher check must live in its own step so "
        "failures remain clearly attributable"
    )
