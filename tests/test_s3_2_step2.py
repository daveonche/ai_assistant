"""S3.2 Step 2 verification: action references pinned to full-length SHAs."""

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "ci.yml"
TECH_STACK_PATH = REPO_ROOT / "docs" / "tech_stack.md"

# owner/repo@<ref> (or owner/repo/subdir@<ref>); docker:// image
# references are not action references and are exempt.
USES_REF = re.compile(r"^(?P<action>[\w.-]+/[\w.-]+(?:/[\w.-]+)*)@(?P<ref>\S+)$")
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")


def _load_workflow() -> dict:
    assert WORKFLOW_PATH.is_file(), "missing .github/workflows/ci.yml"
    workflow = yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))
    assert isinstance(workflow, dict), "ci.yml is not a mapping"
    return workflow


def _action_references(workflow: dict) -> list[tuple[str, str, str]]:
    """Return (job, action, ref) for every uses: reference in ci.yml."""
    refs: list[tuple[str, str, str]] = []
    jobs = workflow.get("jobs") or {}
    assert isinstance(jobs, dict) and jobs, "ci.yml defines no jobs"
    for job_name, job in jobs.items():
        for step in (job or {}).get("steps") or []:
            if not isinstance(step, dict):
                continue
            uses = str(step.get("uses") or "")
            if not uses:
                continue
            if uses.startswith("docker://"):
                continue  # container image reference, not an action
            match = USES_REF.match(uses)
            assert match, (
                f"unparseable uses: reference {uses!r} in job {job_name}"
            )
            refs.append((job_name, match.group("action"), match.group("ref")))
    return refs


def _verified_shas() -> set[str]:
    """Return the full-length SHAs recorded in docs/tech_stack.md."""
    text = TECH_STACK_PATH.read_text(encoding="utf-8")
    return set(re.findall(r"\b[0-9a-f]{40}\b", text))


def _summary(refs: list[tuple[str, str, str]]) -> str:
    pinned = sum(1 for _, _, ref in refs if FULL_SHA.match(ref))
    return (
        f"{pinned} of {len(refs)} uses: references pinned to "
        "full-length commit SHAs"
    )


def test_all_action_references_are_full_length_shas():
    workflow = _load_workflow()
    refs = _action_references(workflow)
    assert refs, "no uses: references found in ci.yml"
    unpinned = [
        f"job {job}: {action}@{ref}"
        for job, action, ref in refs
        if not FULL_SHA.match(ref)
    ]
    assert not unpinned, f"{_summary(refs)}; not SHA-pinned: {unpinned}"
    print(f"action-pin summary: {_summary(refs)}")


def test_pinned_shas_match_verified_pins_in_tech_stack():
    workflow = _load_workflow()
    refs = _action_references(workflow)
    verified = _verified_shas()
    assert verified, "docs/tech_stack.md records no verified SHAs"
    unverified = [
        f"job {job}: {action}@{ref}"
        for job, action, ref in refs
        if ref not in verified
    ]
    assert not unverified, (
        f"{_summary(refs)}; SHAs not recorded as verified in "
        f"docs/tech_stack.md: {unverified}"
    )
    print(f"action-pin summary: {_summary(refs)}")
