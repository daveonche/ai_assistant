#!/usr/bin/env bash
set -euo pipefail

# ai-assistant.sh - Launcher for the Python AI assistant implementation
# stored in the .agent directory.

# Ensure an ssh-agent is reachable so git push/pull over SSH remotes works
# inside the container (ai_assistant.py forwards SSH_AUTH_SOCK into it). A
# persistent per-user agent on a fixed socket is reused across launches and
# started on first use. Interactive-only and best-effort: skipped entirely
# for non-TTY callers (tests, scripts) so nothing is spawned or prompted
# there, and never fails the launch.
#
# GitHub host-key pinning is handled by ai_assistant.py on every launch
# (fingerprint-verified, append-only), so ssh never prompts here or in
# the container.
#
# The well-known agent socket is only used when it is owned by this uid:
# a socket planted by another local user could pose as an agent and
# harvest the private keys ssh-add offers below. An existing socket
# whose owner cannot be determined is treated as untrusted.
if [[ -z "${SSH_AUTH_SOCK:-}" && -d "${HOME}/.ssh" && -t 0 && -t 1 ]] \
   && command -v ssh-agent >/dev/null 2>&1 \
   && command -v ssh-add >/dev/null 2>&1; then
  agent_sock="${XDG_RUNTIME_DIR:-/tmp}/ssh-agent-$(id -u).sock"
  agent_sock_owner=""
  if [[ -S "$agent_sock" ]]; then
    agent_sock_owner="$(stat -c %u "$agent_sock" 2>/dev/null || true)"
  fi
  agent_sock_trusted=1
  if [[ -S "$agent_sock" && "$agent_sock_owner" != "$(id -u)" ]]; then
    printf 'Warning: %s is not owned by uid %s; skipping ssh-agent setup.\n' \
      "$agent_sock" "$(id -u)" >&2
    agent_sock_trusted=0
  fi
  if (( agent_sock_trusted )); then
    export SSH_AUTH_SOCK="$agent_sock"
    add_rc=0
    ssh-add -l >/dev/null 2>&1 || add_rc=$?
    if (( add_rc == 2 )); then
      # No agent answers: clear a stale socket, then start one.
      rm -f "$agent_sock"
      ssh-agent -a "$agent_sock" >/dev/null 2>&1 || true
    fi
    if (( add_rc != 0 )); then
      # Agent alive but no identities (or just started): unlock the
      # default keys once — the passphrase prompt appears only here.
      ssh-add >/dev/null 2>&1 || true
    fi
    # If no agent ended up reachable, drop the variable so the container
    # falls back to direct-key auth (ssh prompts for the passphrase on
    # the container TTY) instead of forwarding a dead socket.
    add_rc=0
    ssh-add -l >/dev/null 2>&1 || add_rc=$?
    if (( add_rc == 2 )); then
      unset SSH_AUTH_SOCK
    fi
  fi
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${SCRIPT_DIR}/ai_assistant.py" "$@"
