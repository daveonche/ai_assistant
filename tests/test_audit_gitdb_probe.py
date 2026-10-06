"""Pre-flight gitdb probe: detect-and-warn before a BadObject launch.

Aider reads the repository through GitPython/gitdb inside the container,
not through the git binary, and gitdb can fail with "BadObject" on
repositories git itself reads cleanly — observed on launch with a few
thousand fragmented loose objects while `git fsck --full` passed. The
launcher now gates a one-shot container probe on the host loose-object
count (LOOSE_OBJECT_PROBE_THRESHOLD) and, when the image's own gitdb
cannot read the repository, warns with the remediation instead of
letting aider fail mid-launch. Detection only: the probe mounts the
repository read-only and the launch is never blocked.

Covers:

1. The loose-object gate: below the threshold no probe container is
   started, so ordinary launches pay nothing beyond the local
   count-objects call.
2. The .git guard: a non-repository root is never probed (git is not
   even invoked).
3. A healthy probe (exit 0) stays silent and the launch proceeds.
4. A failing probe (exit 2) warns with the unreadable object,
   prescribes plain `git gc`, cautions against --prune=now, and still
   launches — with the probe verified read-only, network-less, running
   as the host uid on the image's venv interpreter, and ordered before
   the assistant container run.
5. With another session live in the workspace, the remediation is
   deferred (live-pid note) instead of an immediate concurrent gc.

The docker and git CLIs are stubbed on PATH (recording stubs, same
pattern as tests/test_audit_assistant_config_trust.py); .agent/start.sh
runs the real launcher python. The stub's image inspect always fails so
every launch takes the cache-miss -> build path; the probe container is
distinguished from the real assistant run by its --network flag, and
the git stub emulates only `count-objects -v`.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SANDBOX_FILES = (
    ".agent/start.sh",
    ".agent/ai_assistant.py",
    ".agent/Dockerfile.aider",
)

# The object sha from the original incident, emitted as the probe's
# unreadable object so the warning text is asserted end to end.
BAD_OBJECT = "621ea7268990c39d10a52fce95d9b510b8ac9e6c"

# Above LOOSE_OBJECT_PROBE_THRESHOLD (1024), matching the observed
# failure state's order of magnitude.
HIGH_LOOSE_COUNT = "2000"

DOCKER_STUB = """\
#!/usr/bin/env bash
# Recording docker stub for the gitdb probe reproducers.
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
    for arg in "$@"; do
      if [[ "$arg" == "--network" ]]; then
        # The gitdb probe: drain the probe program from stdin, then
        # answer from the configurable result files.
        cat > /dev/null
        if [[ -f "$STUB_DIR/probe-stdout" ]]; then
          cat "$STUB_DIR/probe-stdout"
        fi
        probe_exit=0
        if [[ -f "$STUB_DIR/probe-exit" ]]; then
          probe_exit="$(cat "$STUB_DIR/probe-exit")"
        fi
        exit "$probe_exit"
      fi
    done
    printf 'assistant-ready\\n'  # the real assistant container run
    exit 0
    ;;
  ps)
    if [[ -f "$STUB_DIR/ps-output" ]]; then
      cat "$STUB_DIR/ps-output"
    fi
    exit 0
    ;;
  *)
    exit 0
    ;;
esac
"""

GIT_STUB = """\
#!/usr/bin/env bash
# Recording git stub: emulates `count-objects -v` with a configurable
# loose-object count; every other subcommand exits 0 silently.
set -uo pipefail
STUB_DIR="__STUB_DIR__"
INVOCATIONS="$STUB_DIR/git-invocations.txt"
record=""
for arg in "$@"; do
  record="$record$arg"$'\\x1f'
done
printf '%s\\n' "$record" >> "$INVOCATIONS"
is_count=0
for arg in "$@"; do
  [[ "$arg" == "count-objects" ]] && is_count=1
done
if (( is_count )); then
  count=0
  if [[ -f "$STUB_DIR/loose-count" ]]; then
    count="$(cat "$STUB_DIR/loose-count")"
  fi
  printf 'count: %s\\n' "$count"
  printf 'in-pack: 0\\n'
  printf 'packs: 1\\n'
  exit 0
fi
exit 0
"""


def _make_sandbox(tmp_path: Path, with_git: bool = True) -> Path:
    sandbox = tmp_path / "project"
    (sandbox / ".agent").mkdir(parents=True)
    for rel in SANDBOX_FILES:
        shutil.copy2(PROJECT_ROOT / rel, sandbox / rel)
    (sandbox / "home").mkdir()
    (sandbox / "runtime").mkdir()
    if with_git:
        # Only the launcher's existence check inspects this directory;
        # git itself is stubbed, so an empty .git suffices.
        (sandbox / ".git").mkdir()
    return sandbox


def _write_stubs(sandbox: Path) -> Path:
    stub_dir = sandbox / "stub"
    stub_dir.mkdir()
    for name, body in (("docker", DOCKER_STUB), ("git", GIT_STUB)):
        stub = stub_dir / name
        stub.write_text(body.replace("__STUB_DIR__", str(stub_dir)))
        stub.chmod(0o755)
    return stub_dir


def _launcher_env(sandbox: Path, stub_dir: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PATH"] = f"{stub_dir}{os.pathsep}{env.get('PATH', '')}"
    env["HOME"] = str(sandbox / "home")
    env["AI_ASSISTANT_SESSION_ID"] = "gitdb-probe"
    env.pop("SSH_AUTH_SOCK", None)
    return env


def run_chain(
    sandbox: Path,
    stub_dir: Path,
    args: list[str] | None = None,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(sandbox / ".agent" / "start.sh"), *(args or [])],
        cwd=sandbox,
        env=_launcher_env(sandbox, stub_dir),
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


def git_invocations(sandbox: Path) -> list[list[str]]:
    """Git stub invocations; empty when git was never invoked.

    Tolerant of a missing log because the .git guard can skip every git
    call in a launch (test_probe_skipped_without_git_repository).
    """
    path = sandbox / "stub" / "git-invocations.txt"
    if not path.exists():
        return []
    return [
        line.split("\x1f")[:-1]
        for line in path.read_text().splitlines()
    ]


def _probe_runs(invocations: list[list[str]]) -> list[list[str]]:
    """The one-shot gitdb probe, identified by its --network flag."""
    return [
        inv for inv in invocations
        if inv[0] == "run" and "--network" in inv
    ]


def _container_runs(invocations: list[list[str]]) -> list[list[str]]:
    """The launcher's assistant container run.

    The gitdb probe also invokes `docker run` (with --network none), and
    the passwd-home probe would add --entrypoint, so the real container
    run is identified negatively (same pattern as
    tests/test_audit_assistant_config_trust.py).
    """
    return [
        inv for inv in invocations
        if inv[0] == "run"
        and "--network" not in inv
        and "--entrypoint" not in inv
    ]


def test_probe_skipped_below_loose_object_threshold(tmp_path: Path):
    """Below the threshold no probe container starts: ordinary launches
    pay nothing beyond the local count-objects call."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_stubs(sandbox)
    (stub_dir / "loose-count").write_text("10\n")

    result = run_chain(sandbox, stub_dir)

    assert result.returncode == 0, result.stderr
    # The gate ran (count-objects was called) and cheaply declined.
    assert any(
        "count-objects" in inv for inv in git_invocations(sandbox)
    ), git_invocations(sandbox)
    invocations = stub_invocations(sandbox)
    assert not _probe_runs(invocations), invocations
    assert _container_runs(invocations), invocations


def test_probe_skipped_without_git_repository(tmp_path: Path):
    """A non-repository root is never probed, even above the threshold:
    the .git guard fires before git is invoked at all."""
    sandbox = _make_sandbox(tmp_path, with_git=False)
    stub_dir = _write_stubs(sandbox)
    (stub_dir / "loose-count").write_text(f"{HIGH_LOOSE_COUNT}\n")

    result = run_chain(sandbox, stub_dir)

    assert result.returncode == 0, result.stderr
    assert not any(
        "count-objects" in inv for inv in git_invocations(sandbox)
    ), git_invocations(sandbox)
    assert not _probe_runs(stub_invocations(sandbox)), (
        stub_invocations(sandbox)
    )


def test_healthy_probe_is_silent_and_launch_proceeds(tmp_path: Path):
    """Exit 0 from the probe produces no warning; the launch continues."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_stubs(sandbox)
    (stub_dir / "loose-count").write_text(f"{HIGH_LOOSE_COUNT}\n")
    (stub_dir / "probe-exit").write_text("0\n")
    (stub_dir / "probe-stdout").write_text("probe-ok\n")

    result = run_chain(sandbox, stub_dir)

    assert result.returncode == 0, result.stderr
    invocations = stub_invocations(sandbox)
    assert len(_probe_runs(invocations)) == 1, invocations
    assert _container_runs(invocations), invocations
    assert "gitdb" not in result.stderr, result.stderr


def test_failed_probe_warns_and_still_launches(tmp_path: Path):
    """Exit 2 warns with the unreadable object and the gc remediation,
    and the assistant still launches (detection never blocks)."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_stubs(sandbox)
    (stub_dir / "loose-count").write_text(f"{HIGH_LOOSE_COUNT}\n")
    (stub_dir / "probe-exit").write_text("2\n")
    (stub_dir / "probe-stdout").write_text(
        f"probe-bad-object: HEAD tree walk: BadObject(b'{BAD_OBJECT}')\n"
    )

    result = run_chain(sandbox, stub_dir)

    assert result.returncode == 0, result.stderr
    invocations = stub_invocations(sandbox)
    probes = _probe_runs(invocations)
    runs = _container_runs(invocations)
    assert len(probes) == 1, invocations
    assert runs, "assistant should still launch after the warning"
    assert invocations.index(probes[0]) < invocations.index(runs[0])

    # The probe is faithful and contained: the image's venv interpreter,
    # the host uid, no network, and the repository mounted read-only at
    # its identical path.
    probe = probes[0]
    assert probe[probe.index("--entrypoint") + 1] == "/venv/bin/python3", (
        probe
    )
    assert probe[probe.index("--user") + 1] == str(os.getuid()), probe
    assert probe[probe.index("--network") + 1] == "none", probe
    assert f"{sandbox}:{sandbox}:ro" in probe, probe

    stderr = result.stderr
    assert "could not read this repository" in stderr, stderr
    assert BAD_OBJECT in stderr, stderr
    assert "git gc" in stderr, stderr
    assert "--prune=now" in stderr, stderr
    assert "Fix while no assistant session is running" in stderr, stderr


def test_live_session_defers_the_remediation(tmp_path: Path):
    """With a live session in the workspace the warning defers the
    repair instead of suggesting an immediate concurrent gc."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = _write_stubs(sandbox)
    (stub_dir / "loose-count").write_text(f"{HIGH_LOOSE_COUNT}\n")
    (stub_dir / "probe-exit").write_text("2\n")
    (stub_dir / "probe-stdout").write_text(
        f"probe-bad-object: HEAD tree walk: BadObject(b'{BAD_OBJECT}')\n"
    )
    # A live session: the stub answers `docker ps` with this host pid,
    # which _pid_alive must find alive.
    (stub_dir / "ps-output").write_text(f"c0ffee {os.getpid()}\n")

    result = run_chain(sandbox, stub_dir)

    assert result.returncode == 0, result.stderr
    stderr = result.stderr
    assert "could not read this repository" in stderr, stderr
    assert "are still live" in stderr, stderr
    assert "Fix while no assistant session is running" not in stderr, (
        stderr
    )
    assert "git gc" in stderr, stderr
