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
# whose owner cannot be determined is treated as untrusted. Because a
# fake agent can be planted at the fixed path after any single check,
# ownership is re-proven immediately before every key-offering ssh-add
# and before the socket is finally exported into the container.

# agent_socket_trusted - Verify a path is a socket owned by this uid.
#
# Globals: none
# Arguments: $1 - path of the agent socket to verify
# Outputs: none
# Returns: 0 when the path is a socket owned by this uid; 1 otherwise,
# including when ownership cannot be determined (fail closed).
agent_socket_trusted() {
  local sock="${1:-}"
  local owner=""
  [[ -S "$sock" ]] || return 1
  owner="$(stat -c %u "$sock" 2>/dev/null || true)"
  [[ -n "$owner" && "$owner" == "$(id -u)" ]]
}

if [[ -z "${SSH_AUTH_SOCK:-}" && -d "${HOME}/.ssh" && -t 0 && -t 1 ]] \
   && command -v ssh-agent >/dev/null 2>&1 \
   && command -v ssh-add >/dev/null 2>&1; then
  agent_sock="${XDG_RUNTIME_DIR:-/tmp}/ssh-agent-$(id -u).sock"
  if agent_socket_trusted "$agent_sock"; then
    export SSH_AUTH_SOCK="$agent_sock"
    add_rc=0
    ssh-add -l >/dev/null 2>&1 || add_rc=$?
    if (( add_rc == 2 )); then
      # No agent answers: clear a stale socket, then start one. The rm
      # is best-effort: a sticky-bit /tmp can hold an object this uid
      # cannot remove, and letting it abort the launch would turn a
      # planted file into a persistent denial of service. A failed bind
      # means no agent of ours is listening: warn and fall back instead
      # of trusting whatever occupies the path.
      rm -f "$agent_sock" 2>/dev/null || true
      if ssh-agent -a "$agent_sock" >/dev/null 2>&1; then
        add_rc=1  # our fresh agent: alive, no identities added yet
      else
        printf 'Warning: ssh-agent failed on %s; skipping setup.\n' \
          "$agent_sock" >&2
        unset SSH_AUTH_SOCK
        add_rc=0  # nothing to unlock into; skip the key-offering step
      fi
    fi
    if (( add_rc != 0 )); then
      # Agent alive but no identities (or just started): unlock the
      # default keys once — the passphrase prompt appears only here.
      # Re-prove ownership immediately before offering keys: a local
      # attacker can plant a fake agent at the fixed path after the
      # check above, and ssh-add sends the decrypted private key to
      # whatever answers.
      if agent_socket_trusted "$agent_sock"; then
        ssh-add >/dev/null 2>&1 || true
      else
        printf 'Warning: %s not a trusted agent socket; skipping setup.\n' \
          "$agent_sock" >&2
        unset SSH_AUTH_SOCK
      fi
    fi
    # If no agent ended up reachable — or the socket is no longer owned
    # by this uid (a fake agent was planted after the checks above) —
    # drop the variable so the container falls back to direct-key auth
    # (ssh prompts for the passphrase on the container TTY) instead of
    # forwarding a dead or hostile socket.
    add_rc=0
    ssh-add -l >/dev/null 2>&1 || add_rc=$?
    if (( add_rc == 2 )) || ! agent_socket_trusted "$agent_sock"; then
      unset SSH_AUTH_SOCK
    fi
  else
    printf 'Warning: %s not a trusted agent socket; skipping setup.\n' \
      "$agent_sock" >&2
  fi
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${SCRIPT_DIR}/ai_assistant.py" "$@"
