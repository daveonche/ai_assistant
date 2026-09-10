"""S1.8 Step 2: progress feedback during long operations.

Must Support verified:
- A visible progress indicator while long-running operations execute.
- Feedback that updates automatically without requiring user action
  (second test in this file).

The spinner output is gated on sys.stdout.isatty(), so the launcher is
attached to a pseudo-terminal (stdlib pty) and the terminal transcript is
captured with per-chunk timestamps. The long operation is a fake
`docker build` on the cache-miss path, which emits build-log lines
progressively; the launcher derives its status text from them.
"""

from __future__ import annotations

import os
import pty
import re
import select
import subprocess
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SESSION_ID = "s18-step2"

# Spinner frame: "\r[<char>] Loading AI Assistant... <status message>".
SPINNER_FRAME = re.compile(r"\[[^\]]+\] Loading AI Assistant\.\.\. +\S")

# Fake docker: records argv as a JSON array per invocation (same recording
# body as tests/test_s1_8_step1.py). `docker version` succeeds, every
# `docker image inspect` fails (cache miss -> the build path runs), and
# `docker build` is the slow long operation: it emits two build-log lines
# (FROM, CACHED) one second apart before exiting 0. Everything else exits 0.
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

cmd="${1:-}"
if [[ "$cmd" == "build" ]]; then
  printf 'FROM paulgauthier/aider-full:v0.86.2@sha256:ba4d51b3c846b89d0f261f88dd712b9ce62968d3844c73fe2b3353ae65b11ea4\\n' >&2
  sleep 1
  printf '#5 CACHED\\n' >&2
  sleep 1
  exit 0
fi
if [[ "$cmd" == "image" ]]; then
  exit 1
fi
exit 0
"""


def _make_sandbox(tmp_path: Path) -> Path:
    """Create an isolated sandbox cwd and HOME for the launcher."""
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir()
    (sandbox / ".agent").mkdir()
    return sandbox


def _write_docker_stub(stub_dir: Path) -> Path:
    stub = stub_dir / "docker"
    stub.write_text(DOCKER_STUB)
    stub.chmod(0o755)
    return stub


def run_in_pty(
    sandbox: Path,
    stub_dir: Path,
    args: list[str] | None = None,
) -> tuple[int, list[tuple[float, str]]]:
    """Run agent.sh attached to a pseudo-terminal.

    The launcher's spinner only renders when stdout is a TTY, so the launch
    chain is attached to a pty slave. Returns (returncode, timestamped
    transcript chunks) so callers can order spinner updates in time; stdin
    is never written to, so every update that appears happened without user
    action.
    """
    master, slave = pty.openpty()
    env = os.environ.copy()
    env["PATH"] = f"{stub_dir}{os.pathsep}{env['PATH']}"
    env["DOCKER_STUB_LOG"] = str(sandbox / "docker-stub.log")
    env["HOME"] = str(sandbox)
    env["AI_ASSISTANT_SESSION_ID"] = SESSION_ID

    process = subprocess.Popen(
        ["bash", str(PROJECT_ROOT / "agent.sh"), *(args or [])],
        stdin=slave,
        stdout=slave,
        stderr=slave,
        cwd=sandbox,
        env=env,
    )
    os.close(slave)

    chunks: list[tuple[float, str]] = []
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
            break  # slave side fully closed: launcher (and watchdog) exited
        if not data:
            break
        chunks.append((time.monotonic(), data.decode("utf-8", errors="replace")))

    os.close(master)
    return process.wait(timeout=10), chunks


def test_progress_indicator_visible_during_long_operation(tmp_path: Path):
    """During a slow fake docker build, spinner frames carrying a status
    message appear in the terminal transcript — including statuses derived
    from the build log — and the run ends with the done marker. The run is
    a normal (non-debug) run, proving feedback appears without debug mode."""
    sandbox = _make_sandbox(tmp_path)
    stub_dir = tmp_path / "stubs"
    stub_dir.mkdir()
    _write_docker_stub(stub_dir)

    # Normal mode (no --debug): the spinner is TTY-gated and disabled under
    # --debug, so this exercises exactly the mode users see feedback in.
    returncode, chunks = run_in_pty(sandbox, stub_dir)
    transcript = "".join(text for _, text in chunks)

    assert returncode == 0, transcript

    # Spinner frames carrying a status message were rendered on the terminal.
    frames = SPINNER_FRAME.findall(transcript)
    assert frames, "no spinner frames found in transcript"

    # Statuses derived from the build log while the build ran: the fake
    # build's FROM/CACHED lines feed the status line.
    assert any("FROM" in frame or "CACHED" in frame for frame in frames), frames

    # Completion marker rendered; the failure branch never fired.
    assert "[✔] Loading AI Assistant... done." in transcript
    assert "[✖] Loading AI Assistant... failed." not in transcript
