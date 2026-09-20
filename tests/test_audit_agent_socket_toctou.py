"""Security-audit reproducer: agent-socket TOCTOU before key offering.

Reproducer for audit Finding 1 in .agent/ai-assistant.sh: a fake SSH
agent planted at the well-known socket path after the launcher's
ownership check must never receive the decrypted private key from the
key-offering ssh-add, and the hostile socket must not be exported into
the container.

The race is made deterministic: the ssh-add stub plants the fake agent
socket and arms the stat stub (marker file) during the launcher's first
`ssh-add -l` probe — after the initial ownership check but before the
key-offering ssh-add. The stat stub then reports the planted socket as
owned by another uid, standing in for the other local user of the
original attack. The launcher runs attached to a pseudo-terminal
(stdlib pty) because agent setup is TTY-gated, and python3 is stubbed
so only the launcher's bash logic runs.
"""

from __future__ import annotations

import os
import pty
import select
import shlex
import socket
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Uid the stat stub reports for the planted socket ("another local
# user"); must differ from the uid the tests run as.
FOREIGN_UID = 1001

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

# ssh-add stub: `-l` probes drive the race. In lure mode a probe plants
# a fake agent socket at the well-known path, arms the stat stub, and
# answers "no identities" (exit 1) exactly like a luring fake agent. A
# key-offering invocation (no arguments) is recorded as KEYS_OFFERED —
# the theft signal this test forbids.
SSH_ADD_STUB = """\
#!/usr/bin/env bash
set -euo pipefail
# ssh-add stub: `-l` probes drive the planted-socket race; a
# key-offering invocation (no arguments) is recorded as KEYS_OFFERED.
log="${SSH_ADD_STUB_LOG:?}"
printf 'ssh-add argv:%s\\n' "$(printf ' %s' "$@")" >> "$log"
if [[ "${1:-}" == "-l" && "${SSH_ADD_STUB_MODE:-}" == "lure" ]]; then
  # Plant the fake agent: replace the socket, arm the stat stub.
  rm -f "$AGENT_SOCK_PATH"
  __PYTHON__ -c 'import socket, sys
s = socket.socket(socket.AF_UNIX)
s.bind(sys.argv[1])
' "$AGENT_SOCK_PATH"
  touch "$SOCKET_RACE_MARKER"
  exit 1
fi
if [[ "${1:-}" != "-l" ]]; then
  printf 'KEYS_OFFERED\\n' >> "$log"
fi
exit 0
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

# stat stub: once the race marker exists, report the agent socket as
# owned by the foreign uid; otherwise defer to the real stat binary.
STAT_STUB = """\
#!/usr/bin/env bash
set -euo pipefail
# stat stub: report the agent socket as foreign once the marker exists.
if [[ "${1:-}" == "-c" && "${3:-}" == "$AGENT_SOCK_PATH" ]] \\
  && [[ -n "${SOCKET_RACE_MARKER:-}" && -e "$SOCKET_RACE_MARKER" ]]; then
  printf '%s\\n' "$FOREIGN_UID"
  exit 0
fi
for real in /usr/bin/stat /bin/stat; do
  if [[ -x "$real" ]]; then
    exec "$real" "$@"
  fi
done
exit 127
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
    """Write the PATH stubs that stand in for python3/ssh tooling/stat."""
    stubs = {
        "python3": PYTHON3_STUB,
        "ssh-add": SSH_ADD_STUB.replace("__PYTHON__", shlex.quote(sys.executable)),
        "ssh-agent": SSH_AGENT_STUB,
        "stat": STAT_STUB,
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


def run_launcher(sandbox: Path, stub_dir: Path) -> subprocess.CompletedProcess:
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
    env["SOCKET_RACE_MARKER"] = str(sandbox / "race-marker")
    env["SSH_ADD_STUB_MODE"] = "lure"
    env["FOREIGN_UID"] = str(FOREIGN_UID)

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


def test_planted_socket_receives_no_keys_and_is_not_exported(tmp_path: Path):
    """A fake agent planted between the ownership check and the
    key-offering ssh-add receives no key material, and the launcher
    still completes with no SSH_AUTH_SOCK exported to the assistant."""
    assert FOREIGN_UID != os.getuid()
    sandbox = _make_sandbox(tmp_path)
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_stubs(stub_dir)
    # Trusted at the initial check: a stale socket owned by this uid.
    _plant_stale_socket(_agent_sock_path(sandbox))

    result = run_launcher(sandbox, stub_dir)
    transcript = result.stdout

    assert result.returncode == 0, transcript

    # The race happened: the fake agent was planted during the first
    # probe and the stat stub now reports a foreign owner.
    assert (sandbox / "race-marker").exists(), transcript
    assert _agent_sock_path(sandbox).exists(), transcript

    # The assistant was reached with no agent socket exported.
    python_log = (sandbox / "python3-stub.log").read_text()
    assert "SSH_AUTH_SOCK_UNSET" in python_log, python_log
    assert "SSH_AUTH_SOCK=" not in python_log, python_log

    # No key-offering ssh-add ran: no decrypted private key was handed
    # to the planted socket.
    ssh_add_log = (sandbox / "ssh-add-stub.log").read_text()
    assert "KEYS_OFFERED" not in ssh_add_log, ssh_add_log

    # The launcher said why it skipped: the socket was not trusted.
    assert "not a trusted agent socket" in transcript, transcript
