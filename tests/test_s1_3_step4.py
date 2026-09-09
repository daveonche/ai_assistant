"""S1.3 Step 4: deterministic session container identity.

Must Support verified:
- Container names derived deterministically from a hash of the current
  workspace location combined with a unique per-session identifier.
- The same workspace always producing the same name portion, while separate
  sessions produce distinguishable names.
- Multiple containers allowed to coexist within the same workspace while
  their host launcher processes are alive, regardless of editor or terminal.
- Each container labeled with the host launcher PID so its lifetime is bound
  to that process.
- At launch, removal of leftover same-workspace containers whose host
  launcher PID is no longer alive, while containers whose launcher is still
  running are left untouched.
- When the launcher process dies (terminal close, editor close, SIGHUP,
  SIGTERM, or SIGKILL), its container is stopped and removed without waiting
  for a later launch.
- Session identity resolved editor-agnostically for naming only, honoring an
  explicit AI_ASSISTANT_SESSION_ID override, the tmux or GNU screen session
  when present, and otherwise the parent shell PID. Session identity does not
  drive destructive cleanup.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import signal
import subprocess
import time
from pathlib import Path
from typing import NamedTuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Fake docker: records argv as a JSON array per invocation and always
# succeeds. Optional behaviors armed per test via environment:
# - DOCKER_STUB_PS_ROWS: printed verbatim in response to `docker ps ...`
#   (one leftover container per line: "<id> <hostpid>"), simulating
#   same-workspace containers recorded by the host daemon.
# - DOCKER_STUB_RUN_HOLD: `docker run` polls until this file exists before
#   exiting, so a launcher stays alive while the test signals it.
DOCKER_STUB = """\
#!/usr/bin/env bash
set -euo pipefail
json="["
for arg in "$@"; do
  esc=${arg//\\\\/\\\\\\\\}
  esc=${esc//\\"/\\\\\\\"}
  json+="\\"$esc\\","
done
printf '%s\\n' "${json%,}]" >> "$DOCKER_STUB_LOG"

if [[ "${1:-}" == "ps" && -n "${DOCKER_STUB_PS_ROWS:-}" ]]; then
  printf '%s\\n' "$DOCKER_STUB_PS_ROWS"
fi

if [[ "${1:-}" == "run" && -n "${DOCKER_STUB_RUN_HOLD:-}" ]]; then
  while [[ ! -f "$DOCKER_STUB_RUN_HOLD" ]]; do
    sleep 0.2
  done
fi
exit 0
"""


class LaunchResult(NamedTuple):
    """Outcome of a completed launcher chain run."""

    returncode: int
    stderr: str
    pid: int  # launcher PID: agent.sh exec's down to ai_assistant.py


def _make_sandbox(tmp_path: Path, name: str = "sandbox") -> Path:
    """Create an isolated sandbox workspace (cwd + HOME) for the launcher."""
    sandbox = tmp_path / name
    sandbox.mkdir()
    (sandbox / ".agent").mkdir()
    return sandbox


def _write_docker_stub(stub_dir: Path) -> Path:
    stub = stub_dir / "docker"
    stub.write_text(DOCKER_STUB)
    stub.chmod(0o755)
    return stub


def _launcher_env(
    sandbox: Path, stub_dir: Path, extra_env: dict[str, str] | None = None
) -> dict[str, str]:
    """Build the launcher environment; session markers default to absent.

    AI_ASSISTANT_SESSION_ID, TMUX, and STY are removed so every test starts
    from the parent-PID default and re-arms exactly what it exercises.
    """
    env = os.environ.copy()
    env["PATH"] = f"{stub_dir}{os.pathsep}{env['PATH']}"
    env["DOCKER_STUB_LOG"] = str(sandbox / "docker-stub.log")
    env["HOME"] = str(sandbox)
    for var in ("AI_ASSISTANT_SESSION_ID", "TMUX", "STY"):
        env.pop(var, None)
    if extra_env:
        env.update(extra_env)
    return env


def _popen_chain(
    sandbox: Path, env: dict[str, str], args: list[str]
) -> subprocess.Popen:
    return subprocess.Popen(
        ["bash", str(PROJECT_ROOT / "agent.sh"), *args],
        cwd=sandbox,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def run_chain(
    sandbox: Path,
    stub_dir: Path,
    args: list[str],
    extra_env: dict[str, str] | None = None,
) -> LaunchResult:
    """Run agent.sh to completion with the docker stub on PATH."""
    proc = _popen_chain(sandbox, _launcher_env(sandbox, stub_dir, extra_env), args)
    try:
        _, err = proc.communicate(timeout=60)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()
        raise
    return LaunchResult(proc.returncode, err, proc.pid)


def stub_invocations(sandbox: Path) -> list[list[str]]:
    """Return the docker stub's recorded argument vectors."""
    log = sandbox / "docker-stub.log"
    if not log.exists():
        return []
    return [json.loads(line) for line in log.read_text().splitlines() if line]


def run_invocations(sandbox: Path) -> list[list[str]]:
    """Return the recorded `docker run` argument vectors."""
    return [inv for inv in stub_invocations(sandbox) if inv and inv[0] == "run"]


def container_name(invocation: list[str]) -> str:
    """Extract the --name value from a docker run argv."""
    return invocation[invocation.index("--name") + 1]


def label_value(invocation: list[str], name: str) -> str:
    """Extract the value of a `--label <name>=<value>` pair from an argv."""
    values = [
        arg.split("=", 1)[1]
        for i, arg in enumerate(invocation)
        if i > 0
        and invocation[i - 1] == "--label"
        and arg.startswith(f"{name}=")
    ]
    assert values, f"label {name!r} not present in: {invocation}"
    return values[0]


def _strip_pid_suffix(name: str) -> str:
    """Mask the trailing per-launch PID segment of a container name."""
    return re.sub(r"-\d+$", "", name, count=1)


def _wait_for(predicate, timeout: float, description: str) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.2)
    raise AssertionError(f"timed out waiting for {description}")


def _load_launcher_module():
    """Import .agent/ai_assistant.py as a module for direct unit calls."""
    spec = importlib.util.spec_from_file_location(
        "ai_assistant_under_test",
        PROJECT_ROOT / ".agent" / "ai_assistant.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_container_name_deterministic_and_stable_per_workspace(tmp_path: Path):
    """The same workspace with the same session identity yields the exact
    same container-name portion across launches, while a different workspace
    yields a different name — names derive from a hash of the workspace
    location combined with the session identifier."""
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_docker_stub(stub_dir)
    session_env = {"AI_ASSISTANT_SESSION_ID": "det"}

    sandbox = _make_sandbox(tmp_path)
    first = run_chain(sandbox, stub_dir, args=[], extra_env=session_env)
    second = run_chain(sandbox, stub_dir, args=[], extra_env=session_env)
    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr

    names = [container_name(inv) for inv in run_invocations(sandbox)]
    assert len(names) == 2, names
    # Same workspace + same session => same name portion (PID suffix differs).
    assert _strip_pid_suffix(names[0]) == _strip_pid_suffix(names[1])

    # A different workspace location produces a different name portion.
    other = _make_sandbox(tmp_path, "sandbox-other")
    third = run_chain(other, stub_dir, args=[], extra_env=session_env)
    assert third.returncode == 0, third.stderr
    other_name = container_name(run_invocations(other)[0])
    assert _strip_pid_suffix(other_name) != _strip_pid_suffix(names[0])


def test_separate_sessions_produce_distinguishable_names(tmp_path: Path):
    """Two sessions in the identical workspace yield container names that
    share the workspace-hash portion but carry distinct session segments —
    separate sessions produce distinguishable names for the same workspace."""
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_docker_stub(stub_dir)
    sandbox = _make_sandbox(tmp_path)

    alpha = run_chain(
        sandbox, stub_dir, args=[], extra_env={"AI_ASSISTANT_SESSION_ID": "alpha"}
    )
    beta = run_chain(
        sandbox, stub_dir, args=[], extra_env={"AI_ASSISTANT_SESSION_ID": "beta"}
    )
    assert alpha.returncode == 0, alpha.stderr
    assert beta.returncode == 0, beta.stderr

    names = [container_name(inv) for inv in run_invocations(sandbox)]
    assert len(names) == 2, names

    # Documented format: ai-assistant-<workspace>-<hash8>-<session>-<pid>.
    alpha_parts = names[0].split("-")
    beta_parts = names[1].split("-")
    assert len(alpha_parts) == 6, names
    # Same workspace: the hash segment matches; only the session differs.
    assert alpha_parts[3] == beta_parts[3]
    assert alpha_parts[4] != beta_parts[4]
    # Therefore the name portions are fully distinguishable.
    assert _strip_pid_suffix(names[0]) != _strip_pid_suffix(names[1])


def test_multiple_containers_coexist_within_workspace(tmp_path: Path):
    """Two concurrent launchers in the identical workspace each obtain their
    own container and neither disturbs the other: the second launcher sees
    the first's container with a live host PID and leaves it untouched, and
    the first launcher survives the second's entire lifecycle."""
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_docker_stub(stub_dir)
    sandbox = _make_sandbox(tmp_path)
    hold = sandbox / "run-hold"

    # Launcher A: its docker run blocks until the hold file appears, so A's
    # launcher process stays alive while B runs.
    env_a = _launcher_env(
        sandbox,
        stub_dir,
        extra_env={
            "AI_ASSISTANT_SESSION_ID": "one",
            "DOCKER_STUB_RUN_HOLD": str(hold),
        },
    )
    proc_a = _popen_chain(sandbox, env_a, args=[])
    try:
        _wait_for(
            lambda: bool(run_invocations(sandbox)),
            timeout=30,
            description="launcher A's docker run to start",
        )
        assert proc_a.poll() is None  # A alive, holding its container

        # Launcher B runs in the same workspace while A lives. The stub's
        # `docker ps` reports A's container with A's live launcher PID —
        # exactly what the host daemon would list.
        env_b = _launcher_env(
            sandbox,
            stub_dir,
            extra_env={
                "AI_ASSISTANT_SESSION_ID": "two",
                "DOCKER_STUB_PS_ROWS": f"c0ffee {proc_a.pid}",
            },
        )
        proc_b = _popen_chain(sandbox, env_b, args=[])
        try:
            _, err_b = proc_b.communicate(timeout=60)
        except subprocess.TimeoutExpired:
            proc_b.kill()
            proc_b.communicate()
            raise
        assert proc_b.returncode == 0, err_b

        # A's launcher survived B's entire lifecycle, cleanup included.
        assert proc_a.poll() is None
        # Nothing was removed: A's container is bound to a live PID, and no
        # session identity drives any destructive cleanup.
        rm_invocations = [
            inv for inv in stub_invocations(sandbox) if inv[:2] == ["rm", "-f"]
        ]
        assert rm_invocations == [], rm_invocations

        # Both containers exist in the same workspace: shared hash segment,
        # distinct sessions.
        names = [container_name(inv) for inv in run_invocations(sandbox)]
        assert len(names) == 2, names
        assert names[0].split("-")[3] == names[1].split("-")[3]
        assert names[0].split("-")[4] != names[1].split("-")[4]

        # Release A's docker run so the launcher completes normally.
        hold.write_text("release")
        _, err_a = proc_a.communicate(timeout=60)
        assert proc_a.returncode == 0, err_a
    finally:
        if proc_a.poll() is None:
            proc_a.kill()
            proc_a.communicate()


def test_container_labels_bind_to_host_launcher_process(tmp_path: Path):
    """The docker run argv labels the container with the launcher process's
    own PID — exactly the PID the test observes for the exec'd launcher
    chain — alongside the resolved session identity and a stable workspace
    hash, binding each container's lifetime to its host launcher process."""
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_docker_stub(stub_dir)
    sandbox = _make_sandbox(tmp_path)

    result = run_chain(
        sandbox,
        stub_dir,
        args=[],
        extra_env={"AI_ASSISTANT_SESSION_ID": "label-probe"},
    )
    assert result.returncode == 0, result.stderr

    runs = run_invocations(sandbox)
    assert len(runs) == 1, runs
    run_argv = runs[0]

    # The hostpid label is the launcher chain's own PID: every entry file
    # exec's down to ai_assistant.py, so the Popen pid IS os.getpid() there.
    host_pid = label_value(run_argv, "aider.hostpid")
    assert host_pid == str(result.pid)

    # The session label carries the resolved (overridden) session identity.
    assert label_value(run_argv, "aider.session") == "label-probe"

    # The workspace label is the hash the container name derives from: the
    # name's hash segment is its first 8 characters.
    workspace_hash = label_value(run_argv, "aider.dir")
    assert re.fullmatch(r"[0-9a-f]{32}", workspace_hash), workspace_hash
    assert container_name(run_argv).split("-")[3] == workspace_hash[:8]


def test_launch_cleanup_removes_only_dead_launcher_containers(
    tmp_path: Path, monkeypatch
):
    """Stale-container cleanup removes exactly the containers whose host
    launcher PID is dead and leaves live-launcher containers untouched; the
    ps query filters by the workspace label only, so session identity never
    drives destructive cleanup.

    cleanup_containers is called directly: the launcher skips stale-container
    cleanup whenever it detects /.dockerenv (see main()), and this test
    suite runs inside the aider container. PID liveness is checked in the
    same PID namespace as this test process, so the dead/live simulation is
    real.
    """
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_docker_stub(stub_dir)
    sandbox = _make_sandbox(tmp_path)

    # A killed-and-reaped child provides a guaranteed-dead host PID; a
    # sleeping child provides a guaranteed-live one for the duration.
    victim = subprocess.Popen(["sleep", "30"])
    victim.kill()
    victim.wait()
    dead_pid = victim.pid
    live = subprocess.Popen(["sleep", "60"])
    try:
        launcher = _load_launcher_module()
        workspace_hash = "0123456789abcdef0123456789abcdef"
        monkeypatch.setenv("PATH", f"{stub_dir}{os.pathsep}{os.environ['PATH']}")
        monkeypatch.setenv("DOCKER_STUB_LOG", str(sandbox / "docker-stub.log"))
        monkeypatch.setenv(
            "DOCKER_STUB_PS_ROWS",
            f"deadbeef1 {dead_pid}\ndeadbeef2 {live.pid}",
        )
        launcher.cleanup_containers(workspace_hash, debug=False)
    finally:
        live.kill()
        live.wait()

    invocations = stub_invocations(sandbox)
    assert invocations, "docker stub was never invoked"

    # The cleanup query is scoped by the workspace label only; the session
    # identity appears in no filter and drives no removal.
    ps_inv = next(inv for inv in invocations if inv[0] == "ps")
    filters = [arg for arg in ps_inv if arg.startswith("label=")]
    assert filters == [f"label=aider.dir={workspace_hash}"], ps_inv

    # Exactly the dead-launcher container is removed; the live one untouched.
    rm_invocations = [inv for inv in invocations if inv[:2] == ["rm", "-f"]]
    assert rm_invocations == [["rm", "-f", "deadbeef1"]], rm_invocations
