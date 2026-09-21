"""Security-audit reproducer: agent-socket bootstrap in ai-assistant.sh.

Companion to the Finding 1/2 socket tests: covers the launcher's
bootstrap path for a *missing* socket. Before the bootstrap change the
launcher treated an absent well-known socket the same as an untrusted
one and skipped setup in every fresh terminal; after it, a fresh agent
is started — but only when the parent directory is private (owned by
this uid, not group/other-writable), so the world-writable /tmp
fallback and any pre-existing object at the path stay fail-closed.

Covered here:
- happy path: absent socket in a private runtime dir → the launcher
  starts an agent at the well-known path, offers the default keys to
  it exactly once, and exports SSH_AUTH_SOCK to the assistant;
- fallback: an unbootstrappable runtime dir (group/other-writable;
  stands in for the WSL2 root-owned case, which cannot be simulated
  without root) → the launcher falls back to the private
  ~/.cache/aider-agent dir, starts the agent there, and leaves the
  well-known path untouched;
- negative: a pre-existing non-private cache dir must fail closed —
  no agent started anywhere, no socket exported, skip warning.

The launcher runs attached to a pseudo-terminal (stdlib pty) because
agent setup is TTY-gated; python3 and the ssh tooling are stubbed so
only the launcher's bash logic runs.
"""

from __future__ import annotations

import os
import pty
import select
import shlex
import subprocess
import sys
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

# ssh-add stub: before the agent stub has bound, `-l` answers "cannot
# connect" (exit 2, like the real ssh-add against a dead path);
# afterwards "agent alive, no identities" (exit 1). A key-offering
# invocation (no arguments) is recorded as KEYS_OFFERED.
SSH_ADD_STUB = """\
#!/usr/bin/env bash
set -euo pipefail
# ssh-add stub: `-l` probes depend on the agent-bound marker; a
# key-offering invocation (no arguments) is recorded as KEYS_OFFERED.
log="${SSH_ADD_STUB_LOG:?}"
printf 'ssh-add argv:%s\\n' "$(printf ' %s' "$@")" >> "$log"
if [[ "${1:-}" == "-l" ]]; then
  if [[ -e "${AGENT_BOUND_MARKER:-}" ]]; then
    exit 1
  fi
  exit 2
fi
printf 'KEYS_OFFERED\\n' >> "$log"
exit 0
"""

# ssh-agent stub: binds a (stale) unix socket at the requested path,
# marks it bound, and exits 0 like a successful `ssh-agent -a`. The
# launcher only ever probes the socket through the ssh-add stub, so a
# listener is not needed.
SSH_AGENT_STUB = """\
#!/usr/bin/env bash
set -euo pipefail
# ssh-agent stub: bind a socket at the requested path, mark it bound.
log="${SSH_AGENT_STUB_LOG:?}"
printf 'ssh-agent argv:%s\\n' "$(printf ' %s' "$@")" >> "$log"
__PYTHON__ -c 'import socket, sys
s = socket.socket(socket.AF_UNIX)
s.bind(sys.argv[1])
' "$2"
touch "${AGENT_BOUND_MARKER:?}"
exit 0
"""


def _make_sandbox(tmp_path: Path) -> Path:
    """Create an isolated sandbox cwd and HOME for the launcher."""
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir()
    (sandbox / ".agent").mkdir()
    # The launcher's agent setup is gated on $HOME/.ssh existing.
    (sandbox / ".ssh").mkdir()
    # ~/.cache must exist for the cache-dir fallback gate (the launcher
    # never creates ~/.cache itself, mirroring a real HOME).
    (sandbox / ".cache").mkdir()
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
        "ssh-agent": SSH_AGENT_STUB.replace(
            "__PYTHON__", shlex.quote(sys.executable)
        ),
    }
    for name, body in stubs.items():
        stub = stub_dir / name
        stub.write_text(body)
        stub.chmod(0o755)


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
    env["AGENT_BOUND_MARKER"] = str(sandbox / "agent-bound-marker")

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


def test_absent_socket_in_private_runtime_dir_is_bootstrapped(tmp_path: Path):
    """With nothing at the well-known path (the fresh-terminal case) and
    a private runtime dir, the launcher starts a fresh agent there,
    offers the default keys to it exactly once, and exports the socket
    to the assistant — instead of skipping with a warning."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_stubs(stub_dir)

    result = run_launcher(sandbox, stub_dir)
    transcript = result.stdout

    assert result.returncode == 0, transcript
    # A fresh agent was started at the well-known path...
    agent_log = (sandbox / "ssh-agent-stub.log").read_text()
    assert str(_agent_sock_path(sandbox)) in agent_log, agent_log
    assert _agent_sock_path(sandbox).is_socket(), transcript
    # ...the default keys were offered to it exactly once...
    ssh_add_log = (sandbox / "ssh-add-stub.log").read_text()
    assert ssh_add_log.count("KEYS_OFFERED") == 1, ssh_add_log
    # ...and the socket was exported to the assistant.
    python_log = (sandbox / "python3-stub.log").read_text()
    assert "SSH_AUTH_SOCK=" in python_log, python_log
    assert "SSH_AUTH_SOCK_UNSET" not in python_log, python_log
    # Setup succeeded deliberately: no skip warning was emitted.
    assert "not a trusted agent socket" not in transcript, transcript


def test_unbootstrappable_runtime_dir_falls_back_to_cache_dir(tmp_path: Path):
    """A group/other-writable runtime dir (stands in for the WSL2
    root-owned runtime dir, which cannot be simulated without root)
    must not be bootstrapped — but the launcher falls back to the
    private ~/.cache/aider-agent dir, starts the agent there, offers
    the default keys once, and exports the fallback socket. The
    well-known path is never touched."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_stubs(stub_dir)
    (sandbox / "runtime").chmod(0o777)
    cache_sock = sandbox / ".cache" / "aider-agent" / (
        f"ssh-agent-{os.getuid()}.sock"
    )

    result = run_launcher(sandbox, stub_dir)
    transcript = result.stdout

    assert result.returncode == 0, transcript
    # The fallback was announced...
    assert "not usable as an agent socket dir" in transcript, transcript
    # ...the agent was started in the cache dir...
    agent_log = (sandbox / "ssh-agent-stub.log").read_text()
    assert str(cache_sock) in agent_log, agent_log
    assert cache_sock.is_socket(), transcript
    # ...the well-known path stayed untouched...
    assert not _agent_sock_path(sandbox).exists(), transcript
    # ...the keys were offered exactly once, and the fallback socket
    # was exported to the assistant.
    ssh_add_log = (sandbox / "ssh-add-stub.log").read_text()
    assert ssh_add_log.count("KEYS_OFFERED") == 1, ssh_add_log
    python_log = (sandbox / "python3-stub.log").read_text()
    assert f"SSH_AUTH_SOCK={cache_sock}" in python_log, python_log
    assert "SSH_AUTH_SOCK_UNSET" not in python_log, python_log
    assert "not a trusted agent socket" not in transcript, transcript


def test_non_private_cache_dir_fails_closed(tmp_path: Path):
    """A pre-existing cache dir that is not fully private (drwx------)
    must fail closed: no agent started anywhere, no keys offered, no
    socket exported, and the launch still completes with the skip
    warning."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_stubs(stub_dir)
    (sandbox / "runtime").chmod(0o777)
    cache_dir = sandbox / ".cache" / "aider-agent"
    cache_dir.mkdir(parents=True)
    cache_dir.chmod(0o755)

    result = run_launcher(sandbox, stub_dir)
    transcript = result.stdout

    assert result.returncode == 0, transcript
    python_log = (sandbox / "python3-stub.log").read_text()
    assert "SSH_AUTH_SOCK_UNSET" in python_log, python_log
    assert "SSH_AUTH_SOCK=" not in python_log, python_log
    # The ssh tooling was never invoked: nothing was started or offered.
    assert not (sandbox / "ssh-agent-stub.log").exists(), transcript
    assert not (sandbox / "ssh-add-stub.log").exists(), transcript
    # The launch was skipped deliberately, not by a crash.
    assert "not a trusted agent socket" in transcript, transcript
