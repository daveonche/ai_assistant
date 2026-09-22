"""S3.2 Step 1 verification: release tag guard trigger and pinned reference."""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "ci.yml"
INSTALLER_PATH = REPO_ROOT / "scripts" / "install.sh"
GUARD_JOB = "release-tag-guard"


def _load_workflow() -> dict:
    assert WORKFLOW_PATH.is_file(), "missing .github/workflows/ci.yml"
    workflow = yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))
    assert isinstance(workflow, dict), "ci.yml is not a mapping"
    return workflow


def _workflow_triggers(workflow: dict) -> dict:
    # PyYAML implements YAML 1.1: an unquoted `on:` key parses as True.
    for key in ("on", True):
        if key in workflow:
            triggers = workflow[key]
            assert isinstance(triggers, dict), "ci.yml `on:` is not a mapping"
            return triggers
    raise AssertionError("ci.yml defines no triggers")


def _guard_job(workflow: dict) -> dict:
    jobs = workflow.get("jobs") or {}
    assert isinstance(jobs, dict), "ci.yml `jobs:` is not a mapping"
    assert GUARD_JOB in jobs, (
        f"missing '{GUARD_JOB}' job in .github/workflows/ci.yml"
    )
    return jobs[GUARD_JOB]


def _workflow_tag_patterns(triggers: dict) -> list[str]:
    push = triggers.get("push")
    if not isinstance(push, dict):
        return []
    return [str(tag) for tag in (push.get("tags") or [])]


def _default_ref() -> str:
    for line in INSTALLER_PATH.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        # The declaration is `readonly DEFAULT_REF="v1.0.13"`; match the
        # assignment wherever it appears on the line.
        if "DEFAULT_REF=" in stripped and not stripped.startswith("#"):
            value = stripped.split("DEFAULT_REF=", 1)[1]
            return value.strip().strip("\"'")
    raise AssertionError("scripts/install.sh does not define DEFAULT_REF")


def _run_step_scripts(job: dict) -> list[str]:
    steps = job.get("steps") or []
    return [
        step["run"]
        for step in steps
        if isinstance(step, dict) and "run" in step
    ]


def test_guard_job_triggers_on_version_tag_pushes():
    workflow = _load_workflow()
    job = _guard_job(workflow)
    patterns = _workflow_tag_patterns(_workflow_triggers(workflow))
    workflow_level = any("v*" in pattern for pattern in patterns)
    condition = str(job.get("if") or "")
    job_level = "refs/tags/" in condition and "v" in condition
    assert workflow_level or job_level, (
        "release-tag-guard is not triggered by version-tag pushes: "
        f"push tags={patterns!r}, job if={condition!r}"
    )


def test_guard_job_compares_pushed_tag_to_pinned_reference():
    workflow = _load_workflow()
    job = _guard_job(workflow)
    pinned = _default_ref()
    assert pinned.startswith("v"), (
        f"pinned DEFAULT_REF {pinned!r} is not a version tag"
    )
    scripts = _run_step_scripts(job)
    assert scripts, "release-tag-guard job defines no run steps"
    comparators = [s for s in scripts if "DEFAULT_REF" in s]
    assert comparators, (
        "no release-tag-guard run step references DEFAULT_REF "
        "from scripts/install.sh"
    )
    assert any(
        "GITHUB_REF_NAME" in s or "refs/tags/" in s for s in comparators
    ), "guard step does not read the pushed tag reference"
    assert any("exit 1" in s for s in comparators), (
        "guard step does not fail the pipeline when the tag disagrees "
        "with the pinned reference"
    )


def test_pinned_reference_matches_sprint_3_pin():
    # S3.1 verified every location pins the same ref; the guard must
    # enforce this exact value, so a silent pin change breaks this check.
    assert _default_ref() == "v1.0.13"
