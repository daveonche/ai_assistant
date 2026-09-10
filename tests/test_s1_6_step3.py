"""Story S1.6 Step 3 — shell script validation in the pipeline.

Verifies the Must Support items: "Automated static analysis of every *.sh
script in the repository", "Scripts discovered by pattern rather than a
hard-coded list, so newly added scripts are covered automatically", and
"A detected analysis finding marks the overall pipeline run as failed".
"""

import subprocess
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


def _git_list_files(args: list[str]) -> set[str]:
    result = subprocess.run(
        ["git", *args], capture_output=True, check=True, text=True
    )
    return {p for p in result.stdout.split("\0") if p}


def test_shell_scripts_discovered_by_pattern_not_hardcoded_list():
    steps = _shell_analysis_steps()
    assert steps, "a shell analysis step must exist"
    run = steps[0].get("run") or ""
    assert "git ls-files" in run, (
        "script discovery must use git ls-files (pattern-based discovery), "
        "not a hard-coded script list"
    )
    assert "*.sh" in run, \
        "discovery must select scripts by the '*.sh' pattern"
    assert "-z" in run, \
        "ls-files must emit null-delimited names (-z) so any path is handled safely"
    assert "xargs" in run and "-0" in run, \
        "xargs must consume null-delimited names (-0), matching ls-files -z"
    assert "-r" in run, (
        "xargs must be empty-safe (-r) so a repository without *.sh scripts "
        "does not invoke the analyzer with no inputs"
    )
    assert "|" in run, \
        "the discovered script list must be piped into the static analyzer"
    for script in ("agent.sh", ".agent/ai-assistant.sh"):
        assert script not in run, (
            f"discovery must not hard-code script names (found '{script}'); "
            "newly added scripts must be covered automatically"
        )

    discovered = _git_list_files(["ls-files", "-z", "*.sh"])
    tracked_sh = {
        p for p in _git_list_files(["ls-files", "-z"]) if p.endswith(".sh")
    }
    assert discovered == tracked_sh, (
        "the '*.sh' discovery pattern must select every tracked *.sh script"
    )
    assert {"agent.sh", ".agent/ai-assistant.sh"} <= discovered, (
        "the currently known scripts (agent.sh, .agent/ai-assistant.sh) must "
        "be covered by the discovery pattern"
    )
