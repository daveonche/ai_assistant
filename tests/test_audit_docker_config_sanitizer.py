"""Security-audit reproducers for the Docker config sanitizer in
.agent/ai_assistant.py (_sanitize_docker_config).

Windows Docker Desktop writes "credsStore": "desktop.exe" into the host
~/.docker/config.json. That helper is a Windows binary: inside the
assistant container every registry operation consulting it (resolving a
build frontend, pulling a base image) fails with "executable file not
found in $PATH". The launcher therefore mounts a sanitized copy (.exe
helpers dropped) from the launcher-private cache instead of the raw host
directory, and fails closed — no Docker config mount at all — when the
config cannot be parsed or the copy cannot be written.

Each test inspects the -v arguments of the real container run recorded
by the stubbed docker CLI (same pattern as
tests/test_audit_assistant_config_trust.py); agent.sh runs the real
launcher python. Non-.exe credential helpers are intentionally passed
through untouched: only the provably-broken Windows class is handled.
"""

from __future__ import annotations

import json
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

# Recording docker stub, identical in behavior to the one in
# tests/test_audit_assistant_config_trust.py: image inspect always fails
# (cache-miss -> build path), run prints a marker and exits 0.
DOCKER_STUB = """\
#!/usr/bin/env bash
# Recording docker stub for the Docker-config sanitizer reproducers.
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
    env["AI_ASSISTANT_SESSION_ID"] = "audit-sanitizer"
    env.pop("SSH_AUTH_SOCK", None)
    return env


def run_chain(
    sandbox: Path,
    stub_dir: Path,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    env = _launcher_env(sandbox, stub_dir)
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        ["bash", str(sandbox / "agent.sh")],
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


def _container_runs(invocations: list[list[str]]) -> list[list[str]]:
    """The launcher's container run, not the passwd-home probe run."""
    return [
        inv for inv in invocations
        if inv[0] == "run" and "--entrypoint" not in inv
    ]


def _write_docker_config(sandbox: Path, text: str) -> Path:
    docker_dir = sandbox / "home" / ".docker"
    docker_dir.mkdir(parents=True, exist_ok=True)
    config = docker_dir / "config.json"
    config.write_text(text, encoding="utf-8")
    return config


def _sanitized_config(sandbox: Path) -> Path:
    return (
        sandbox / "home" / ".cache" / "aider-agent"
        / "docker-config" / "config.json"
    )


def _docker_config_mounts(run_args: list[str]) -> list[str]:
    """Mount sources of the container's read-only /home/.docker mount."""
    return [
        arg[: -len(":/home/.docker:ro")]
        for arg in run_args
        if arg.endswith(":/home/.docker:ro")
    ]


def test_windows_creds_store_is_dropped_from_the_mounted_config(
    tmp_path: Path,
):
    """desktop.exe must never reach the container: the mount points at
    the sanitized cache copy, the helper is gone, auths survive, and the
    host file is never rewritten."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)
    host_config = _write_docker_config(
        sandbox,
        json.dumps(
            {
                "credsStore": "desktop.exe",
                "auths": {"https://index.docker.io/v1/": {}},
            }
        ),
    )

    result = run_chain(sandbox, stub_dir)
    assert result.returncode == 0, result.stderr

    runs = _container_runs(stub_invocations(sandbox))
    assert len(runs) == 1, stub_invocations(sandbox)
    sanitized_dir = _sanitized_config(sandbox).parent
    assert _docker_config_mounts(runs[0]) == [str(sanitized_dir)], runs[0]

    doc = json.loads(_sanitized_config(sandbox).read_text(encoding="utf-8"))
    assert "credsStore" not in doc, doc
    assert doc["auths"] == {"https://index.docker.io/v1/": {}}, doc

    assert (
        json.loads(host_config.read_text(encoding="utf-8"))["credsStore"]
        == "desktop.exe"
    )
    assert "dropped Windows-only credential helper" in result.stderr, (
        result.stderr
    )

    # The sanitized copy stays outside every container-writable mount.
    cache_mounts = [
        arg[: -len(":/home/.cache")]
        for arg in runs[0]
        if arg.endswith(":/home/.cache")
    ]
    assert cache_mounts, runs[0]
    for source in cache_mounts:
        assert not sanitized_dir.is_relative_to(source), (
            f"sanitized config {sanitized_dir} is inside container-writable "
            f"mount source {source}"
        )


def test_cred_helpers_exe_entries_are_filtered(tmp_path: Path):
    """Mixed credHelpers: only the .exe helper is dropped; the Linux
    helper entry survives in the mounted copy."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)
    _write_docker_config(
        sandbox,
        json.dumps(
            {
                "credHelpers": {
                    "registry.example": "desktop.exe",
                    "ghcr.io": "docker-credential-linux",
                },
            }
        ),
    )

    result = run_chain(sandbox, stub_dir)
    assert result.returncode == 0, result.stderr

    runs = _container_runs(stub_invocations(sandbox))
    assert len(runs) == 1, stub_invocations(sandbox)
    assert _docker_config_mounts(runs[0]) == [
        str(_sanitized_config(sandbox).parent)
    ], runs[0]

    sanitized_text = _sanitized_config(sandbox).read_text(encoding="utf-8")
    doc = json.loads(sanitized_text)
    assert doc["credHelpers"] == {"ghcr.io": "docker-credential-linux"}, doc
    assert "desktop.exe" not in sanitized_text


def test_all_exe_cred_helpers_remove_the_key(tmp_path: Path):
    """When every credHelpers entry is a Windows helper, the key is
    removed entirely instead of leaving an empty mapping."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)
    _write_docker_config(
        sandbox,
        json.dumps(
            {
                "credHelpers": {
                    "registry.example": "desktop.exe",
                    "ghcr.io": "docker-credential-desktop.exe",
                },
            }
        ),
    )

    result = run_chain(sandbox, stub_dir)
    assert result.returncode == 0, result.stderr

    runs = _container_runs(stub_invocations(sandbox))
    assert len(runs) == 1, stub_invocations(sandbox)
    assert _docker_config_mounts(runs[0]) == [
        str(_sanitized_config(sandbox).parent)
    ], runs[0]

    doc = json.loads(_sanitized_config(sandbox).read_text(encoding="utf-8"))
    assert "credHelpers" not in doc, doc


def test_clean_config_passes_through_unchanged(tmp_path: Path):
    """No .exe helpers (including a Linux credsStore): the host directory
    itself is mounted and no sanitized copy is created."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)
    _write_docker_config(
        sandbox,
        json.dumps({"credsStore": "seahorses", "auths": {}}),
    )

    result = run_chain(sandbox, stub_dir)
    assert result.returncode == 0, result.stderr

    runs = _container_runs(stub_invocations(sandbox))
    assert len(runs) == 1, stub_invocations(sandbox)
    assert _docker_config_mounts(runs[0]) == [
        str(sandbox / "home" / ".docker")
    ], runs[0]
    assert not _sanitized_config(sandbox).exists()


def test_missing_config_file_mounts_the_host_directory(tmp_path: Path):
    """~/.docker without config.json mounts unchanged (FileNotFoundError
    pass-through)."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)
    (sandbox / "home" / ".docker").mkdir(parents=True)

    result = run_chain(sandbox, stub_dir)
    assert result.returncode == 0, result.stderr

    runs = _container_runs(stub_invocations(sandbox))
    assert len(runs) == 1, stub_invocations(sandbox)
    assert _docker_config_mounts(runs[0]) == [
        str(sandbox / "home" / ".docker")
    ], runs[0]


def test_unparsable_config_fails_closed(tmp_path: Path):
    """A config.json that is not valid JSON must not be mounted at all;
    the launch still proceeds (anonymous public pulls work)."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)
    _write_docker_config(sandbox, '{"credsStore": "desktop.exe"')  # truncated

    result = run_chain(sandbox, stub_dir)
    assert result.returncode == 0, result.stderr

    runs = _container_runs(stub_invocations(sandbox))
    assert len(runs) == 1, stub_invocations(sandbox)
    assert not _docker_config_mounts(runs[0]), runs[0]
    assert "cannot parse" in result.stderr, result.stderr


def test_non_object_config_fails_closed(tmp_path: Path):
    """A valid-JSON non-object config must not be mounted at all."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)
    _write_docker_config(sandbox, '["desktop.exe"]')

    result = run_chain(sandbox, stub_dir)
    assert result.returncode == 0, result.stderr

    runs = _container_runs(stub_invocations(sandbox))
    assert len(runs) == 1, stub_invocations(sandbox)
    assert not _docker_config_mounts(runs[0]), runs[0]
    assert "not a JSON object" in result.stderr, result.stderr


def test_unwritable_cache_fails_closed(tmp_path: Path):
    """When the sanitized copy cannot be written, no Docker config is
    mounted (fail closed) and the launch still proceeds."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_docker_stub(sandbox)
    _write_docker_config(sandbox, json.dumps({"credsStore": "desktop.exe"}))
    # A regular file where the launcher-private cache dir must be created
    # makes every mkdir/write inside the sanitizer fail.
    cache = sandbox / "home" / ".cache"
    cache.mkdir()
    (cache / "aider-agent").write_text("", encoding="utf-8")

    result = run_chain(sandbox, stub_dir)
    assert result.returncode == 0, result.stderr

    runs = _container_runs(stub_invocations(sandbox))
    assert len(runs) == 1, stub_invocations(sandbox)
    assert not _docker_config_mounts(runs[0]), runs[0]
    assert "could not write the sanitized Docker config" in result.stderr, (
        result.stderr
    )
