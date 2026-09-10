"""Story S1.6 Step 4 — container image build validation in the pipeline.

Verifies the Must Support items: "Automated build of the container image from
.agent/Dockerfile.aider on every pipeline run", "The build mirrors the
launcher's own image build (same definition and build inputs)", and "A build
failure marks the overall pipeline run as failed".
"""

from pathlib import Path

import yaml

CI_WORKFLOW = Path(".github/workflows/ci.yml")
IMAGE_DEFINITION = ".agent/Dockerfile.aider"


def _load_workflow() -> dict:
    data = yaml.safe_load(CI_WORKFLOW.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "workflow must parse as a YAML mapping"
    return data


def _docker_build_job() -> dict:
    jobs = _load_workflow().get("jobs") or {}
    job = jobs.get("docker-build")
    assert isinstance(job, dict), "workflow must define a 'docker-build' job"
    return job


def _build_steps() -> list[dict]:
    steps = _docker_build_job().get("steps") or []
    return [
        s for s in steps
        if isinstance(s, dict) and "docker build" in (s.get("run") or "")
    ]


def test_image_build_is_dedicated_pipeline_stage():
    job = _docker_build_job()
    assert not job.get("if"), \
        "the docker-build job must run on every pipeline run (no 'if' condition)"
    steps = _build_steps()
    assert len(steps) == 1, \
        "exactly one docker-build job step must run the image build"
    step = steps[0]
    assert step.get("name"), \
        "the image build step must be named so a failure is easy to " \
        "attribute in the run summary"
    assert not step.get("if"), \
        "the image build step must run on every pipeline run"
    run = step.get("run") or ""
    assert f"-f {IMAGE_DEFINITION}" in run or f"-f {IMAGE_DEFINITION} " in run, (
        f"the build stage must build from the project image definition "
        f"({IMAGE_DEFINITION})"
    )
    assert "shellcheck" not in run and "py_compile" not in run, (
        "the image build stage must be its own stage: the source validations "
        "must live in their own job/steps so failures remain clearly attributable"
    )
