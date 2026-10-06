"""S5.1 step 5 verification: the project-root config counterpart notice.

Exercises the launcher from the outside with a recording docker stub, so
the full launch completes and the container run can be inspected.

Covered here:
- each of the four known project-root configuration filenames gets a
  one-line notice stating it is not read and pointing at
  --init-project-args;
- no notice is printed when none of the files exist;
- the check is existence-only: a distinctive payload written into a
  root config file never reaches the assistant command.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

AIDER_IMAGE = "aider-agent:latest"

SANDBOX_FILES = (
    ".agent/start.sh",
    ".agent/ai_assistant.py",
    ".agent/Dockerfile.aider",
)

ROOT_CONFIG_FILENAMES = (
    ".aider.conf.yml",
    ".aider.model.settings.yml",
    ".aiderignore",
    ".aider.model.metadata.json",
)

# Recording docker stub. Image inspect always fails, so every launch
# takes the cache-miss -> build path; version/ps/rm/build/tag succeed;
# run (both the passwd-home probe and the real container) prints a
# marker and exits 0.
DOCKER_STUB = """\
#!/usr/bin/env bash
# Recording docker stub for the S5.1 root-config-notice reproducers.
set -uo pipefail
STUB_DIR="__STUB_DIR__"
INVOCATIONS="$STUB_DIR/invocations.txt"
record=""
for arg in "$@"; do
  record="$record$arg"$'\\x1f'
done
printf '%s\\n' "$record" >> "$INVOCATIONS"
cmd="${1:-}"
case "$cmd" in
  image)
    exit 1  # every launch takes the cache-miss -> build path
    ;;
  run)
    printf 'assistant-ready\\n'
    exit 0
    ;;
  *)
    exit 0
    ;;
esac
"""


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
    stub.write_text(DOCKER_STUB.replace("__STUB_DIR__", str(stub_dir)))
    stub.chmod(0o755)
    return stub_dir


def _launcher_env(sandbox: Path, stub_dir: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = f"{stub_dir}{os.pathsep}{env.get('PATH', '')}"
    env["HOME"] = str(sandbox / "home")
    env["AI_ASSISTANT_SESSION_ID"] = "s5-1-step5"
    env.pop("SSH_AUTH_SOCK", None)
    return env


def run_chain(
    sandbox: Path,
    stub_dir: Path,
    args: list[str] | None = None,
) -> subprocess.CompletedProcess:
    env = _launcher_env(sandbox, stub_dir)
    return subprocess.run(
        ["bash", str(sandbox / ".agent" / "start.sh"), *(args or [])],
        cwd=sandbox,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )


def stub_invocations(sandbox: Path) -> list[list[str]]:
    path = sandbox / "stub" / "invocations.txt"
    return [
        line.split("\x1f")[:-1]
        for line in path.read_text().splitlines()
    ]


def _container_run(sandbox: Path) -> list[str]:
    """The launcher's container run, not the passwd-home probe run.

    _container_passwd_home() also invokes `docker run` (with
    --entrypoint) whenever ~/.ssh exists — and the launcher's GitHub
    host-key pinning creates it — so the real container run is
    identified by the absence of --entrypoint.
    """
    runs = [
        inv for inv in stub_invocations(sandbox)
        if inv[0] == "run" and "--entrypoint" not in inv
    ]
    assert len(runs) == 1, stub_invocations(sandbox)
    return runs[0]


def _notice_line(name: str) -> str:
    return (
        f"Notice: {name} exists in the project root but is not read; "
        "customize per-project with --init-project-args"
    )


def test_every_root_config_file_gets_a_notice(tmp_path: Path):
    """Each of the four known root config filenames gets its own one-line
    notice stating the file is not read and pointing at the args file."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)
    for name in ROOT_CONFIG_FILENAMES:
        (sandbox / name).write_text(
            "# contents are never read\n", encoding="utf-8"
        )

    result = run_chain(sandbox, stub_dir)
    assert result.returncode == 0, result.stderr

    for name in ROOT_CONFIG_FILENAMES:
        assert _notice_line(name) in result.stdout, result.stdout


def test_no_notice_without_root_config_files(tmp_path: Path):
    """With none of the known filenames present, nothing is announced."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)

    result = run_chain(sandbox, stub_dir)
    assert result.returncode == 0, result.stderr

    assert "Notice:" not in result.stdout, result.stdout


def test_notice_checks_existence_only(tmp_path: Path):
    """The notice is driven by file existence: a distinctive payload
    written into a root config file never reaches the assistant
    command."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)
    payload = "--evil-flag-from-repo-content"
    (sandbox / ".aider.conf.yml").write_text(
        payload + "\n", encoding="utf-8"
    )

    result = run_chain(sandbox, stub_dir)
    assert result.returncode == 0, result.stderr

    assert _notice_line(".aider.conf.yml") in result.stdout, result.stdout
    run = _container_run(sandbox)
    assert not any(payload in arg for arg in run), run
