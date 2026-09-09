"""Tests for S1.3 Step 6: Enable assistant configuration argument assembly."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SANDBOX_FILES = (
    "agent.sh",
    ".agent/ai-assistant.sh",
    ".agent/ai_assistant.py",
    ".agent/Dockerfile.aider",
)

# Config-derived aider flags assembled by _aider_config_args(), in order.
CONFIG_FLAG_FILES = (
    (".aider.conf.yml", "--config"),
    (".aider.model.settings.yml", "--model-settings-file"),
    (".aiderignore", "--aiderignore"),
    (".aider.model.metadata.json", "--model-metadata-file"),
)

# Recording docker stub: image inspect succeeds only for tags the launcher
# itself has tagged/built, so the chain reaches docker run and every
# invocation is recorded. Digest probes (--format) always fail, making the
# cache tag a deterministic hash of the Dockerfile bytes alone.
DOCKER_STUB = """\
#!/usr/bin/env bash
# Recording docker stub for S1.3 Step 6 tests.
set -uo pipefail
STUB_DIR="__STUB_DIR__"
INVOCATIONS="$STUB_DIR/invocations.txt"
KNOWN_TAGS="$STUB_DIR/known_tags.txt"

record=""
for arg in "$@"; do
  record="$record$arg"$'\\x1f'
done
printf '%s\\n' "$record" >> "$INVOCATIONS"

cmd="${1:-}"
case "$cmd" in
  version)
    exit 0
    ;;
  ps|rm)
    exit 0
    ;;
  image)
    if [[ "${2:-}" == "inspect" ]]; then
      if [[ " $* " == *" --format "* ]]; then
        exit 1
      fi
      tag="${*: -1}"
      if [[ -f "$KNOWN_TAGS" ]] && grep -Fxq -- "$tag" "$KNOWN_TAGS"; then
        exit 0
      fi
      exit 1
    fi
    exit 0
    ;;
  build)
    printf '%s\\n' "aider-agent:latest" >> "$KNOWN_TAGS"
    printf 'docker build ok\\n'
    exit "${FAIL_BUILD:-0}"
    ;;
  tag)
    printf '%s\\n' "${*: -1}" >> "$KNOWN_TAGS"
    exit 0
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
        shutil.copy2(REPO_ROOT / rel, sandbox / rel)
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
    env["AI_ASSISTANT_SESSION_ID"] = "s6"
    (sandbox / "home").mkdir(exist_ok=True)
    return env


def run_chain(
    sandbox: Path,
    stub_dir: Path,
    args: list[str],
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    env = _launcher_env(sandbox, stub_dir)
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        ["bash", str(sandbox / "agent.sh"), *args],
        cwd=sandbox,
        env=env,
        capture_output=True,
        text=True,
        timeout=180,
    )


def stub_invocations(sandbox: Path) -> list[list[str]]:
    path = sandbox / "stub" / "invocations.txt"
    return [
        line.split("\x1f")[:-1]
        for line in path.read_text().splitlines()
    ]


def _run_tail(invocation: list[str]) -> list[str]:
    """Return the aider argument tail after the image name of a run invocation."""
    return invocation[invocation.index("aider-agent:latest") + 1 :]


def _flag_pairs(tail: list[str]) -> list[list[str]]:
    return [tail[i : i + 2] for i in range(len(tail) - 1)]


def test_present_config_files_assemble_corresponding_launch_arguments(tmp_path):
    sandbox = _make_sandbox(tmp_path)
    for name, _flag in CONFIG_FLAG_FILES:
        (sandbox / ".agent" / name).write_text("# config\n", encoding="utf-8")
    stub_dir = _write_docker_stub(sandbox)

    result = run_chain(sandbox, stub_dir, [])
    assert result.returncode == 0, result.stderr

    run_inv = [inv for inv in stub_invocations(sandbox) if inv[0] == "run"][-1]
    pairs = _flag_pairs(_run_tail(run_inv))

    for name, flag in CONFIG_FLAG_FILES:
        expected_path = str(sandbox / ".agent" / name)
        assert [flag, expected_path] in pairs, (
            f"{flag} {expected_path} missing from assembled arguments"
        )


def test_config_file_set_change_is_reflected_in_assembled_arguments(tmp_path):
    sandbox = _make_sandbox(tmp_path)
    present = CONFIG_FLAG_FILES[:2]   # .aider.conf.yml, .aider.model.settings.yml
    absent = CONFIG_FLAG_FILES[2:]    # .aiderignore, .aider.model.metadata.json

    for name, _flag in present:
        (sandbox / ".agent" / name).write_text("# config\n", encoding="utf-8")
    stub_dir = _write_docker_stub(sandbox)

    first = run_chain(sandbox, stub_dir, [])
    assert first.returncode == 0, first.stderr
    offset = len(stub_invocations(sandbox))

    # Remove one present config file and re-run.
    removed_name, removed_flag = present[1]
    (sandbox / ".agent" / removed_name).unlink()

    second = run_chain(sandbox, stub_dir, [])
    assert second.returncode == 0, second.stderr

    second_run = [
        inv
        for inv in stub_invocations(sandbox)[offset:]
        if inv[0] == "run"
    ][-1]
    second_pairs = _flag_pairs(_run_tail(second_run))

    # Removed file's flag is no longer assembled...
    assert not any(pair[0] == removed_flag for pair in second_pairs), second_run
    # ...the still-present file keeps its flag with the sandbox path...
    kept_name, kept_flag = present[0]
    assert [kept_flag, str(sandbox / ".agent" / kept_name)] in second_pairs
    # ...and never-present files never gained a flag.
    for _name, flag in absent:
        assert not any(pair[0] == flag for pair in second_pairs), second_run
