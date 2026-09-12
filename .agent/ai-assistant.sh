#!/usr/bin/env bash
set -euo pipefail

# AI-assistance disclosure: this file was written with the aider AI coding
# assistant (https://aider.chat), driven by the prompt workflows in
# .agent/.aider.prompt/, as permitted for the CS50x final project.
# See README.md, section "Development methodology".

# ai-assistant.sh - Thin launcher for the Python AI assistant implementation
# stored in the .agent directory.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${SCRIPT_DIR}/ai_assistant.py" "$@"
