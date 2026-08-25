#!/usr/bin/env bash
set -euo pipefail

# Print exact failure details before exiting on error
trap 'echo -e "\033[31m[ERROR] Script failed at line $LINENO: command \"$BASH_COMMAND\" exited with status $?\033[0m"' ERR

# Optional: Uncomment the line below to print EVERY command as it runs (verbose debugging)
# set -x

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

# Clean up ALL containers associated with this workspace directory (running or stopped)
ALL_DIR_CONTAINERS=$(docker ps -a --filter "label=aider.dir=${WORKSPACE_HASH}" --format "{{.ID}}")

if [ -n "$ALL_DIR_CONTAINERS" ]; then
    while read -r id; do
        if [ -n "$id" ]; then
            # Stop and force-remove any old container for this workspace
            docker rm -f "$id" > /dev/null 2>&1 || true
        fi
    done <<< "$ALL_DIR_CONTAINERS"
fi

if [ -f "$DOCKERFILE_PATH" ]; then
    BUILD_LOG=$(mktemp)
    # Ensure the build log is removed on exit or interrupt
    trap 'rm -f "$BUILD_LOG"' EXIT
    
    # Enable BuildKit for faster, cached builds
    export DOCKER_BUILDKIT=1

    # Run docker build in the background, piping output to log
    docker build -t "$AIDER_IMAGE" -f "$DOCKERFILE_PATH" "$(pwd)" > "$BUILD_LOG" 2>&1 &
    BUILD_PID=$!

    SPIN_CHARS="-\|/."
    i=0

    # Loop while the build process is active
    while kill -0 $BUILD_PID 2>/dev/null; do
        LATEST_LINE=$(grep -oE '(RUN|COPY|FROM|Installing|Extracting|Downloading)[^[:cntrl:]]*' "$BUILD_LOG" | tail -n 1 || true)
        
        if [ -z "$LATEST_LINE" ]; then
            STATUS_MSG="Initializing build environment..."
        else
            STATUS_MSG="${LATEST_LINE:0:45}"
        fi

        CHAR="${SPIN_CHARS:i%${#SPIN_CHARS}:1}"
        printf "\r[%s] Loading AI Assistant... %-50s" "$CHAR" "$STATUS_MSG"
        
        i=$((i+1))
        sleep 0.1
    done

    # Wait for completion and fetch exit status
    wait $BUILD_PID
    BUILD_STATUS=$?

    if [ $BUILD_STATUS -ne 0 ]; then
        printf "\r[✖] Loading AI Assistant... failed.                                              \n\n"
        echo -e "\033[31m--- Last lines of build log (Error Details) ---\033[0m"
        tail -n 25 "$BUILD_LOG"
        echo -e "\033[31m-------------------------------------------------\033[0m"
        rm -f "$BUILD_LOG"
        exit 1
    else
        # Added extra padding spaces at the end to completely clear out long previous lines like mkdir
        printf "\r[✔] Loading AI Assistant... done.                                                  \n"
    fi
else
    echo "Dockerfile.aider not found at $DOCKERFILE_PATH. Exiting."
    exit 1
fi

# Ensure the cache directory exists on the host to avoid permission issues
mkdir -p "$HOME/.cache/aider"

# Check if .env file exists to conditionally include it
ENV_FILE_ARG=""
if [ -f ".env" ]; then
    ENV_FILE_ARG="--env-file .env"
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
    $ENV_FILE_ARG \
    "$AIDER_IMAGE" --chat-mode ask "$@"
