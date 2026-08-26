#!/usr/bin/env python3
"""Launch an AI assistant in a Docker container.

This module provides a command-line interface equivalent to the previous
ai-assistant.sh script. It handles optional Docker image builds, container
cleanup, and running the assistant in a Docker container with workspace
isolation, audio support, and Docker-in-Docker capabilities.

When installed as part of the `.agent` directory, this script uses the
project root as the working directory and Docker build context while keeping
all helper files inside `.agent`.
"""

from __future__ import annotations

import grp
import hashlib
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import List

TOOL_NAME = "ai-assistant"
AIDER_IMAGE = "aider-agent:latest"

ANSI_RED = "\033[31m"
ANSI_RESET = "\033[0m"
SPIN_CHARS = ["-", "\\", "|", "/", "."]

LOG_RE = re.compile(
    r"(?:RUN|COPY|FROM|Installing|Extracting|Downloading).*"
)

AGENT_DIR = Path(__file__).resolve().parent


def _trace_command(command: List[str]) -> None:
    """Print a command to stderr when debug output is enabled."""
    print("+", " ".join(command), file=sys.stderr)


def _tail_lines(path: Path, count: int) -> List[str]:
    """Return up to the last count lines from a text file."""
    try:
        lines = path.read_text(errors="replace").splitlines()
    except FileNotFoundError:
        return []
    return lines[-count:] if count > 0 else lines


def _print_spinner_update(char: str, message: str) -> None:
    """Print a single-line spinner status update."""
    sys.stdout.write(f"\r[{char}] Loading AI Assistant... {message:<50}")
    sys.stdout.flush()


def _get_docker_gid() -> int:
    """Return the Docker group GID, or 0 when the group does not exist."""
    try:
        return grp.getgrnam("docker").gr_gid
    except KeyError:
        return 0


def _aider_config_args(agent_dir: Path) -> List[str]:
    """Return Aider CLI flags for config files stored in agent_dir."""
    args: List[str] = []

    config_file = agent_dir / ".aider.conf.yml"
    if config_file.exists():
        args.extend(["--config", str(config_file)])

    model_settings_file = agent_dir / ".aider.model.settings.yml"
    if model_settings_file.exists():
        args.extend(["--model-settings-file", str(model_settings_file)])

    prompt_dir = agent_dir / ".aider.prompt"
    if prompt_dir.exists():
        args.extend(["--prompt-dir", str(prompt_dir)])

    return args


def cleanup_containers(workspace_hash: str) -> None:
    """Remove all containers associated with the current workspace.

    Arguments:
        workspace_hash: Aider directory hash used as a Docker label.

    Returns:
        None
    """
    result = subprocess.run(
        [
            "docker",
            "ps",
            "-a",
            "--filter",
            f"label=aider.dir={workspace_hash}",
            "--format",
            "{{.ID}}",
        ],
        capture_output=True,
        text=True,
    )
    container_ids = [
        line for line in (result.stdout or "").splitlines() if line.strip()
    ]
    for container_id in container_ids:
        subprocess.run(
            ["docker", "rm", "-f", container_id],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def build_image(
    dockerfile_path: Path,
    cwd: Path,
    debug: bool = False,
) -> int:
    """Build the Docker image with a progressive status indicator.

    Arguments:
        dockerfile_path: Path to the project Dockerfile.
        cwd: Current working directory used as the Docker build context.
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
            "-t",
            AIDER_IMAGE,
            "-f",
            str(dockerfile_path),
            str(cwd),
        ]
        if debug:
            _trace_command(command)

        env = os.environ.copy()
        env["DOCKER_BUILDKIT"] = "1"

        with log_path.open("w") as log_file:
            process = subprocess.Popen(
                command,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                env=env,
            )

            spin_index = 0
            while process.poll() is None:
                latest_line = ""
                try:
                    text = log_path.read_text(errors="replace")
                    matches = LOG_RE.findall(text)
                    if matches:
                        latest_line = matches[-1]
                except FileNotFoundError:
                    pass

                if not latest_line:
                    status_message = "Initializing build environment..."
                else:
                    status_message = latest_line[:45]

                char = SPIN_CHARS[spin_index % len(SPIN_CHARS)]
                _print_spinner_update(char, status_message)

                spin_index += 1
                time.sleep(0.1)

            returncode = process.wait()

        if returncode != 0:
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
        sys.stdout.write(f"\r[✔] Loading AI Assistant... done.{' ':50}\n")
        sys.stdout.flush()
        return 0
    finally:
        try:
            log_path.unlink()
        except OSError:
            pass


def run_container(
    workspace_hash: str,
    session_id: str,
    container_name: str,
    docker_gid: int,
    agent_dir: Path,
    debug: bool,
    assistant_args: List[str],
) -> int:
    """Run the AI assistant Docker container.

    Arguments:
        workspace_hash: Docker label for the workspace.
        session_id: Docker label for the session.
        container_name: Name to assign to the Docker container.
        docker_gid: Host Docker group GID to add to the container.
        agent_dir: Directory containing the AI assistant helper files.
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
        "--user",
        f"{uid}:{gid}",
        "--group-add",
        str(docker_gid),
        "--group-add",
        "audio",
        "--device",
        "/dev/snd",
        "-e",
        "HOME=/home",
        "-e",
        "PYTHONUNBUFFERED=1",
        "-v",
        "/var/run/docker.sock:/var/run/docker.sock",
        "-v",
        f"{home}/.docker:/home/.docker:ro",
        "-v",
        f"{cwd}:{cwd}",
        "-w",
        cwd,
        "-v",
        f"{home}/.bashrc:/home/.bashrc:ro",
        "-v",
        f"{home}/.gitconfig:/home/.gitconfig:ro",
        "-v",
        f"{home}/.cache/aider:/home/.cache",
        "-v",
        f"{pulse_user_dir}:{pulse_user_dir}",
        "-v",
        "/dev/shm:/dev/shm",
        "-e",
        f"PULSE_SERVER=unix:{pulse_user_dir}",
    ]

    project_root = Path(cwd)
    env_file = project_root / ".env"
    agent_env_file = agent_dir / ".env"

    if env_file.exists():
        command.extend(["--env-file", str(env_file)])
    elif agent_env_file.exists():
        command.extend(["--env-file", str(agent_env_file)])

    command.append(AIDER_IMAGE)
    command.extend(["--chat-mode", "ask"])
    command.extend(_aider_config_args(agent_dir))
    command.extend(assistant_args)

    if debug:
        _trace_command(command)

    return subprocess.run(command).returncode


def main() -> int:
    """Orchestrate the AI assistant launch."""
    assistant_args = sys.argv[1:]
    debug = False

    while assistant_args and assistant_args[0] in ("-x", "--debug"):
        debug = True
        assistant_args.pop(0)

    project_root = Path.cwd()
    dir_name = project_root.name
    workspace_hash = hashlib.md5((str(project_root) + "\n").encode()).hexdigest()
    session_id = os.environ.get("VSCODE_PID", "0")
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

    cleanup_containers(workspace_hash)

    build_code = build_image(dockerfile_path, project_root, debug=debug)
    if build_code != 0:
        return build_code

    aider_cache_dir = Path.home() / ".cache" / "aider"
    aider_cache_dir.mkdir(parents=True, exist_ok=True)

    return run_container(
        workspace_hash,
        session_id,
        container_name,
        docker_gid,
        AGENT_DIR,
        debug,
        assistant_args,
    )


if __name__ == "__main__":
    sys.exit(main())
