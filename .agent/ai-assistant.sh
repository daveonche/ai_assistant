#!/usr/bin/env bash
set -euo pipefail

# ai-assistant.sh - Thin launcher for the Python AI assistant implementation
# stored in the .agent directory.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${SCRIPT_DIR}/ai_assistant.py" "$@"
