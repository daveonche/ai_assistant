#!/usr/bin/env bash

TOOL_NAME="ai-assistant"
DIR_NAME=$(basename "$(pwd)")
WORKSPACE_HASH=$(pwd | md5sum | awk '{print $1}')

# Use VSCODE_PID as a session ID to group containers; fallback to 0 if not in VS Code
SESSION_ID="${VSCODE_PID:-0}"

# Include SESSION_ID and shell PID ($$) to allow multiple concurrent containers per session
CONTAINER_NAME="${TOOL_NAME}-${DIR_NAME}-${WORKSPACE_HASH:0:8}-${SESSION_ID}-${$}"
DOCKER_GID=$(getent group docker | cut -d: -f3 2>/dev/null || echo 0)
AIDER_IMAGE="aider-agent:latest"
DOCKERFILE_PATH="$(pwd)/Dockerfile.aider"

# Clean up orphaned containers from previous sessions (e.g., after a VS Code window reload)
# This allows multiple concurrent containers in the current session, but clears old ones on reload
ALL_DIR_CONTAINERS=$(docker ps --filter "label=aider.dir=${WORKSPACE_HASH}" --format "{{.ID}}\t{{.Label \"aider.session\"}}")

while IFS=$'\t' read -r id session; do
    if [ "$session" != "$SESSION_ID" ]; then
        docker rm -f "$id" > /dev/null 2>&1
    fi
done <<< "$ALL_DIR_CONTAINERS"

if [ -f "$DOCKERFILE_PATH" ]; then
    # Relying on Docker's layer cache, this is instant if nothing changed
    # Suppress build output completely unless an error occurs
    if ! docker build -t "$AIDER_IMAGE" -f "$DOCKERFILE_PATH" "$(pwd)" > /dev/null 2>&1; then
        echo "Failed to build Aider image. Exiting."
        exit 1
    fi
else
    echo "Dockerfile.aider not found at $DOCKERFILE_PATH. Exiting."
    exit 1
fi

# Ensure the cache directory exists on the host to avoid permission issues
mkdir -p "$HOME/.cache/aider"

docker run -it --rm \
    --name "$CONTAINER_NAME" \
    --label "aider.dir=${WORKSPACE_HASH}" \
    --label "aider.session=${SESSION_ID}" \
    --user "$(id -u):$(id -g)" \
    --group-add "$DOCKER_GID" \
    --group-add audio \
    --device /dev/snd \
    -e HOME=/home \
    -v "/var/run/docker.sock:/var/run/docker.sock" \
    -v "$HOME/.docker:/home/.docker:ro" \
    -v "$(pwd):$(pwd)" \
    -w "$(pwd)" \
    -v "$HOME/.bashrc:/home/.bashrc:ro" \
    -v "$HOME/.gitconfig:/home/.gitconfig:ro" \
    -v "$HOME/.cache/aider:/home/.cache" \
    -v "/run/user/$(id -u)/pulse/native:/run/user/1000/pulse/native" \
    -v "/dev/shm:/dev/shm" \
    -e PULSE_SERVER=unix:/run/user/1000/pulse/native \
    ${RFILE:---env-file .env} \
    "$AIDER_IMAGE" "$@"
