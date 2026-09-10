"""Story S1.6 Step 4 — container image build validation in the pipeline.

Verifies the Must Support items: "Automated build of the container image from
.agent/Dockerfile.aider on every pipeline run", "The build mirrors the
launcher's own image build (same definition and build inputs)", and "A build
failure marks the overall pipeline run as failed".
"""

import shlex
from pathlib import Path

import yaml

CI_WORKFLOW = Path(".github/workflows/ci.yml")
IMAGE_DEFINITION = ".agent/Dockerfile.aider"
LAUNCHER = Path(".agent/ai_assistant.py")


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


def test_ci_build_mirrors_launcher_build_inputs():
    steps = _build_steps()
    assert steps, "an image build step must exist"
    step = steps[0]
    run = step.get("run") or ""
    tokens = shlex.split(run)

    # Same definition: -f .agent/Dockerfile.aider
    assert "-f" in tokens, "the CI build must select the image definition with -f"
    assert tokens[tokens.index("-f") + 1] == IMAGE_DEFINITION, (
        f"the CI build must use the same image definition as the launcher "
        f"({IMAGE_DEFINITION})"
    )

    # Same context: trailing positional argument .agent
    assert tokens[-1] == ".agent", (
        "the CI build context must be the same directory the launcher uses "
        "(.agent, the image definition's own directory)"
    )

    # Same flag: --progress=plain
    assert "--progress=plain" in tokens, (
        "the CI build must pass --progress=plain like the launcher's build"
    )

    # Same build input env: DOCKER_BUILDKIT=1
    env = step.get("env") or {}
    assert env.get("DOCKER_BUILDKIT") == "1", (
        "the CI build must set DOCKER_BUILDKIT=1 like the launcher's build"
    )

    # Launcher cross-check: build_image() must still declare these same
    # inputs, so a launcher-side change forces re-verification of the mirror.
    source = LAUNCHER.read_text(encoding="utf-8")
    assert '"--progress=plain"' in source, (
        "launcher build_image() must still build with --progress=plain"
    )
    assert 'env["DOCKER_BUILDKIT"] = "1"' in source, (
        "launcher build_image() must still set DOCKER_BUILDKIT=1"
    )
    assert 'AGENT_DIR / "Dockerfile.aider"' in source, (
        "launcher must still build from AGENT_DIR / Dockerfile.aider "
        "(the .agent image definition)"
    )
    assert "build_image(dockerfile_path, AGENT_DIR" in source, (
        "launcher must still use AGENT_DIR (.agent) as the build context"
    )


def test_image_build_failure_fails_overall_run():
    job = _docker_build_job()
    assert not job.get("continue-on-error"), \
        "the docker-build job must not suppress failures (continue-on-error)"
    steps = _build_steps()
    assert steps, "an image build step must exist"
    step = steps[0]
    assert step.get("continue-on-error") not in (True, "true"), (
        "the image build step must not suppress failures "
        "(continue-on-error); a failed build must fail the run"
    )
    run = step.get("run") or ""
    for pattern in ("|| true", "|| exit 0", "; true", "&& true"):
        assert pattern not in run, (
            f"build command must not swallow errors (found '{pattern}'); "
            "a build failure must mark the overall run as failed"
        )
