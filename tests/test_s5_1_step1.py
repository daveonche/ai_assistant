"""S5.1 step 1 verification: configuration references point at .agent/ only.

Exercises the launcher from the outside, the way a user runs it: the
sandbox copies the real launch chain (.agent/start.sh ->
.agent/launcher.py), the docker CLI is a recording stub on PATH,
and HOME points inside the sandbox.

Covered here:
- with the assistant's own configuration files present in .agent/, the
  container run carries the corresponding reference flags, each pointing
  at the .agent/ copy's path;
- project-root configuration files are never detected, read, or passed
  to the assistant (covered in the second test of this suite).
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
    ".agent/launcher.py",
    ".agent/Dockerfile.aider",
)

# Recording docker stub. Image inspect always fails, so every launch
# takes the cache-miss -> build path; version/ps/rm/build/tag succeed;
# run (both the passwd-home probe and the real container) prints a
# marker and exits 0.
DOCKER_STUB = """\
#!/usr/bin/env bash
# Recording docker stub for the S5.1 config-reference reproducers.
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

# Assistant-directory configuration files: (reference flag, filename,
# harmless content). Existence is what the launcher keys on; contents
# are never parsed by it.
AGENT_CONFIG_FILES = (
    ("--config", ".aider.conf.yml", "# agent-dir config\n"),
    (
        "--model-settings-file",
        ".aider.model.settings.yml",
        "# agent-dir model settings\n",
    ),
    ("--aiderignore", ".aiderignore", "# agent-dir ignore\n"),
    ("--model-metadata-file", ".aider.model.metadata.json", "{}\n"),
)

# Project-root configuration files the launcher must ignore: (filename,
# payload). The payload is assistant-flag-shaped, so if the launcher ever
# passed root config contents through to the assistant, the container run
# would show it.
ROOT_CONFIG_FILES = (
    (".aider.conf.yml", "--evil-flag-from-root-config"),
    (".aider.model.settings.yml", "--evil-flag-from-root-model-settings"),
    (".aiderignore", "--evil-flag-from-root-aiderignore"),
    (".aider.model.metadata.json", "--evil-flag-from-root-model-metadata"),
)


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
    env["AI_ASSISTANT_SESSION_ID"] = "s5-1-step1"
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


def test_config_references_point_at_agent_dir(tmp_path: Path):
    """With the assistant's own configuration files present in .agent/,
    every reference flag in the container run points at the .agent/
    copy's path — and the launch completes normally with no project-root
    configuration files present."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)
    for _flag, name, content in AGENT_CONFIG_FILES:
        (sandbox / ".agent" / name).write_text(content, encoding="utf-8")
    # No project-root configuration files exist.

    result = run_chain(sandbox, stub_dir)
    assert result.returncode == 0, result.stderr

    run = _container_run(sandbox)
    for flag, name, _content in AGENT_CONFIG_FILES:
        # index() proves the flag is present; the token after it must be
        # the .agent/ copy's path.
        assert run[run.index(flag) + 1] == str(sandbox / ".agent" / name), run


def test_root_config_files_are_never_read_or_passed(tmp_path: Path):
    """With all four project-root configuration files present, the
    container run contains neither their paths nor their contents: the
    launcher never detects, reads, or passes them to the assistant."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)
    for name, payload in ROOT_CONFIG_FILES:
        (sandbox / name).write_text(payload + "\n", encoding="utf-8")

    result = run_chain(sandbox, stub_dir)
    assert result.returncode == 0, result.stderr

    run = _container_run(sandbox)
    for name, payload in ROOT_CONFIG_FILES:
        root_path = str(sandbox / name)
        # Substring form, so an occurrence embedded inside a longer
        # argument is caught too.
        assert not any(root_path in arg for arg in run), run
        assert not any(payload in arg for arg in run), run
