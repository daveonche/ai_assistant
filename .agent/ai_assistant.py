#!/usr/bin/env python3
"""Launch an AI assistant in a Docker container.

This module provides a command-line interface equivalent to the previous
ai-assistant.sh script. It handles optional Docker image builds, container
cleanup, and running the assistant in a Docker container with workspace
isolation, audio support, and Docker-outside-of-Docker capabilities.

When installed as part of the `.agent` directory, this script keeps all
helper files, the Docker build context, and all caches inside `.agent`,
while the project root is bind-mounted into the container at the identical
path and used as the container working directory. Two invariants follow
from this design:

1. Aider can read and edit application source code anywhere under the
   project root, because the root is mounted at the same path it has on
   the host.
2. `docker` / `docker compose` commands run from inside the container
   operate on the host daemon via the mounted docker.sock, and any
   bind-mount paths in compose files resolve correctly because the project
   root path is identical inside and outside the container.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import threading
import time
from collections import deque
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

TOOL_NAME = "ai-assistant"
AIDER_IMAGE = "aider-agent:latest"
BASE_IMAGE_FALLBACK = "paulgauthier/aider-full:latest"
SESSION_ID_ENV_VAR = "AI_ASSISTANT_SESSION_ID"

# Pre-flight gitdb probe. Aider reads the repository through GitPython and
# gitdb (pure Python), not the git binary, and gitdb can fail with
# "BadObject" on repositories the git binary reads cleanly — observed with
# a few thousand fragmented loose objects. When the loose-object count
# reaches this threshold, a one-shot container re-reads the repository with
# the image's own gitdb before launch and warns with the remediation
# instead of letting aider fail mid-launch. Detection only: the probe
# mounts the repository read-only, repairs nothing, and never fails the
# launch. The gate targets the observed failure mode; a stale pack index
# with few loose objects is not detected.
LOOSE_OBJECT_PROBE_THRESHOLD = 1024

# Seconds before the one-shot gitdb probe container is abandoned as
# inconclusive. Container startup dominates; the probe itself only reads
# object headers.
GITDB_PROBE_TIMEOUT = 60

# The probe program, delivered to the container's venv interpreter on
# stdin so the traced command stays a single line. It exercises the gitdb
# read paths aider uses: resolving HEAD, walking HEAD's tree, and
# streaming every index entry's object. Exit codes: 0 healthy (or nothing
# to probe), 2 gitdb could not read an object, 3 the probe itself could
# not run.
GITDB_PROBE_SNIPPET = """\
import binascii
import stat
import sys

try:
    import git
except Exception as exc:
    print(f"probe-error: GitPython import failed: {exc}")
    sys.exit(3)

try:
    repo = git.Repo(".")
except Exception:
    print("probe-ok: not a git repository")
    sys.exit(0)

if repo.bare:
    print("probe-ok: bare repository")
    sys.exit(0)

try:
    head = repo.head.commit
except Exception:
    print("probe-ok: no commits on HEAD")
    sys.exit(0)

errors = []
try:
    head.tree.traverse()
except Exception as exc:
    errors.append(f"HEAD tree walk: {exc!r}")

EMPTY_BLOB = binascii.unhexlify(
    "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"
)
try:
    if repo.index.exists():
        for entry in repo.index.entries.values():
            if stat.S_ISGITLINK(entry.mode):
                continue  # submodule pointers live in the submodule's odb
            if entry.binsha == EMPTY_BLOB:
                continue  # intent-to-add entries may be unwritten
            repo.odb.stream(entry.binsha).close()
except Exception as exc:
    errors.append(f"index object read: {exc!r}")

if errors:
    for error in errors:
        print(f"probe-bad-object: {error}")
    sys.exit(2)
print("probe-ok")
"""

# Per-session engine-command log. Configured once in main() from the
# workspace hash + session ID; every traced command is appended so runs
# stay auditable regardless of debug mode. None until configured.
COMMAND_LOG_PATH: Optional[Path] = None

# How many recent command-log lines to surface at failure checkpoints.
COMMAND_LOG_TAIL_LINES = 10

# Well-known provider credential variables forwarded from the host
# environment into the container by name only (docker run -e VAR). Docker
# fills the value from the launcher process's own environment, so secrets
# never appear in commands or their debug traces (see run_container).
CREDENTIAL_ENV_VARS = (
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "OPENROUTER_API_KEY",
    "AZURE_API_KEY",
    "DEEPSEEK_API_KEY",
    "GROQ_API_KEY",
    "MISTRAL_API_KEY",
    "COHERE_API_KEY",
    "TOGETHER_API_KEY",
    "HF_TOKEN",
)

# LLM endpoint variables. Repo-supplied values (.env files) are never
# allowed to set these: a hostile checkout could repoint a forwarded
# provider credential at an attacker-controlled server (see
# run_container). Host-exported values are forwarded after --env-file
# (host wins); repo-only values are neutralized to empty. Names follow
# the litellm/provider conventions for the CREDENTIAL_ENV_VARS providers.
ENDPOINT_ENV_VARS = (
    "OPENAI_API_BASE",
    "OPENAI_BASE_URL",
    "ANTHROPIC_API_BASE",
    "ANTHROPIC_BASE_URL",
    "AZURE_API_BASE",
    "AZURE_OPENAI_ENDPOINT",
    "DEEPSEEK_API_BASE",
    "GROQ_API_BASE",
    "MISTRAL_API_BASE",
    "COHERE_API_BASE",
    "TOGETHER_API_BASE",
    "GOOGLE_GEMINI_BASE_URL",
    "HF_ENDPOINT",
)

# GitHub's published SSH host keys and their officially published SHA256
# fingerprints. The rsa key is not pinned (too long to embed safely);
# modern clients negotiate GitHub's ed25519 host key first. A key is
# appended to the host known_hosts only when its computed fingerprint
# matches the published one, so a tampered source can never inject a
# host key (see _ensure_github_known_hosts).
GITHUB_ED25519_KEY = (
    "AAAAC3NzaC1lZDI1NTE5AAAAIOMqqnkVzrm0SdG6UOoqKLsabg"
    "H5C9okWi0dh2l9GKJl"
)
GITHUB_ECDSA_KEY = (
    "AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAA"
    "BBBEmKSENjQEezOmxkZMy7opKgwFB9nkt5YRrYMjNuG5N87uRg"
    "g6CLrbo5wAdT/y6v0mKV0U2w0WZ2YB/++Tpockg="
)
GITHUB_ED25519_FINGERPRINT = (
    "SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU"
)
GITHUB_ECDSA_FINGERPRINT = (
    "SHA256:p2QAMXNIC1TJYWeIOttrVc98/R1BUFWu3/LiyKgUfQM"
)

ANSI_RED = "\033[31m"
ANSI_GREEN = "\033[32m"
ANSI_RESET = "\033[0m"
SPIN_CHARS = ["-", "\\", "|", "/", "."]

LOG_RE = re.compile(
    r"(?:RUN|COPY|FROM|Installing|Extracting|Downloading|Unpacking|"
    r"Setting up|Get:|added|CACHED|ERROR|error).*"
)

AGENT_DIR = Path(__file__).resolve().parent

DOCKERIGNORE_CONTENT = """\
# Auto-generated by ai_assistant.py.
# The Dockerfile performs no COPY instructions, so the build context is kept
# minimal (just the Dockerfile) to make builds fast on large projects.
# If you add COPY instructions, whitelist the required files below.
*
!Dockerfile.aider
"""


def _remove_if_empty(path: Path) -> None:
    """Remove a file or directory if it exists and is empty."""
    try:
        if path.is_dir():
            if not any(path.iterdir()):
                path.rmdir()
        elif path.is_file() and path.stat().st_size == 0:
            path.unlink()
    except OSError:
        pass


def _cleanup_empty_artifacts(project_root: Path, agent_dir: Path) -> None:
    """Remove known launcher artifacts that are empty after a session.

    Conservative by design: only the launcher's own artifact paths are
    checked, never a repository-wide scan. Artifacts left by an abnormally
    killed launcher are re-checked and removed at the next session's exit.
    Anything that contains content is left untouched (see _remove_if_empty).
    """
    _remove_if_empty(project_root / ".aider.tags.cache.v4")
    _remove_if_empty(agent_dir / ".aider.tags.cache.v4")
    _remove_if_empty(agent_dir / ".aider.chat.history.md")
    _remove_if_empty(agent_dir / ".aider.input.history")


def _docker_available(debug: bool = False) -> bool:
    """Return True when the docker CLI can be executed."""
    command = ["docker", "version"]
    try:
        _trace_command(command, debug)
        result = subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def _trace_command(command: list[str], debug: bool) -> None:
    """Append a command to the session log; print it when debug is enabled.

    Engine commands reference credential variables by name only (Docker
    fills the values from this process's environment; see run_container),
    so the log never contains secret values.
    """
    line = "+ " + " ".join(command)
    if COMMAND_LOG_PATH is not None:
        try:
            COMMAND_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            # 0600 on creation and afterwards: the log holds the session's
            # engine commands and must stay private to the launching user
            # (fchmod also tightens files created by older versions).
            # O_NOFOLLOW keeps the append on the real log file: a symlink
            # planted at the predictable path is never followed, and the
            # mode change lands on the opened file, not on a link target.
            fd = os.open(
                COMMAND_LOG_PATH,
                os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW,
                0o600,
            )
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, "a", encoding="utf-8") as log_file:
                log_file.write(line + "\n")
        except OSError:
            pass
    if debug:
        print(line, file=sys.stderr)


# Launcher-private cache directory name. Deliberately OUTSIDE the
# container-visible ~/.cache/aider mount (see run_container): the command
# log, the approved-Dockerfile hash, and the container-home cache must
# stay unwritable by the container they relate to.
LAUNCHER_CACHE_DIR_NAME = "aider-agent"

# File recording the Dockerfile hash at the last user-approved build.
APPROVED_DOCKERFILE_NAME = ".approved-dockerfile"


def _launcher_cache_dir() -> Path:
    """Return the launcher-private cache directory."""
    return Path.home() / ".cache" / LAUNCHER_CACHE_DIR_NAME


def _configure_command_log(workspace_hash: str, session_id: str) -> Path:
    """Point the command log at a per-session file in the user's cache.

    The log lives under the user-private ~/.cache/aider-agent directory
    (created 0700) instead of a shared temp directory, so another local
    user cannot plant a symlink at the guessable path in the first place.
    The directory is also outside the container-visible ~/.cache/aider
    mount (see run_container), so an in-container session cannot rewrite
    the audit log of the launch that ran it. The file name is derived
    from the workspace hash and session ID, so the location is stable
    for a given session. The file is created on first write and appended
    to afterwards, never truncated.
    """
    global COMMAND_LOG_PATH
    cache_dir = _launcher_cache_dir()
    try:
        cache_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    except OSError:
        pass
    COMMAND_LOG_PATH = (
        cache_dir / f"ai-assistant-{workspace_hash[:8]}-{session_id}.log"
    )
    return COMMAND_LOG_PATH


def _dump_recent_log_lines(debug: bool) -> None:
    """Surface the most recent command-log entries when debug is enabled."""
    if not debug or COMMAND_LOG_PATH is None:
        return
    recent = _tail_lines(COMMAND_LOG_PATH, COMMAND_LOG_TAIL_LINES)
    if not recent:
        return
    print("--- Recent command log entries ---", file=sys.stderr)
    for line in recent:
        print(line, file=sys.stderr)


def _tail_lines(path: Path, count: int) -> list[str]:
    """Return up to the last count lines from a text file."""
    try:
        lines = path.read_text(errors="replace").splitlines()
    except FileNotFoundError:
        return []
    return lines[-count:] if count > 0 else lines


def _print_spinner_update(char: str, message: str) -> None:
    """Print a single-line spinner status update when stdout is a TTY."""
    if not sys.stdout.isatty():
        return
    sys.stdout.write(f"\r[{char}] Loading AI Assistant... {message:<50}")
    sys.stdout.flush()


def _spin_worker(message: str, stop_event: threading.Event) -> None:
    """Animate the spinner until stop_event is set."""
    spin_index = 0
    while True:
        char = SPIN_CHARS[spin_index % len(SPIN_CHARS)]
        _print_spinner_update(char, message)
        spin_index += 1
        if stop_event.wait(0.25):
            break


@contextmanager
def _spinner(message: str, debug: bool = False) -> Iterator[None]:
    """Show a single-line spinner while the wrapped operation runs.

    The spinner animates on a daemon thread and only when stdout is a
    TTY; it is skipped in debug mode so traced commands print cleanly.
    """
    active = not debug and sys.stdout.isatty()
    stop_event = threading.Event()
    thread = threading.Thread(
        target=_spin_worker,
        args=(message, stop_event),
        daemon=True,
    )
    if active:
        thread.start()
    try:
        yield
    finally:
        stop_event.set()
        if thread.is_alive():
            thread.join()
        if active:
            # Overwrite the spinner line with spaces, then return the
            # cursor to the start of the line.
            sys.stdout.write("\r" + " " * 80 + "\r")
            sys.stdout.flush()


def _get_docker_gid() -> Optional[int]:
    """Return the Docker group GID, or None when the group is unavailable."""
    try:
        import grp
        return grp.getgrnam("docker").gr_gid
    except (KeyError, ImportError):
        return None


def _atomic_write_text(path: Path, text: str) -> None:
    """Write text to path without following a symlink planted there.

    Writes a temporary file in the destination directory and renames it
    over the destination: os.replace() swaps the directory entry itself,
    so a symlink at path is replaced rather than followed and the bytes
    never reach the link target. The temporary file is created 0600 by
    mkstemp and removed again if the write or rename fails.
    """
    fd, temp_name = tempfile.mkstemp(
        dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            try:
                os.unlink(temp_name)
            except OSError:
                pass


def _aider_config_args(agent_dir: Path) -> list[str]:
    """Return Aider CLI flags for config files stored in agent_dir."""
    args: list[str] = []

    config_file = agent_dir / ".aider.conf.yml"
    if config_file.exists():
        args.extend(["--config", str(config_file)])

    model_settings_file = agent_dir / ".aider.model.settings.yml"
    if model_settings_file.exists():
        args.extend(["--model-settings-file", str(model_settings_file)])

    aiderignore_file = agent_dir / ".aiderignore"
    if aiderignore_file.exists():
        args.extend(["--aiderignore", str(aiderignore_file)])

    model_metadata_file = agent_dir / ".aider.model.metadata.json"
    if model_metadata_file.exists():
        args.extend(["--model-metadata-file", str(model_metadata_file)])

    return args


# Per-project args files live under ~/.config/aider-agent/projects/:
# user-authored configuration in the home config area — outside any
# repository and outside the launcher cache — so repository content can
# never create or alter them, and they survive assistant updates (see
# _project_args_path and _load_project_args).
PROJECT_ARGS_DIR_NAME = "aider-agent"


def _project_args_path(project_root: Path, workspace_hash: str) -> Path:
    """Return the per-project args-file path for this project.

    Keyed to the project's identity with the same workspace-hash formula
    as the command log (md5 of the project path plus a newline, first 8
    hex characters; see main()), so the path is stable across launches
    from the same project directory.
    """
    file_name = f"{project_root.name}-{workspace_hash[:8]}.args"
    return Path.home() / ".config" / PROJECT_ARGS_DIR_NAME / "projects" / file_name


def _load_project_args(path: Path) -> list[str]:
    """Return the assistant argument tokens stored in a project args file.

    One token per line: surrounding whitespace is stripped, blank lines
    and lines starting with '#' are ignored, and every remaining line is
    taken verbatim — no quote removal, no variable expansion, no command-
    interpreter interpretation — so entries stay predictable. An
    unreadable file yields no tokens; the launch continues without them.
    """
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    tokens: list[str] = []
    for line in lines:
        entry = line.strip()
        if not entry or entry.startswith("#"):
            continue
        tokens.append(entry)
    return tokens


# Template written by --init-project-args (see _init_project_args). Every
# line is a comment, so a freshly created file loads as zero arguments;
# users uncomment the entries they want.
PROJECT_ARGS_TEMPLATE = """\
# Per-project assistant arguments
#
# This file adds arguments to every assistant launch for this project
# directory. It lives in your home configuration area, outside any
# repository, so repository content can never create or alter it, and it
# survives assistant updates.
#
# Format: one argument token per line. Blank lines and lines starting
# with '#' are ignored. Entries are taken verbatim: no quotes, no
# variable expansion, no shell interpretation. A value that contains
# spaces goes on its own line after its flag.
#
# Precedence: arguments you type on the command line win over entries in
# this file, which win over the assistant's own defaults in .agent/.
#
# Simple flags — uncomment to enable; they apply on every launch:
#
#   --dark-mode
#
#   --test-cmd
#   python -m pytest -q
#
#   --lint-cmd
#   ruff check .
#
# File overrides — replace the assistant's own file entirely, so use them
# only when this project genuinely needs extra or different
# configurations; otherwise leave them commented out so the assistant's
# own copy stays in force. When you do override:
#
#   1. Reference a file under a distinctive name unlikely to exist in any
#      repository: a hostile repository could ship a same-named file that
#      silently satisfies the reference.
#   2. Create that file in the project root and copy the needed entries
#      from the assistant's own copy (.agent/.aider.model.settings.yml or
#      .agent/.aiderignore) so the override is self-sufficient.
#
#   --model-settings-file
#   my-project-model-settings.yml
#
#   --aiderignore
#   my-project-aiderignore
"""


def _init_project_args(project_root: Path, workspace_hash: str) -> int:
    """Create the per-project args file from the template, or report it.

    The file is created exclusively ('x' mode) after its parent directory
    is made, so an existing file is never overwritten or modified: the
    existing file is reported and left untouched. Returns a process exit
    code: 0 when the file exists afterwards (freshly created or
    pre-existing), 1 when the template cannot be written.
    """
    path = _project_args_path(project_root, workspace_hash)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8") as handle:
            handle.write(PROJECT_ARGS_TEMPLATE)
    except FileExistsError:
        print(f"Project args file already exists; left unchanged: {path}")
        return 0
    except OSError as exc:
        print(f"Warning: could not create {path}: {exc}", file=sys.stderr)
        return 1
    print(f"Created the per-project args file: {path}")
    return 0


def _show_project_config(project_root: Path, workspace_hash: str) -> int:
    """Print the effective per-project configuration for this project.

    The single command that answers "what configuration is actually in
    effect for this project": the args-file path, its contents verbatim
    (or a clear absence notice pointing at --init-project-args), and the
    effective argument order — typed command-line arguments win over file
    entries, which win over the assistant-directory defaults. Returns a
    process exit code (0; the display never fails the launch).
    """
    path = _project_args_path(project_root, workspace_hash)
    print(f"Project args file: {path}")
    if path.exists():
        try:
            contents = path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"Warning: cannot read {path}: {exc}", file=sys.stderr)
        else:
            print("Contents:")
            print(contents.rstrip("\n"))
    else:
        print("Not found; create it with --init-project-args")
    print(
        "Effective argument order: typed command-line arguments win over "
        "file entries, which win over the assistant's own defaults in "
        ".agent/."
    )
    return 0


# Project-root configuration filenames the launcher deliberately ignores.
# Existence is checked only to tell the user why their files have no
# effect; contents are never read (see _notice_root_config_files).
ROOT_CONFIG_FILENAMES = (
    ".aider.conf.yml",
    ".aider.model.settings.yml",
    ".aiderignore",
    ".aider.model.metadata.json",
)


def _notice_root_config_files(project_root: Path) -> None:
    """Point at --init-project-args when root config files are present.

    Repository configuration files the launcher deliberately ignores would
    otherwise fail silently: a repository ships .aider.conf.yml, the user
    expects it to apply, and nothing happens. For each known filename that
    exists in the project root, one line states the file is not read and
    points at the per-project args file as the supported alternative.
    Existence is tested only (is_file); file contents are never read.
    Prints nothing when no such files exist.
    """
    for name in ROOT_CONFIG_FILENAMES:
        if (project_root / name).is_file():
            print(
                f"Notice: {name} exists in the project root but is not "
                "read; customize per-project with --init-project-args"
            )


def _base_repo_digests(image: str, debug: bool = False) -> str:
    """Return local repo digests for an image, or "" when unknown."""
    command = [
        "docker",
        "image",
        "inspect",
        "--format",
        "{{range .RepoDigests}}{{.}} {{end}}",
        image,
    ]
    try:
        _trace_command(command, debug)
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return ""
    if result.returncode != 0:
        return ""
    return (result.stdout or "").strip()


def _base_image(dockerfile_path: Path) -> str:
    """Extract the FROM image reference from a Dockerfile."""
    try:
        for line in dockerfile_path.read_text(errors="replace").splitlines():
            stripped = line.strip()
            if stripped.upper().startswith("FROM"):
                for token in stripped.split()[1:]:
                    if not token.startswith("--"):
                        return token
    except OSError:
        pass
    return BASE_IMAGE_FALLBACK


def _image_cache_tag(dockerfile_path: Path, debug: bool = False) -> str:
    """Return a content-hash tag for the built image.

    Combines the Dockerfile bytes with the base image's repo digests, so the
    cache tag changes (triggering a rebuild) whenever either the Dockerfile
    or the upstream base image changes. Before the first local pull the base
    contributes "" to the hash; after a successful build the tag is
    recomputed and refreshed (see main()).
    """
    hasher = hashlib.sha256()
    try:
        hasher.update(dockerfile_path.read_bytes())
    except OSError:
        pass
    hasher.update(_base_repo_digests(_base_image(dockerfile_path), debug).encode())
    return f"aider-agent:c-{hasher.hexdigest()[:16]}"


def _dockerfile_hash(dockerfile_path: Path) -> str:
    """Return the sha256 of the Dockerfile bytes ("" when unreadable)."""
    try:
        return hashlib.sha256(dockerfile_path.read_bytes()).hexdigest()
    except OSError:
        return ""


def _approved_dockerfile_hash() -> str:
    """Return the Dockerfile hash recorded at the last approved build."""
    try:
        approved = _launcher_cache_dir() / APPROVED_DOCKERFILE_NAME
        return approved.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def _record_approved_dockerfile(dockerfile_path: Path) -> None:
    """Record the Dockerfile hash as approved after a successful build."""
    try:
        cache_dir = _launcher_cache_dir()
        cache_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        approved = cache_dir / APPROVED_DOCKERFILE_NAME
        approved.write_text(
            _dockerfile_hash(dockerfile_path) + "\n", encoding="utf-8"
        )
    except OSError:
        pass


def _rebuild_approved(dockerfile_path: Path, debug: bool = False) -> bool:
    """Return True when building the repo-provided Dockerfile is allowed.

    The build executes instructions from the repo-writable Dockerfile, so
    a changed definition is rebuilt only with fresh user confirmation:
    the current Dockerfile hash is compared against the hash recorded at
    the last approved build, and a differing hash prompts on an
    interactive session. A first-time build (nothing approved yet) is
    not gated: prompting there would hang unattended launch chains whose
    stdin is never written (pty drivers, editor integrations); the hash
    is recorded on success, so every later change is gated. Non-
    interactive sessions (tests, CI) cannot prompt: the build proceeds
    after the visible warning, preserving automation behavior (documented
    residual risk).
    """
    approved = _approved_dockerfile_hash()
    if _dockerfile_hash(dockerfile_path) == approved:
        return True
    if not approved:
        print(
            f"Warning: {dockerfile_path} executes repo-provided build "
            "instructions; the build is recorded as approved on success.",
            file=sys.stderr,
        )
        return True
    print(
        f"Warning: {dockerfile_path} executes repo-provided build "
        "instructions and differs from the last approved build.",
        file=sys.stderr,
    )
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        if debug:
            print(
                "Note: non-interactive session; rebuild proceeding.",
                file=sys.stderr,
            )
        return True
    try:
        answer = input("Approve rebuild? [y/N] ")
    except (EOFError, KeyboardInterrupt):
        return False
    return answer.strip().lower() in ("y", "yes")


def _image_exists(tag: str, debug: bool = False) -> bool:
    """Return True when a local Docker image exists for the given tag."""
    command = ["docker", "image", "inspect", tag]
    try:
        _trace_command(command, debug)
        result = subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def _ensure_build_dockerignore(agent_dir: Path) -> None:
    """Create a minimal .dockerignore in agent_dir when one is missing."""
    target = agent_dir / ".dockerignore"
    if target.exists():
        return
    try:
        target.write_text(DOCKERIGNORE_CONTENT)
    except OSError:
        pass


def _warn_agent_dir_location(project_root: Path) -> None:
    """Warn when .agent is not inside the project root.

    The container bind-mounts the project root at the same path. Aider config
    and history paths (which live in .agent) only resolve inside the container
    when .agent is a subdirectory of the project root.
    """
    try:
        AGENT_DIR.relative_to(project_root)
    except ValueError:
        print(
            "Warning: the .agent directory is outside the project root; "
            "aider config and history files may not be visible inside the "
            "container.",
            file=sys.stderr,
        )


def _ssh_fingerprint(key_blob: str) -> Optional[str]:
    """Return the OpenSSH SHA256 fingerprint of a base64 key blob.

    Mirrors `ssh-keygen -lf` output: "SHA256:" plus unpadded base64 of
    the SHA256 digest over the decoded wire-format key blob.
    """
    try:
        decoded = base64.b64decode(key_blob, validate=True)
    except ValueError:
        return None
    digest = hashlib.sha256(decoded).digest()
    return "SHA256:" + base64.b64encode(digest).decode("ascii").rstrip("=")


def _ensure_github_known_hosts(debug: bool) -> None:
    """Pin GitHub's published SSH host keys in the host known_hosts file.

    Appends a key only when its computed SHA256 fingerprint matches the
    published fingerprint and the blob is not already present, so the
    file is never rewritten and a tampered source cannot inject a host
    key. Best-effort and non-fatal: failure only means ssh may prompt on
    the next push.
    """
    candidates = [
        ("ssh-ed25519", GITHUB_ED25519_KEY, GITHUB_ED25519_FINGERPRINT),
        ("ecdsa-sha2-nistp256", GITHUB_ECDSA_KEY, GITHUB_ECDSA_FINGERPRINT),
    ]
    ssh_dir = Path.home() / ".ssh"
    known_hosts = ssh_dir / "known_hosts"
    try:
        ssh_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        existing = (
            known_hosts.read_text(encoding="utf-8", errors="replace")
            if known_hosts.exists()
            else ""
        )
    except OSError as exc:
        print(f"Warning: cannot update {known_hosts}: {exc}", file=sys.stderr)
        return
    additions = [
        f"github.com {key_type} {blob}\n"
        for key_type, blob, fingerprint in candidates
        if _ssh_fingerprint(blob) == fingerprint and blob not in existing
    ]
    if not additions:
        return
    try:
        with known_hosts.open("a", encoding="utf-8") as handle:
            handle.writelines(additions)
    except OSError as exc:
        print(f"Warning: cannot update {known_hosts}: {exc}", file=sys.stderr)
        return
    if debug:
        print(
            f"Pinned {len(additions)} GitHub host key(s) in {known_hosts}.",
            file=sys.stderr,
        )


def _ensure_commit_msg_gate(project_root: Path, debug: bool) -> None:
    """Activate the repo's commit-msg gate when core.hooksPath is unset.

    Git never runs tracked hooks on its own: core.hooksPath is a local
    config value and deliberately not versioned, so a copied-in .githooks/
    directory stays inert until the value is set. Every launch therefore
    sets it to .githooks when the project root is a git worktree that
    ships the gate, applying the installer's policy: an existing value
    (husky, pre-commit, another gate) is never overwritten. The change
    is repo-local (.git/config only), so it applies identically inside
    and outside a container. Best-effort and non-fatal: a missing git
    binary or a failed config write only skips the activation, never the
    launch.
    """
    hook = project_root / ".githooks" / "commit-msg"
    if not hook.is_file() or not (project_root / ".git").exists():
        return
    if not os.access(hook, os.X_OK):
        print(
            f"Warning: {hook} is not executable, so the gate would stay "
            "inactive; fix with chmod +x .githooks/commit-msg and git "
            "update-index --chmod=+x .githooks/commit-msg.",
            file=sys.stderr,
        )
    get_command = ["git", "-C", str(project_root), "config", "core.hooksPath"]
    set_command = get_command + [".githooks"]
    try:
        _trace_command(get_command, debug)
        current = subprocess.run(get_command, capture_output=True, text=True)
        if current.returncode == 0:
            existing = (current.stdout or "").strip()
            if debug and existing != ".githooks":
                print(
                    f"Note: core.hooksPath is already {existing!r}; "
                    "leaving it untouched.",
                    file=sys.stderr,
                )
            return
        if current.returncode != 1:
            # Only "not set" (exit 1) may trigger a write; any other
            # status is a git error (e.g. a broken repository) and must
            # not be written to blind.
            if debug:
                print(
                    "Note: cannot read core.hooksPath ("
                    f"{(current.stderr or '').strip()}); gate not "
                    "activated.",
                    file=sys.stderr,
                )
            return
        _trace_command(set_command, debug)
        result = subprocess.run(set_command, capture_output=True, text=True)
    except FileNotFoundError:
        if debug:
            print(
                "Note: git is unavailable; commit-msg gate not activated.",
                file=sys.stderr,
            )
        return
    if result.returncode != 0:
        if debug:
            print(
                "Note: could not set core.hooksPath ("
                f"{(result.stderr or '').strip()}); gate not activated.",
                file=sys.stderr,
            )
        return
    print(
        "Note: commit-msg gate activated (git config core.hooksPath "
        ".githooks).",
        file=sys.stderr,
    )


def _valid_container_home(home: str) -> bool:
    """Return True when home is safe to embed in a bind-mount spec.

    The value is embedded as "{home}/.ssh" inside a -v argument, so a
    colon or whitespace would corrupt the mount spec (or inject extra
    mount fields); a poisoned cache entry must never reach docker run.
    """
    return (
        home.startswith("/")
        and home != "/"
        and ":" not in home
        and not any(char.isspace() for char in home)
    )


def _container_passwd_home(cache_tag: str, debug: bool) -> Optional[str]:
    """Return the passwd home directory of the runtime uid in the image.

    OpenSSH resolves default identity and known_hosts paths from the
    passwd home (pw_dir), not from $HOME, so the host ~/.ssh mount must
    target pw_dir for key authentication to work without explicit -i
    flags. The value is discovered with a one-shot container and cached
    in the host aider cache keyed by the image cache tag. Returns None
    when the lookup fails; the caller then keeps the legacy /home mount
    only.
    """
    cache_path = _launcher_cache_dir() / ".container-home"
    prefix = f"{cache_tag} "
    try:
        cached = cache_path.read_text(encoding="utf-8").splitlines()
        if cached and cached[0].startswith(prefix):
            home = cached[0][len(prefix):]
            if _valid_container_home(home):
                return home
    except OSError:
        pass
    uid = os.getuid()
    # --user mirrors real launches: the image's default USER may not exist in
    # /etc/passwd, which aborts the lookup ("unable to find user"). awk
    # matches the uid field (3rd), not the username field, so the passwd home
    # is found even when the account name differs from the uid string.
    command = [
        "docker",
        "run",
        "--rm",
        "--user",
        str(uid),
        "--entrypoint",
        "/bin/sh",
        AIDER_IMAGE,
        "-c",
        f"awk -F: -v u={uid} '$3 == u {{print $6}}' /etc/passwd",
    ]
    _trace_command(command, debug)
    try:
        result = subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        if debug:
            print(
                f"Note: could not query the container home: {exc}",
                file=sys.stderr,
            )
        return None
    home = (result.stdout or "").strip()
    if result.returncode != 0 or not _valid_container_home(home):
        if debug:
            print(
                f"Note: no passwd home for uid {uid} in {AIDER_IMAGE}; "
                "SSH keys will be mounted at /home/.ssh only.",
                file=sys.stderr,
            )
        return None
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(f"{cache_tag} {home}\n", encoding="utf-8")
    except OSError:
        pass
    return home


def _resolve_session_id() -> str:
    """Return the session identifier used for container naming and labels.

    Resolution order:
    1. The AI_ASSISTANT_SESSION_ID environment override, so any editor or
       shell can group multiple terminals into a single session.
    2. The tmux session identity (TMUX is shared by all panes of a session).
    3. The GNU screen session name (STY).
    4. The parent shell PID, giving each plain terminal its own session.

    Returns:
        A session identifier restricted to Docker's legal container-name
        characters, because the value is embedded in the container name.
    """
    override = os.environ.get(SESSION_ID_ENV_VAR)
    if override:
        raw = override
    elif os.environ.get("TMUX"):
        # TMUX holds "<socket>,<server-pid>,<session>,..." and is shared by
        # every pane attached to the same tmux session.
        raw = "tmux-" + os.environ["TMUX"]
    elif os.environ.get("STY"):
        raw = "screen-" + os.environ["STY"]
    else:
        raw = str(os.getppid())
    return re.sub(r"[^a-zA-Z0-9_.-]", "_", raw)


def _pid_alive(pid_text: str) -> bool:
    """Return True when the given host PID currently exists."""
    try:
        pid = int(pid_text)
    except (TypeError, ValueError):
        return False
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def _remove_container(container_ref: str, debug: bool = False) -> None:
    """Force-remove a container by name or ID. Missing containers are ignored."""
    command = ["docker", "rm", "-f", container_ref]
    try:
        _trace_command(command, debug)
        subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        pass


def _set_parent_death_signal(sig: int) -> None:
    """Ask the kernel to signal this process when its parent dies."""
    try:
        import ctypes

        libc = ctypes.CDLL("libc.so.6", use_errno=True)
        pr_set_pdeathsig = 1
        libc.prctl.argtypes = [ctypes.c_int, ctypes.c_ulong]
        libc.prctl.restype = ctypes.c_int
        libc.prctl(pr_set_pdeathsig, sig)
    except (OSError, AttributeError):
        pass


def _start_container_watchdog(container_name: str, debug: bool = False) -> int:
    """Fork a child that removes the container if this process dies.

    Uses PR_SET_PDEATHSIG so SIGKILL of the launcher still stops the
    container, and polls getppid() as a fallback when prctl is unavailable.
    """
    sys.stdout.flush()
    sys.stderr.flush()
    try:
        pid = os.fork()
    except OSError:
        return -1
    if pid > 0:
        return pid

    try:
        os.setsid()
    except OSError:
        try:
            os.setpgrp()
        except OSError:
            pass

    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    parent = os.getppid()
    _set_parent_death_signal(signal.SIGTERM)

    def _cleanup(_signum=None, _frame=None):
        _remove_container(container_name, debug)
        os._exit(0)

    signal.signal(signal.SIGTERM, _cleanup)
    if os.getppid() != parent or os.getppid() == 1:
        _cleanup()
    while True:
        time.sleep(1)
        if os.getppid() != parent or os.getppid() == 1:
            _cleanup()


def _stop_watchdog(watchdog_pid: int) -> None:
    """Terminate a watchdog child started by _start_container_watchdog."""
    if watchdog_pid <= 0:
        return
    try:
        os.kill(watchdog_pid, signal.SIGKILL)
    except OSError:
        pass
    try:
        os.waitpid(watchdog_pid, 0)
    except OSError:
        pass


def _running_in_container() -> bool:
    """Return True when this launcher is itself running inside a container.

    Docker creates /.dockerenv in every container it starts, so the file's
    presence is a reliable marker for a nested launcher invocation. From
    inside a container the host PID space is invisible, so stale-container
    cleanup must not run (see cleanup_containers).
    """
    return Path("/.dockerenv").exists()


def _loose_object_count(project_root: Path, debug: bool) -> Optional[int]:
    """Return the repository's loose-object count, or None when unknown.

    Reads only the "count:" line of git count-objects -v. The count gates
    the gitdb probe so ordinary launches pay nothing (see
    LOOSE_OBJECT_PROBE_THRESHOLD). Returns None when git is unavailable,
    the command fails, or the output cannot be parsed; the caller then
    skips the probe silently.
    """
    command = ["git", "-C", str(project_root), "count-objects", "-v"]
    _trace_command(command, debug)
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return None
    if result.returncode != 0:
        return None
    for line in (result.stdout or "").splitlines():
        if line.startswith("count:"):
            try:
                return int(line.split(":", 1)[1].strip())
            except ValueError:
                return None
    return None


def _probe_gitdb_reads(
    project_root: Path,
    image: str,
    debug: bool,
) -> Optional[list[str]]:
    """Re-read the repository with the image's gitdb, exactly as aider will.

    Runs a one-shot container (same pattern as _container_passwd_home) as
    the host uid, with the project root bind-mounted read-only at its
    identical path and no network, and feeds GITDB_PROBE_SNIPPET to the
    venv interpreter aider itself runs under. The probe program arrives on
    stdin so the traced command stays a single line.

    Returns an empty list when every gitdb read succeeded, the
    "probe-bad-object:" lines naming what failed when gitdb could not read
    an object, and None when the probe could not run or finished
    inconclusively (the caller stays silent for None outside debug mode).
    """
    command = [
        "docker",
        "run",
        "--rm",
        "-i",
        "--network",
        "none",
        "--user",
        str(os.getuid()),
        "-v",
        f"{project_root}:{project_root}:ro",
        "-w",
        str(project_root),
        "--entrypoint",
        "/venv/bin/python3",
        image,
        "-",
    ]
    _trace_command(command, debug)
    try:
        result = subprocess.run(
            command,
            input=GITDB_PROBE_SNIPPET,
            capture_output=True,
            text=True,
            timeout=GITDB_PROBE_TIMEOUT,
        )
    except FileNotFoundError:
        return None
    except subprocess.TimeoutExpired:
        if debug:
            print(
                "Note: gitdb probe timed out; treating as inconclusive.",
                file=sys.stderr,
            )
        return None
    if result.returncode == 0:
        if debug:
            print((result.stdout or "").strip(), file=sys.stderr)
        return []
    if result.returncode == 2:
        if debug:
            if (result.stdout or "").strip():
                print(result.stdout.strip(), file=sys.stderr)
            if (result.stderr or "").strip():
                print(result.stderr.strip(), file=sys.stderr)
        problems = [
            line
            for line in (result.stdout or "").splitlines()
            if line.startswith("probe-bad-object:")
        ]
        return problems or [
            "probe-bad-object: gitdb could not read the repository"
        ]
    if debug:
        print(
            "Note: gitdb probe exited with status "
            f"{result.returncode}; treating as inconclusive.",
            file=sys.stderr,
        )
    return None


def _live_session_pids(workspace_hash: str, debug: bool) -> list[int]:
    """Return host PIDs of assistant containers still live in this workspace.

    Same label query as cleanup_containers, but read-only: used only to
    adapt the gitdb warning when the repair command would be unsafe to
    run concurrently with a live session.
    """
    command = [
        "docker",
        "ps",
        "--filter",
        f"label=aider.dir={workspace_hash}",
        "--format",
        '{{.ID}} {{.Label "aider.hostpid"}}',
    ]
    _trace_command(command, debug)
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return []
    if result.returncode != 0:
        return []
    pids: list[int] = []
    for line in (result.stdout or "").splitlines():
        fields = line.split()
        if len(fields) < 2:
            continue
        if _pid_alive(fields[1]):
            pids.append(int(fields[1]))
    return pids


def _check_gitdb_reads(
    project_root: Path,
    workspace_hash: str,
    image: str,
    debug: bool,
) -> None:
    """Warn when the image's gitdb cannot read this repository.

    Gated by the loose-object count (see LOOSE_OBJECT_PROBE_THRESHOLD) so
    ordinary launches pay nothing; the gate targets the observed failure
    mode, heavy loose-object accumulation — a stale pack index with few
    loose objects is not detected. Skipped only for non-repositories:
    unlike cleanup_containers, the probe is read-only, needs no host PID
    space, and reaches the host daemon through the same docker.sock mount
    a nested launcher already uses, so it behaves identically inside and
    outside a container. On a failed probe the warning names the unreadable
    object and prints the remediation, mirroring
    agent_socket_report_blocker's diagnose-don't-mutate pattern: the
    launch continues either way, and the repair is deferred while another
    session is still live in this workspace.
    """
    if not (project_root / ".git").exists():
        return
    loose = _loose_object_count(project_root, debug)
    if loose is None or loose < LOOSE_OBJECT_PROBE_THRESHOLD:
        return
    if debug:
        print(
            f"Note: {loose} loose objects reach the probe threshold "
            f"({LOOSE_OBJECT_PROBE_THRESHOLD}); probing gitdb reads.",
            file=sys.stderr,
        )
    problems = _probe_gitdb_reads(project_root, image, debug)
    if not problems:
        # Healthy ([]), inconclusive, or unrunnable (None): stay silent.
        return
    print(
        "Warning: the Python object database (gitdb) inside the assistant "
        "image could not read this repository, although the git binary "
        'reads it fine; aider may fail with "BadObject" errors. The probe '
        "found:",
        file=sys.stderr,
    )
    for line in problems:
        print(f"  {line}", file=sys.stderr)
    live_pids = _live_session_pids(workspace_hash, debug)
    if live_pids:
        print(
            "Note: assistant session(s) with host pid(s) "
            f"{', '.join(str(pid) for pid in live_pids)} are still live in "
            "this workspace; close them before repairing, because a repack "
            "while aider reads the repository is one of the triggers this "
            "probe guards against.",
            file=sys.stderr,
        )
    else:
        print(
            "Fix while no assistant session is running in this workspace:",
            file=sys.stderr,
        )
    print("    git gc", file=sys.stderr)
    print(
        "then re-run the launcher. Do not add --prune=now: it discards "
        "objects that are still recoverable. If the warning persists "
        "after gc, update the pinned base image (docs/tech_stack.md) and "
        "report the sha upstream.",
        file=sys.stderr,
    )


def cleanup_containers(
    workspace_hash: str,
    debug: bool = False,
) -> None:
    """Remove leftover containers whose host launcher process is not alive.

    Live launchers in the same workspace are left running so multiple
    terminals can coexist. Session identity is not used for cleanup.

    Arguments:
        workspace_hash: Aider directory hash used as a Docker label.
        debug: Whether to print the underlying Docker commands to stderr.

    Returns:
        None
    """
    command = [
        "docker",
        "ps",
        "-a",
        "--filter",
        f"label=aider.dir={workspace_hash}",
        "--format",
        '{{.ID}} {{.Label "aider.hostpid"}}',
    ]
    try:
        _trace_command(command, debug)
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        print("Warning: unable to locate the Docker CLI.", file=sys.stderr)
        return

    if result.returncode != 0:
        warning = (result.stderr or "").strip()
        if warning:
            print(f"Warning: unable to list Docker containers: {warning}", file=sys.stderr)
        else:
            print(
                f"Warning: docker ps exited with status {result.returncode}.",
                file=sys.stderr,
            )
        return

    stale_ids = []
    for line in (result.stdout or "").splitlines():
        fields = line.split()
        if not fields:
            continue
        # Unlabeled leftovers (no hostpid) are treated as orphaned.
        host_pid = fields[1] if len(fields) > 1 else ""
        if not _pid_alive(host_pid):
            stale_ids.append(fields[0])
    for container_id in stale_ids:
        _remove_container(container_id, debug=debug)


def build_image(
    dockerfile_path: Path,
    context_dir: Path,
    debug: bool = False,
) -> int:
    """Build the Docker image with a progressive status indicator.

    Arguments:
        dockerfile_path: Path to the project Dockerfile.
        context_dir: Docker build context directory. The Dockerfile contains
            no COPY instructions, so a minimal context (the .agent directory)
            keeps builds fast even for very large projects.
        debug: Whether to print the underlying Docker command to stderr.

    Returns:
        0 on success, otherwise the Docker build exit code.
    """
    log_handle = tempfile.NamedTemporaryFile(
        mode="w",
        prefix="ai-assistant-build-",
        suffix=".log",
        delete=False,
    )
    log_path = Path(log_handle.name)
    log_handle.close()

    try:
        command = [
            "docker",
            "build",
            "--progress=plain",
            "-t",
            AIDER_IMAGE,
            "-f",
            str(dockerfile_path),
            str(context_dir),
        ]
        _trace_command(command, debug)

        env = os.environ.copy()
        env["DOCKER_BUILDKIT"] = "1"

        with log_path.open("w") as log_file:
            try:
                process = subprocess.Popen(
                    command,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    env=env,
                )
            except FileNotFoundError:
                print(
                    f"{ANSI_RED}Docker CLI not found while building image.{ANSI_RESET}",
                    file=sys.stderr,
                )
                return 127

            # Incremental log tail: read only newly appended bytes each tick
            # instead of re-reading and re-scanning the whole log file.
            spin_index = 0
            tail: deque[str] = deque(maxlen=40)
            reader = None
            try:
                reader = log_path.open("rb")
            except OSError:
                reader = None

            while process.poll() is None:
                if reader is not None:
                    chunk = reader.read()
                    if chunk:
                        tail.extend(
                            chunk.decode("utf-8", errors="replace").splitlines()
                        )

                status_message = ""
                if tail:
                    status_message = next(
                        (line for line in reversed(tail) if LOG_RE.search(line)),
                        "",
                    )[:45]
                if not status_message:
                    status_message = "Initializing build environment..."

                char = SPIN_CHARS[spin_index % len(SPIN_CHARS)]
                _print_spinner_update(char, status_message)

                spin_index += 1
                time.sleep(0.25)

            if reader is not None:
                reader.close()

            returncode = process.wait()

        if returncode != 0:
            if sys.stdout.isatty():
                sys.stdout.write(
                    f"\r[✖] Loading AI Assistant... failed.{' ':50}\n\n"
                )
                sys.stdout.flush()

            print(
                f"{ANSI_RED}--- Last lines of build log ---{ANSI_RESET}",
                file=sys.stderr,
            )
            for line in _tail_lines(log_path, 25):
                print(line, file=sys.stderr)
            print(
                f"{ANSI_RED}-----------------------------{ANSI_RESET}",
                file=sys.stderr,
            )
            return returncode

        # The fifty trailing spaces clear any remaining spinner text.
        if sys.stdout.isatty():
            sys.stdout.write(f"\r[✔] Loading AI Assistant... done.{' ':50}\n")
            sys.stdout.flush()
        return 0
    finally:
        try:
            log_path.unlink()
        except OSError:
            pass


def _repo_env_keys(env_file: Path) -> set[str]:
    """Return the variable names set by a repo .env file (names only).

    Values are never read; the names drive the endpoint neutralization in
    run_container (see ENDPOINT_ENV_VARS).
    """
    try:
        text = env_file.read_text(errors="replace")
    except OSError:
        return set()
    keys: set[str] = set()
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        keys.add(stripped.split("=", 1)[0].strip())
    return keys


def _sanitize_docker_config(host_docker_dir: Path, debug: bool) -> Optional[Path]:
    """Return a Docker config directory that works inside the container.

    Windows Docker Desktop writes "credsStore": "desktop.exe" into the host
    ~/.docker/config.json. That helper is a Windows binary, executable on
    the host only through WSL interop; inside the container every registry
    operation that consults it (resolving a build frontend, pulling a base
    image) fails with "executable file not found in $PATH". Helper entries
    ending in .exe are therefore dropped from a copy written to the
    launcher-private cache, and that copy is mounted at /home/.docker
    instead of the host directory. Inline "auths" credentials are kept, and
    the copy contains only config.json (other host-side files are not
    carried over).

    Returns the host directory unchanged when config.json is absent or
    references no .exe helper. Returns None when the config cannot be
    read, parsed, or copied: the caller then skips the mount entirely
    (fail closed — anonymous public pulls still work) rather than mount a
    config of unknown usability.
    """
    config_path = host_docker_dir / "config.json"
    try:
        doc = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return host_docker_dir
    except (OSError, ValueError) as exc:
        print(
            f"Warning: cannot parse {config_path} ({exc}); not mounting a "
            "Docker config into the container.",
            file=sys.stderr,
        )
        return None
    if not isinstance(doc, dict):
        print(
            f"Warning: {config_path} is not a JSON object; not mounting a "
            "Docker config into the container.",
            file=sys.stderr,
        )
        return None

    dropped: list[str] = []
    creds_store = doc.get("credsStore")
    if isinstance(creds_store, str) and creds_store.endswith(".exe"):
        del doc["credsStore"]
        dropped.append(creds_store)
    cred_helpers = doc.get("credHelpers")
    if isinstance(cred_helpers, dict):
        filtered = {
            registry: helper
            for registry, helper in cred_helpers.items()
            if not (isinstance(helper, str) and helper.endswith(".exe"))
        }
        dropped.extend(
            helper
            for helper in cred_helpers.values()
            if isinstance(helper, str) and helper.endswith(".exe")
        )
        if filtered:
            doc["credHelpers"] = filtered
        else:
            del doc["credHelpers"]
    if not dropped:
        return host_docker_dir

    try:
        cache_dir = _launcher_cache_dir()
        cache_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        sanitized_dir = cache_dir / "docker-config"
        sanitized_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        payload = json.dumps(doc, indent=2) + "\n"
        target = sanitized_dir / "config.json"
        existing = (
            target.read_text(encoding="utf-8") if target.exists() else None
        )
        if existing != payload:
            _atomic_write_text(target, payload)
    except OSError:
        print(
            "Warning: could not write the sanitized Docker config; not "
            "mounting a Docker config into the container.",
            file=sys.stderr,
        )
        return None
    print(
        "Note: dropped Windows-only credential helper(s) "
        f"{', '.join(sorted(set(dropped)))} from the Docker config mounted "
        "into the container; they cannot run there.",
        file=sys.stderr,
    )
    if debug:
        print(f"Sanitized Docker config: {sanitized_dir}", file=sys.stderr)
    return sanitized_dir


def run_container(
    workspace_hash: str,
    session_id: str,
    container_name: str,
    docker_gid: Optional[int],
    agent_dir: Path,
    container_home: Optional[str],
    debug: bool,
    assistant_args: list[str],
) -> int:
    """Run the AI assistant Docker container.

    Arguments:
        workspace_hash: Docker label for the workspace.
        session_id: Docker label for the session.
        container_name: Name to assign to the Docker container.
        docker_gid: Host Docker group GID to add to the container, or None.
        agent_dir: Directory containing the AI assistant helper files.
        container_home: Passwd home of the container user, or None when
            unknown; the host ~/.ssh directory is additionally mounted
            under it so ssh finds the forwarded keys by default.
        debug: Whether to print the underlying Docker command to stderr.
        assistant_args: Additional arguments passed to the AI assistant.

    Returns:
        The exit code of the docker run process.
    """
    uid = os.getuid()
    gid = os.getgid()
    home = str(Path.home())
    cwd = os.getcwd()
    pulse_user_dir = f"/run/user/{uid}/pulse/native"

    command = [
        "docker",
        "run",
        "-it",
        "--rm",
        "--name",
        container_name,
        "--label",
        f"aider.dir={workspace_hash}",
        "--label",
        f"aider.session={session_id}",
        "--label",
        f"aider.hostpid={os.getpid()}",
        "--user",
        f"{uid}:{gid}",
    ]

    if docker_gid is not None:
        command.extend(["--group-add", str(docker_gid)])
    else:
        print(
            "Warning: host 'docker' group not found; skipping --group-add. "
            "Docker commands inside the container may fail with permission "
            "errors.",
            file=sys.stderr,
        )

    if Path("/dev/snd").exists():
        command.extend([
            "--group-add",
            "audio",
            "--device",
            "/dev/snd",
        ])

    # Docker-outside-of-Docker prerequisite: mounting a nonexistent socket
    # path makes the daemon create an empty directory in its place, which
    # silently breaks engine access inside the container.
    if not Path("/var/run/docker.sock").exists():
        print(
            "Warning: /var/run/docker.sock does not exist on the host; "
            "Docker commands inside the container will fail (e.g. when the "
            "host reaches its daemon through DOCKER_HOST).",
            file=sys.stderr,
        )

    command.extend([
        # Docker-outside-of-Docker: the CLI and compose plugin inside the
        # container drive the host daemon through this socket, so compose
        # stacks started for debugging are siblings, not nested containers.
        "-v",
        "/var/run/docker.sock:/var/run/docker.sock",
        # Same-path bind mount is load-bearing: it gives aider access to the
        # application source code AND makes host paths in compose files and
        # aider config arguments resolve identically inside the container.
        "-v",
        f"{cwd}:{cwd}",
        "-w",
        cwd,
        # Lets the assistant reach ports published on the host (e.g. by
        # sibling compose stacks) via http://host.docker.internal:<port>.
        "--add-host",
        "host.docker.internal:host-gateway",
    ])

    bashrc = Path(home) / ".bashrc"
    gitconfig = Path(home) / ".gitconfig"
    docker_config = Path(home) / ".docker"
    cache_dir = Path(home) / ".cache" / "aider"
    cache_dir.mkdir(parents=True, exist_ok=True)

    if bashrc.exists():
        command.extend(["-v", f"{bashrc}:/home/.bashrc:ro"])

    if gitconfig.exists():
        command.extend(["-v", f"{gitconfig}:/home/.gitconfig:ro"])

    # Mounted read-only so `docker compose` inside the container can use the
    # host's registry credentials when pulling or building images. The
    # directory is sanitized first: credential helpers that cannot run
    # inside the container (Windows .exe helpers written by Docker Desktop)
    # are dropped, so registry operations never fail on a missing helper
    # (see _sanitize_docker_config). Buildx's mutable state is redirected
    # off this mount via BUILDX_CONFIG below.
    if docker_config.exists():
        effective_docker_config = _sanitize_docker_config(docker_config, debug)
        if effective_docker_config is not None:
            command.extend(
                ["-v", f"{effective_docker_config}:/home/.docker:ro"]
            )

    # Mounted read-only so git push/pull over SSH remotes works inside the
    # container: keys, config, and known_hosts travel together, and the
    # container can never modify the host's SSH state. OpenSSH resolves
    # default identity and known_hosts paths from the passwd home
    # (pw_dir), not from $HOME, so when the image user's home differs
    # from /home the same directory is mounted there as well; otherwise
    # ssh never sees the keys (observed as "Permission denied
    # (publickey)" despite HOME=/home).
    ssh_dir = Path(home) / ".ssh"
    if ssh_dir.is_dir():
        command.extend(["-v", f"{ssh_dir}:/home/.ssh:ro"])
        if container_home and container_home != "/home":
            command.extend(["-v", f"{ssh_dir}:{container_home}/.ssh:ro"])

    # Agent-forwarded SSH: mount the host agent socket at its identical
    # path so passphrase-protected keys work without copying them (same
    # pattern as the pulse socket mount). The variable is forwarded after
    # --env-file below so a project .env cannot disarm the forwarding.
    ssh_auth_sock = os.environ.get("SSH_AUTH_SOCK")
    if ssh_auth_sock and Path(ssh_auth_sock).exists():
        command.extend([
            "-v",
            f"{ssh_auth_sock}:{ssh_auth_sock}",
        ])

    command.extend(["-v", f"{cache_dir}:/home/.cache"])

    if Path(pulse_user_dir).exists():
        command.extend([
            "-v",
            f"{pulse_user_dir}:{pulse_user_dir}",
            "-e",
            f"PULSE_SERVER=unix:{pulse_user_dir}",
        ])

    command.extend(["-v", "/dev/shm:/dev/shm"])

    tags_cache_dir = agent_dir / ".aider.tags.cache.v4"
    tags_cache_dir.mkdir(parents=True, exist_ok=True)
    command.extend([
        "-v",
        f"{tags_cache_dir}:{cwd}/.aider.tags.cache.v4",
    ])

    project_root = Path(cwd)
    env_file = project_root / ".env"
    agent_env_file = agent_dir / ".env"

    effective_env_file: Optional[Path] = None
    if env_file.exists():
        command.extend(["--env-file", str(env_file)])
        effective_env_file = env_file
    elif agent_env_file.exists():
        command.extend(["--env-file", str(agent_env_file)])
        effective_env_file = agent_env_file

    # Environment forwards placed after --env-file so a project .env file
    # cannot override them (e.g. redirecting HOME or disarming SSH agent
    # forwarding). BUILDX_CONFIG: buildx keeps per-builder state under
    # $HOME/.docker/buildx, but /home/.docker is mounted read-only
    # (credentials only), which aborts in-container builds; point its
    # mutable state at the writable cache mount instead.
    command.extend([
        "-e",
        "HOME=/home",
        "-e",
        "PYTHONUNBUFFERED=1",
        "-e",
        "BUILDX_CONFIG=/home/.cache/buildx",
    ])
    if ssh_auth_sock and Path(ssh_auth_sock).exists():
        command.extend(["-e", "SSH_AUTH_SOCK"])

    # Forward host-exported credentials by name only: Docker fills the value
    # from this process's environment, so secrets never appear in the command
    # or its debug trace. Placed after --env-file so explicitly exported host
    # credentials take precedence over file defaults.
    for var in CREDENTIAL_ENV_VARS:
        if var in os.environ:
            command.extend(["-e", var])

    # LLM endpoints are never taken from repo files: a hostile checkout
    # could repoint a forwarded credential at an attacker-controlled
    # server. Host-exported endpoint values are forwarded (host wins over
    # --env-file); repo-only values are neutralized to empty so the
    # container falls back to the provider's default endpoint.
    for var in ENDPOINT_ENV_VARS:
        if var in os.environ:
            command.extend(["-e", var])
        elif (
            effective_env_file is not None
            and var in _repo_env_keys(effective_env_file)
        ):
            command.extend(["-e", f"{var}="])
            print(
                f"Warning: {effective_env_file} sets {var}; ignored because "
                "repo files cannot set LLM endpoints.",
                file=sys.stderr,
            )

    command.append(AIDER_IMAGE)
    command.extend(["--chat-mode", "ask"])

    # Configuration references point only at the assistant's own
    # configuration directory; repository content is never read for
    # configuration.
    command.extend(_aider_config_args(agent_dir))

    # Keep aider metadata inside .agent rather than the project root. These
    # paths resolve inside the container because agent_dir sits under the
    # bind-mounted project root (enforced by _warn_agent_dir_location).
    command.extend([
        "--chat-history-file",
        str(agent_dir / ".aider.chat.history.md"),
        "--input-history-file",
        str(agent_dir / ".aider.input.history"),
    ])

    command.extend(assistant_args)

    _trace_command(command, debug)

    watchdog_pid = _start_container_watchdog(container_name, debug)
    try:
        try:
            return subprocess.run(command).returncode
        except FileNotFoundError:
            print(
                "Error: Docker CLI not found while starting assistant.",
                file=sys.stderr,
            )
            _dump_recent_log_lines(debug)
            return 127
        except KeyboardInterrupt:
            _remove_container(container_name, debug)
            return 130
    finally:
        _stop_watchdog(watchdog_pid)


def main() -> int:
    """Orchestrate the AI assistant launch."""
    assistant_args = sys.argv[1:]
    debug = False

    while assistant_args and assistant_args[0] in ("-x", "--debug"):
        debug = True
        assistant_args.pop(0)

    init_project_args = False
    while assistant_args and assistant_args[0] == "--init-project-args":
        init_project_args = True
        assistant_args.pop(0)

    show_project_config = False
    while assistant_args and assistant_args[0] == "--show-project-config":
        show_project_config = True
        assistant_args.pop(0)

    if os.name != "posix":
        print("This assistant currently supports Linux only.", file=sys.stderr)
        return 1

    # Configure the command log before the first engine command runs so the
    # Docker availability check is recorded too.
    project_root = Path.cwd()
    dir_name = project_root.name
    workspace_hash = hashlib.md5((str(project_root) + "\n").encode()).hexdigest()

    # --init-project-args and --show-project-config only write and read the
    # args file, so they are handled before any container interaction
    # (including the Docker availability check) and return without
    # launching: the flags work even when container tooling is unavailable.
    if init_project_args:
        return _init_project_args(project_root, workspace_hash)
    if show_project_config:
        return _show_project_config(project_root, workspace_hash)

    session_id = _resolve_session_id()
    command_log = _configure_command_log(workspace_hash, session_id)
    if debug:
        print(f"Command log: {command_log}", file=sys.stderr)

    # Per-project args file: host-side, outside any repository, keyed to
    # the project identity (same hash formula as the command log). Its
    # tokens are prepended so explicitly typed CLI arguments, which appear
    # later in the final assistant command, win over file entries. The
    # launcher's own -x/--debug flags were popped above, so file entries
    # can never toggle launcher debug mode.
    project_args_path = _project_args_path(project_root, workspace_hash)
    project_args = _load_project_args(project_args_path)
    if sys.stdout.isatty():
        if project_args_path.exists():
            print(
                f"Project args: {project_args_path} "
                f"({len(project_args)} argument(s) loaded)"
            )
        else:
            print(
                f"Project args: {project_args_path} not found; create it "
                "with --init-project-args"
            )
    assistant_args = project_args + assistant_args

    # Root-config notice: repository configuration files the launcher
    # deliberately ignores would otherwise fail silently (see
    # _notice_root_config_files). Placed before the Docker availability
    # check so the notice is observable on every launch, including runs
    # without container tooling.
    _notice_root_config_files(project_root)

    if not _docker_available(debug=debug):
        print(
            "Docker CLI is not available. Please install Docker and ensure it is accessible from PATH.",
            file=sys.stderr,
        )
        _dump_recent_log_lines(debug)
        return 1

    # Pin GitHub's published SSH host keys on the host only (fingerprint-
    # verified, append-only) so container git push/pull never stalls on a
    # host-key prompt: the pinned file travels into the container through
    # the read-only ~/.ssh mounts, so writing it is meaningful on the
    # host alone.
    if not _running_in_container():
        _ensure_github_known_hosts(debug=debug)

    # Activate the repo's commit-msg gate when core.hooksPath is unset
    # (see _ensure_commit_msg_gate). The change is repo-local: it only
    # writes .git/config in the project root, so it runs on every launch,
    # inside or outside a container.
    _ensure_commit_msg_gate(project_root, debug=debug)

    container_name = (
        f"{TOOL_NAME}-{dir_name}-{workspace_hash[:8]}-{session_id}-{os.getpid()}"
    )
    docker_gid = _get_docker_gid()
    dockerfile_path = AGENT_DIR / "Dockerfile.aider"

    if not dockerfile_path.exists():
        print(
            f"Dockerfile.aider not found at {dockerfile_path}. Exiting.",
            file=sys.stderr,
        )
        return 1

    _warn_agent_dir_location(project_root)

    if _running_in_container():
        print(
            "Warning: the launcher appears to be running inside a container; "
            "skipping stale-container cleanup. The launcher must run on the "
            "host, where container aliveness can be checked reliably.",
            file=sys.stderr,
        )
    else:
        with _spinner("Checking for stale containers...", debug=debug):
            cleanup_containers(workspace_hash, debug=debug)

    # The Dockerfile performs no COPY, so the build context only needs the
    # Dockerfile itself. Using .agent (with its generated .dockerignore)
    # avoids shipping the whole repository to the daemon on every launch.
    _ensure_build_dockerignore(AGENT_DIR)

    with _spinner("Checking image cache...", debug=debug):
        cache_tag = _image_cache_tag(dockerfile_path, debug=debug)
        if debug:
            print(f"Image cache tag: {cache_tag}", file=sys.stderr)

        cache_hit = _image_exists(cache_tag, debug=debug)
        if cache_hit:
            command = ["docker", "tag", cache_tag, AIDER_IMAGE]
            _trace_command(command, debug)
            tag_result = subprocess.run(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            cache_hit = tag_result.returncode == 0

    if cache_hit:
        print(
            f"{ANSI_GREEN}[✔] Image up to date — skipping build ({cache_tag}).{ANSI_RESET}"
        )
        build_code = 0
    else:
        # The build executes instructions from the repo-writable
        # Dockerfile, so a changed definition is rebuilt only with fresh
        # user confirmation (see _rebuild_approved).
        if not _rebuild_approved(dockerfile_path, debug=debug):
            print(
                "Rebuild declined; launch aborted. Inspect "
                f"{dockerfile_path}, then re-run to approve the build.",
                file=sys.stderr,
            )
            return 1
        build_code = build_image(dockerfile_path, AGENT_DIR, debug=debug)
        if build_code == 0:
            _record_approved_dockerfile(dockerfile_path)
            command = ["docker", "tag", AIDER_IMAGE, cache_tag]
            _trace_command(command, debug)
            subprocess.run(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            # Once the base image is local its repo digests are known;
            # re-hash so the next run gets a stable, digest-aware tag.
            refreshed_tag = _image_cache_tag(dockerfile_path, debug=debug)
            if refreshed_tag != cache_tag:
                command = ["docker", "tag", AIDER_IMAGE, refreshed_tag]
                _trace_command(command, debug)
                subprocess.run(
                    command,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

    if build_code != 0:
        return build_code

    # Pre-flight repository health probe: warn when the image's gitdb
    # cannot read this repository (detection only; see _check_gitdb_reads).
    with _spinner("Checking repository health...", debug=debug):
        _check_gitdb_reads(
            project_root, workspace_hash, AIDER_IMAGE, debug=debug
        )

    aider_cache_dir = Path.home() / ".cache" / "aider"
    aider_cache_dir.mkdir(parents=True, exist_ok=True)

    # Discover the container user's passwd home (cached per image tag) so
    # the SSH keys are also mounted where ssh actually looks for them.
    container_home = None
    if not _running_in_container() and (Path.home() / ".ssh").is_dir():
        container_home = _container_passwd_home(cache_tag, debug=debug)

    result = run_container(
        workspace_hash,
        session_id,
        container_name,
        docker_gid,
        AGENT_DIR,
        container_home,
        debug,
        assistant_args,
    )

    _cleanup_empty_artifacts(project_root, AGENT_DIR)

    return result


if __name__ == "__main__":
    sys.exit(main())
