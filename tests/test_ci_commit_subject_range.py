"""CI commit-subject gate — every pushed commit is validated.

Verifies the Must Support item: "A non-conforming commit subject buried
under later commits (e.g. committed with --no-verify) still fails CI":
the validate job walks the full range of commits a push introduces with
the commit-msg hook instead of checking only the tip.

The launcher and shell-script validation stages are covered by
tests/test_s1_6_step2.py and tests/test_s1_6_step3.py; the hook's
subject format and edit-block scan are covered by
tests/test_commit_msg_hook.py and tests/test_commit_msg_hook_body_scan.py.
"""

from pathlib import Path

import yaml

CI_WORKFLOW = Path(".github/workflows/ci.yml")
HOOK_INVOCATION = "bash .githooks/commit-msg"


def _load_workflow() -> dict:
    data = yaml.safe_load(CI_WORKFLOW.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "workflow must parse as a YAML mapping"
    return data


def _validate_job() -> dict:
    jobs = _load_workflow().get("jobs") or {}
    job = jobs.get("validate")
    assert isinstance(job, dict), "workflow must define a 'validate' job"
    return job


def _hook_step() -> dict:
    steps = _validate_job().get("steps") or []
    matching = [
        s for s in steps
        if isinstance(s, dict) and HOOK_INVOCATION in (s.get("run") or "")
    ]
    assert len(matching) == 1, \
        "exactly one validate-job step must run the commit-msg hook"
    return matching[0]


def test_hook_stage_is_dedicated_and_named():
    job = _validate_job()
    assert not job.get("if"), \
        "the validate job must run on every pipeline run (no 'if' condition)"
    step = _hook_step()
    assert step.get("name"), \
        "the commit-subject validation step must be named so a failure is " \
        "easy to attribute in the run summary"
    assert not step.get("if"), \
        "the commit-subject validation step must run on every pipeline run"


def test_validate_checkout_fetches_history_for_the_range():
    steps = _validate_job().get("steps") or []
    checkout = steps[0]
    assert "checkout" in (checkout.get("name") or "").casefold(), \
        "the first validate-job step must be the checkout"
    assert (checkout.get("with") or {}).get("fetch-depth") == 0, (
        "walking the pushed commit range requires full history: the "
        "validate job's checkout must set fetch-depth: 0"
    )


def test_push_events_validate_every_introduced_commit():
    run = _hook_step().get("run") or ""
    assert "github.event.before" in run, (
        "the pushed range base must come from the push event's before SHA"
    )
    assert "github.event.after" in run, (
        "the pushed range tip must come from the push event's after SHA"
    )
    assert "rev-list" in run, (
        "the pushed range must be enumerated with git rev-list so every "
        "introduced commit is validated, not only the tip"
    )


def test_new_branch_push_falls_back_to_tip_validation():
    run = _hook_step().get("run") or ""
    assert "^0+$" in run, (
        "a new-branch push (all-zero before SHA) has no base commit and "
        "must fall back to validating the tip"
    )


def test_unresolvable_push_base_fails_closed():
    run = _hook_step().get("run") or ""
    assert "cat-file" in run, (
        "an unresolvable push base (force push) must be detected explicitly"
    )
    assert "exit 1" in run, (
        "an unresolvable push base must fail the run instead of silently "
        "skipping the range validation"
    )


def test_range_validation_failure_fails_overall_run():
    job = _validate_job()
    assert not job.get("continue-on-error"), \
        "the validate job must not suppress failures (continue-on-error)"
    run = _hook_step().get("run") or ""
    for pattern in ("|| true", "|| exit 0", "; true", "&& true"):
        assert pattern not in run, (
            f"validation command must not swallow errors (found '{pattern}'); "
            "a rejected subject must mark the overall run as failed"
        )
    assert "status=1" in run and 'exit "$status"' in run, (
        "a rejected subject anywhere in the pushed range must fail the step"
    )
