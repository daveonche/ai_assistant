"""Security-audit reproducer: planted object at the agent socket path.

Reproducer for audit Finding 2 in .agent/ai-assistant.sh: an object a
local attacker plants at the well-known agent socket path must not be
able to abort the launcher (a persistent denial of service under
`set -e`), and must never lead to a hostile socket being exported.

Two variants are covered:
- a directory planted before the launch (the reported exploit): the
  initial socket check must skip gracefully, and
- the race variant: the socket is swapped for a directory after the
  initial check, so the cleanup `rm -f` fails and must be tolerated
  instead of killing the launch.

The launcher runs attached to a pseudo-terminal (stdlib pty) because
agent setup is TTY-gated; python3 and the ssh tooling are stubbed so
only the launcher's bash logic runs.
"""

from __future__ import annotations

import os
import pty
import select
import socket
import subprocess
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# python3 stub: records argv and whether SSH_AUTH_SOCK was exported,
# then exits 0 so the launcher completes without the real assistant.
PYTHON3_STUB = """\
#!/usr/bin/env bash
set -euo pipefail
# python3 stub: log argv and SSH_AUTH_SOCK state, then exit 0.
log="${PYTHON3_STUB_LOG:?}"
{
  printf 'argv'
  printf ' %s' "$@"
  printf '\\n'
} >> "$log"
if [[ -n "${SSH_AUTH_SOCK:-}" ]]; then
  printf 'SSH_AUTH_SOCK=%s\\n' "$SSH_AUTH_SOCK" >> "$log"
else
  printf 'SSH_AUTH_SOCK_UNSET\\n' >> "$log"
fi
exit 0
"""

# ssh-add stub: `-l` probes answer "cannot connect" (exit 2, like the
# real ssh-add against a dead path). In swap-dir mode the probe first
# replaces the socket at the well-known path with a directory,
# simulating an attacker planting an unremovable object mid-launch.
SSH_ADD_STUB = """\
#!/usr/bin/env bash
set -euo pipefail
# ssh-add stub: optional swap-dir plant on `-l`, then always exit 2.
log="${SSH_ADD_STUB_LOG:?}"
printf 'ssh-add argv:%s\\n' "$(printf ' %s' "$@")" >> "$log"
if [[ "${1:-}" == "-l" && "${SSH_ADD_STUB_MODE:-}" == "swap-dir" ]]; then
  rm -f "$AGENT_SOCK_PATH" 2>/dev/null || true
  mkdir "$AGENT_SOCK_PATH" 2>/dev/null || true
fi
exit 2
"""

# ssh-agent stub: never binds (exit 1, like "address in use"), so any
# bind attempt is treated as a failure by the launcher.
SSH_AGENT_STUB = """\
#!/usr/bin/env bash
set -euo pipefail
# ssh-agent stub: log argv, then fail to bind.
log="${SSH_AGENT_STUB_LOG:?}"
printf 'ssh-agent argv:%s\\n' "$(printf ' %s' "$@")" >> "$log"
exit 1
"""


def _make_sandbox(tmp_path: Path) -> Path:
    """Create an isolated sandbox cwd and HOME for the launcher."""
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir()
    (sandbox / ".agent").mkdir()
    # The launcher's agent setup is gated on $HOME/.ssh existing.
    (sandbox / ".ssh").mkdir()
    (sandbox / "runtime").mkdir()
    return sandbox


def _agent_sock_path(sandbox: Path) -> Path:
    """The well-known socket path derived from the sandbox runtime dir."""
    return sandbox / "runtime" / f"ssh-agent-{os.getuid()}.sock"


def _write_stubs(stub_dir: Path) -> None:
    """Write the PATH stubs standing in for python3 and the ssh tooling."""
    stubs = {
        "python3": PYTHON3_STUB,
        "ssh-add": SSH_ADD_STUB,
        "ssh-agent": SSH_AGENT_STUB,
    }
    for name, body in stubs.items():
        stub = stub_dir / name
        stub.write_text(body)
        stub.chmod(0o755)


def _plant_stale_socket(sock_path: Path) -> None:
    """Bind and close a unix socket, leaving a stale uid-owned socket file."""
    sock = socket.socket(socket.AF_UNIX)
    try:
        sock.bind(str(sock_path))
    finally:
        sock.close()


def run_launcher(
    sandbox: Path, stub_dir: Path, mode: str
) -> subprocess.CompletedProcess:
    """Run agent.sh attached to a pseudo-terminal.

    The launcher's agent setup only runs when stdin/stdout are TTYs, so
    the launch chain is attached to a pty slave. Returns the
    CompletedProcess with the terminal transcript as stdout; stdin is
    never written to.
    """
    master, slave = pty.openpty()
    env = os.environ.copy()
    env["PATH"] = f"{stub_dir}{os.pathsep}{env['PATH']}"
    env["HOME"] = str(sandbox)
    env["XDG_RUNTIME_DIR"] = str(sandbox / "runtime")
    env.pop("SSH_AUTH_SOCK", None)
    env["PYTHON3_STUB_LOG"] = str(sandbox / "python3-stub.log")
    env["SSH_ADD_STUB_LOG"] = str(sandbox / "ssh-add-stub.log")
    env["SSH_AGENT_STUB_LOG"] = str(sandbox / "ssh-agent-stub.log")
    env["AGENT_SOCK_PATH"] = str(_agent_sock_path(sandbox))
    env["SSH_ADD_STUB_MODE"] = mode

    process = subprocess.Popen(
        ["bash", str(PROJECT_ROOT / "agent.sh")],
        stdin=slave,
        stdout=slave,
        stderr=slave,
        cwd=sandbox,
        env=env,
    )
    os.close(slave)

    transcript: list[str] = []
    deadline = time.monotonic() + 30
    while True:
        if time.monotonic() > deadline:
            process.kill()
            process.wait(timeout=10)
            os.close(master)
            raise AssertionError("launcher did not finish within 30s")
        ready, _, _ = select.select([master], [], [], 0.05)
        if not ready:
            if process.poll() is not None:
                break
            continue
        try:
            data = os.read(master, 4096)
        except OSError:
            break  # slave side fully closed: launcher exited
        if not data:
            break
        transcript.append(data.decode("utf-8", errors="replace"))

    # Drain output still buffered after the process exited so transcript
    # assertions cannot race the final read.
    while True:
        ready, _, _ = select.select([master], [], [], 0.05)
        if not ready:
            break
        try:
            data = os.read(master, 4096)
        except OSError:
            break
        if not data:
            break
        transcript.append(data.decode("utf-8", errors="replace"))

    os.close(master)
    returncode = process.wait(timeout=10)
    return subprocess.CompletedProcess([], returncode, "".join(transcript))


def test_planted_directory_does_not_abort_the_launch(tmp_path: Path):
    """A directory planted at the socket path before the launch (the
    reported sticky-/tmp DoS) must not abort the launcher: the launch
    completes, reaches the assistant, and exports no agent socket."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_stubs(stub_dir)
    _agent_sock_path(sandbox).mkdir()

    result = run_launcher(sandbox, stub_dir, "none")
    transcript = result.stdout

    assert result.returncode == 0, transcript
    python_log = (sandbox / "python3-stub.log").read_text()
    assert "SSH_AUTH_SOCK_UNSET" in python_log, python_log
    assert "SSH_AUTH_SOCK=" not in python_log, python_log
    # The launch was skipped deliberately, not by a crash.
    assert "not a trusted agent socket" in transcript, transcript


def test_socket_swapped_for_directory_mid_launch_still_completes(
    tmp_path: Path,
):
    """The race variant: the socket is replaced by a directory after the
    initial ownership check, so the cleanup rm -f fails. The failure
    must be tolerated — the launcher still completes and exports no
    agent socket — instead of aborting under set -e."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_stubs(stub_dir)
    # Trusted at the initial check: a stale socket owned by this uid.
    _plant_stale_socket(_agent_sock_path(sandbox))

    result = run_launcher(sandbox, stub_dir, "swap-dir")
    transcript = result.stdout

    assert result.returncode == 0, transcript
    # The swap happened mid-launch: the path now holds a directory.
    assert _agent_sock_path(sandbox).is_dir(), transcript
    python_log = (sandbox / "python3-stub.log").read_text()
    assert "SSH_AUTH_SOCK_UNSET" in python_log, python_log
    assert "SSH_AUTH_SOCK=" not in python_log, python_log
    # The tolerated-rm path was reached: the bind attempt followed it
    # and failed (the stubbed ssh-agent never binds).
    assert "ssh-agent failed on" in transcript, transcript
