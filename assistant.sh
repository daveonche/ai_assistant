#!/usr/bin/env bash
set -euo pipefail

# assistant.sh - Project-root convenience launcher for .agent/ai-assistant.sh.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/.agent/ai-assistant.sh" "$@"
