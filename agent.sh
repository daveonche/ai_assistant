#!/usr/bin/env bash
set -euo pipefail

# AI-assistance disclosure: this file was written with the aider AI coding
# assistant (https://aider.chat), driven by the prompt workflows in
# .agent/.aider.prompt/, as permitted for the CS50x final project.
# See README.md, section "Development methodology".

# agent.sh - Project-root convenience launcher for .agent/ai-assistant.sh.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${SCRIPT_DIR}/.agent/ai-assistant.sh" "$@"
