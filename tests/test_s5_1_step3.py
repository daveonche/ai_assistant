"""S5.1 step 3 verification: --init-project-args template creation.

Exercises the launcher from the outside with the docker CLI stubbed to
fail every invocation (exit 127, the status a shell reports for a
missing command), so a zero exit proves the flag works without container
tooling.

Covered here:
- the flag creates the per-project args file at its documented host-side
  path (keyed to the project identity with the same workspace-hash
  formula as the command log) when it does not exist;
- the template is entirely comments — a freshly created file loads as
  zero arguments — and carries the worked override examples for the
  model-settings file and the ignore file with the required guidance
  (distinctive referenced filename, self-sufficient copy from the
  assistant's own file, override only when genuinely needed);
- an existing args file is never overwritten or modified.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SANDBOX_FILES = (
    ".agent/start.sh",
    ".agent/launcher.py",
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

USER_CUSTOMIZATION = "--dark-mode\n# user customization\n"


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
    env["AI_ASSISTANT_SESSION_ID"] = "s5-1-step3"
    env.pop("SSH_AUTH_SOCK", None)
    return env


def run_chain(
    sandbox: Path,
    stub_dir: Path,
    args: list[str],
) -> subprocess.CompletedProcess:
    env = _launcher_env(sandbox, stub_dir)
    return subprocess.run(
        ["bash", str(sandbox / ".agent" / "start.sh"), *args],
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


def test_init_creates_commented_template_at_the_documented_path(
    tmp_path: Path,
):
    """With no args file, --init-project-args creates the commented
    template at the documented host-side path and reports it."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)

    result = run_chain(sandbox, stub_dir, ["--init-project-args"])
    assert result.returncode == 0, result.stdout + result.stderr

    expected = _args_file_path(sandbox)
    assert expected.is_file(), result.stdout + result.stderr
    assert (
        f"Created the per-project args file: {expected}" in result.stdout
    ), result.stdout

    text = expected.read_text(encoding="utf-8")
    # Every line is a comment, so a fresh file loads as zero arguments.
    assert all(
        not line.strip() or line.startswith("#") for line in text.splitlines()
    ), text
    # Worked override examples for both file types...
    assert "--model-settings-file" in text, text
    assert "--aiderignore" in text, text
    # ...with the required guidance: a distinctive referenced filename, a
    # self-sufficient copy from the assistant's own file, and overriding
    # only when genuinely needed.
    assert "distinctive name" in text, text
    assert "self-sufficient" in text, text
    assert "genuinely needs" in text, text


def test_init_never_overwrites_an_existing_file(tmp_path: Path):
    """A second run over an existing args file reports it and leaves the
    user's content byte-for-byte untouched."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)

    first = run_chain(sandbox, stub_dir, ["--init-project-args"])
    assert first.returncode == 0, first.stderr

    path = _args_file_path(sandbox)
    path.write_text(USER_CUSTOMIZATION, encoding="utf-8")

    second = run_chain(sandbox, stub_dir, ["--init-project-args"])
    assert second.returncode == 0, second.stderr
    assert (
        f"Project args file already exists; left unchanged: {path}"
        in second.stdout
    ), second.stdout
    assert path.read_text(encoding="utf-8") == USER_CUSTOMIZATION


def test_init_works_without_container_tooling(tmp_path: Path):
    """The docker stub fails every invocation, so a zero exit with the
    file created proves the flag never needs container tooling."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)

    result = run_chain(sandbox, stub_dir, ["--init-project-args"])
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Docker CLI is not available" not in result.stderr, result.stderr
    assert _args_file_path(sandbox).is_file()
