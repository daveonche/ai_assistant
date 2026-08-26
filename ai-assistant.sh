#!/usr/bin/env bash
set -euo pipefail

# ai-assistant.sh - Launches an AI assistant in a Docker container with proper
# workspace isolation, audio support, and Docker-in-Docker capabilities.
#
# This script builds a Docker image from Dockerfile.aider if needed, cleans up
# old containers for the workspace, and runs the AI assistant with appropriate
# volume mounts and environment variables.

# Print exact failure details before exiting on error
trap 'echo -e "\033[31m[ERROR] L$LINENO: $BASH_COMMAND ($?)\033[0m" >&2' ERR

# Constants
readonly TOOL_NAME="ai-assistant"
readonly AIDER_IMAGE="aider-agent:latest"

# Clean up ALL containers associated with this workspace directory
# Globals: WORKSPACE_HASH
# Arguments: None
# Outputs: None
# Returns: None
cleanup_containers() {
  local all_dir_containers
  local id

  all_dir_containers=$(docker ps -a \
    --filter "label=aider.dir=${WORKSPACE_HASH}" \
    --format "{{.ID}}")

  if [[ -n "$all_dir_containers" ]]; then
    while read -r id; do
      if [[ -n "$id" ]]; then
        docker rm -f "$id" > /dev/null 2>&1 || true
      fi
    done <<< "$all_dir_containers"
  fi
}

# Build the Docker image with a spinner showing build progress
# Globals: AIDER_IMAGE, DOCKERFILE_PATH
# Arguments: None
# Outputs: Build progress spinner to STDOUT, errors to STDERR
# Returns: 0 on success, 1 on failure
build_image() {
  local build_log
  local build_pid
  local build_status
  local spin_chars
  local i=0
  local latest_line
  local status_msg
  local char

  build_log=$(mktemp)
  trap "rm -f '$build_log'" EXIT

  export DOCKER_BUILDKIT=1

  docker build -t "$AIDER_IMAGE" -f "$DOCKERFILE_PATH" \
    "$(pwd)" > "$build_log" 2>&1 &
  build_pid=$!

  spin_chars="-\|/."

  while kill -0 "$build_pid" 2>/dev/null; do
    latest_line=$(grep -oE \
      '(RUN|COPY|FROM|Installing|Extracting|Downloading)[^[:cntrl:]]*' \
      "$build_log" | tail -n 1 || true)

    if [[ -z "$latest_line" ]]; then
      status_msg="Initializing build environment..."
    else
      status_msg="${latest_line:0:45}"
    fi

    char="${spin_chars:i%${#spin_chars}:1}"
    printf "\r[%s] Loading AI Assistant... %-50s" "$char" "$status_msg"

    i=$((i + 1))
    sleep 0.1
  done

  wait "$build_pid"
  build_status=$?

  if [[ "$build_status" -ne 0 ]]; then
    printf "\r[✖] Loading AI Assistant... failed.%-50s\n\n" ""
    echo -e "\033[31m--- Last lines of build log ---\033[0m" >&2
    tail -n 25 "$build_log" >&2
    echo -e "\033[31m-----------------------------\033[0m" >&2
    rm -f "$build_log"
    return 1
  else
    # Padding clears previous line content
    printf "\r[✔] Loading AI Assistant... done.%-50s\n" ""
  fi
}

# Run the AI assistant Docker container
# Globals: CONTAINER_NAME, WORKSPACE_HASH, SESSION_ID, DOCKER_GID, AIDER_IMAGE
# Arguments: Additional arguments passed to the AI assistant
# Outputs: None
# Returns: None
run_container() {
  local env_file_arg=""

  if [[ -f ".env" ]]; then
    env_file_arg="--env-file .env"
  fi

  docker run -it --rm \
    --name "$CONTAINER_NAME" \
    --label "aider.dir=${WORKSPACE_HASH}" \
    --label "aider.session=${SESSION_ID}" \
    --user "$(id -u):$(id -g)" \
    --group-add "$DOCKER_GID" \
    --group-add audio \
    --device /dev/snd \
    -e HOME=/home \
    -e PYTHONUNBUFFERED=1 \
    -v "/var/run/docker.sock:/var/run/docker.sock" \
    -v "$HOME/.docker:/home/.docker:ro" \
    -v "$(pwd):$(pwd)" \
    -w "$(pwd)" \
    -v "$HOME/.bashrc:/home/.bashrc:ro" \
    -v "$HOME/.gitconfig:/home/.gitconfig:ro" \
    -v "$HOME/.cache/aider:/home/.cache" \
    -v "/run/user/$(id -u)/pulse/native:/run/user/$(id -u)/pulse/native" \
    -v "/dev/shm:/dev/shm" \
    -e PULSE_SERVER=unix:/run/user/$(id -u)/pulse/native \
    $env_file_arg \
    "$AIDER_IMAGE" --chat-mode ask "$@"
}

# Main function to orchestrate the AI assistant launch
# Globals: Sets WORKSPACE_HASH, CONTAINER_NAME, SESSION_ID, DOCKER_GID,
#   DOCKERFILE_PATH
# Arguments: Additional arguments passed to the AI assistant
# Outputs: Status messages to STDOUT, errors to STDERR
# Returns: 0 on success, 1 on failure
main() {
  local dir_name
  local debug=false

  while [[ $# -gt 0 ]]; do
    case "$1" in
      -x|--debug)
        debug=true
        shift
        ;;
      *)
        break
        ;;
    esac
  done

  if [[ "$debug" == true ]]; then
    set -x
  fi

  dir_name=$(basename "$(pwd)")
  WORKSPACE_HASH=$(pwd | md5sum | awk '{print $1}')
  SESSION_ID="${VSCODE_PID:-0}"
  CONTAINER_NAME="${TOOL_NAME}-${dir_name}-"
  CONTAINER_NAME+="${WORKSPACE_HASH:0:8}-${SESSION_ID}-${$}"
  DOCKER_GID=$(getent group docker | cut -d: -f3 2>/dev/null || echo 0)
  DOCKERFILE_PATH="$(pwd)/Dockerfile.aider"

  if [[ ! -f "$DOCKERFILE_PATH" ]]; then
    echo "Dockerfile.aider not found at $DOCKERFILE_PATH. Exiting." >&2
    return 1
  fi

  cleanup_containers
  build_image || return 1

  mkdir -p "$HOME/.cache/aider"
  run_container "$@"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
