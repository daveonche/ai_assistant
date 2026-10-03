"""S5.1 step 4 verification: --show-project-config without Docker.

Exercises the launcher from the outside with the docker CLI stubbed to
fail every invocation (exit 127), so a zero exit proves the new flags
work without container tooling.

Covered here:
- with no args file, the flag prints the args-file path, an absence
  notice pointing at --init-project-args, and the effective argument
  order (typed command-line arguments win over file entries, which win
  over the assistant-directory defaults);
- with an args file, the flag prints its contents verbatim;
- --init-project-args and --show-project-config both complete without
  container tooling and never reach the Docker availability error.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SANDBOX_FILES = (
    "agent.sh",
    ".agent/ai-assistant.sh",
    ".agent/ai_assistant.py",
    ".agent/Dockerfile.aider",
)

# docker stub standing in for absent container tooling: every invocation
# exits 127, the status a shell reports for a command not found.
DOCKER_STUB = """\
#!/usr/bin/env bash
# Absent-container-tooling stub: every invocation fails with 127.
set -uo pipefail
exit 127
"""

ARGS_FILE_BODY = "--dark-mode\n# project note\n"


def _make_sandbox(tmp_path: Path) -> Path:
    sandbox = tmp_path / "project"
    (sandbox / ".agent").mkdir(parents=True)
    for rel in SANDBOX_FILES:
        shutil.copy2(PROJECT_ROOT / rel, sandbox / rel)
    (sandbox / "home").mkdir()
    return sandbox


def _write_docker_stub(sandbox: Path) -> Path:
    stub_dir = sandbox / "stub"
    stub_dir.mkdir()
    stub = stub_dir / "docker"
    stub.write_text(DOCKER_STUB)
    stub.chmod(0o755)
    return stub_dir


def _launcher_env(sandbox: Path, stub_dir: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = f"{stub_dir}{os.pathsep}{env.get('PATH', '')}"
    env["HOME"] = str(sandbox / "home")
    env["AI_ASSISTANT_SESSION_ID"] = "s5-1-step4"
    env.pop("SSH_AUTH_SOCK", None)
    return env


def run_chain(
    sandbox: Path,
    stub_dir: Path,
    args: list[str],
) -> subprocess.CompletedProcess:
    env = _launcher_env(sandbox, stub_dir)
    return subprocess.run(
        ["bash", str(sandbox / "agent.sh"), *args],
        cwd=sandbox,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )


def _workspace_hash(project_root: Path) -> str:
    """The launcher's project-identity hash (md5 of the path + newline)."""
    return hashlib.md5((str(project_root) + "\n").encode()).hexdigest()


def _args_file_path(sandbox: Path) -> Path:
    """The per-project args-file path the launcher derives for the sandbox."""
    digest = _workspace_hash(sandbox)
    file_name = f"{sandbox.name}-{digest[:8]}.args"
    return (
        sandbox / "home" / ".config" / "aider-agent" / "projects" / file_name
    )


def _write_args_file(sandbox: Path, text: str) -> Path:
    path = _args_file_path(sandbox)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_show_config_without_args_file(tmp_path: Path):
    """With no args file, the flag prints the path, an absence notice
    pointing at the template-creation flag, and the precedence order."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)

    result = run_chain(sandbox, stub_dir, ["--show-project-config"])
    assert result.returncode == 0, result.stdout + result.stderr

    out = result.stdout
    assert f"Project args file: {_args_file_path(sandbox)}" in out, out
    assert "Not found; create it with --init-project-args" in out, out
    assert (
        "Effective argument order: typed command-line arguments win over "
        "file entries, which win over the assistant's own defaults in "
        ".agent/."
    ) in out, out


def test_show_config_prints_contents_when_present(tmp_path: Path):
    """With an args file, the flag prints the path, the contents
    verbatim, and the precedence order."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)
    _write_args_file(sandbox, ARGS_FILE_BODY)

    result = run_chain(sandbox, stub_dir, ["--show-project-config"])
    assert result.returncode == 0, result.stdout + result.stderr

    out = result.stdout
    assert f"Project args file: {_args_file_path(sandbox)}" in out, out
    assert "Contents:" in out, out
    assert "--dark-mode" in out, out
    assert "# project note" in out, out
    assert "Effective argument order" in out, out


def test_both_flags_complete_without_container_tooling(tmp_path: Path):
    """With docker failing on every invocation, both flags exit 0 and
    never reach the Docker availability error."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)

    init = run_chain(sandbox, stub_dir, ["--init-project-args"])
    assert init.returncode == 0, init.stdout + init.stderr
    show = run_chain(sandbox, stub_dir, ["--show-project-config"])
    assert show.returncode == 0, show.stdout + show.stderr
    for result in (init, show):
        assert "Docker CLI is not available" not in result.stderr, (
            result.stderr
        )
