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
if [[ -z "${SSH_AUTH_SOCK:-}" && -d "${HOME}/.ssh" && -t 0 && -t 1 ]] \
   && command -v ssh-agent >/dev/null 2>&1 \
   && command -v ssh-add >/dev/null 2>&1; then
  agent_sock="${XDG_RUNTIME_DIR:-/tmp}/ssh-agent-$(id -u).sock"
  export SSH_AUTH_SOCK="$agent_sock"
  add_rc=0
  ssh-add -l >/dev/null 2>&1 || add_rc=$?
  if (( add_rc == 2 )); then
    # No agent answers: clear a stale socket, then start one.
    rm -f "$agent_sock"
    ssh-agent -a "$agent_sock" >/dev/null 2>&1 || true
  fi
  if (( add_rc != 0 )); then
    # Agent alive but no identities (or just started): unlock the default
    # keys once — the passphrase prompt appears only here, on first use.
    ssh-add >/dev/null 2>&1 || true
  fi
  # If no agent ended up reachable, drop the variable so the container
  # falls back to direct-key auth (ssh prompts for the passphrase on the
  # container TTY) instead of forwarding a dead socket.
  add_rc=0
  ssh-add -l >/dev/null 2>&1 || add_rc=$?
  if (( add_rc == 2 )); then
    unset SSH_AUTH_SOCK
  fi
fi

# Best-effort: pin GitHub's published SSH host keys so git push/pull over
# SSH remotes never stalls on a host-key prompt inside the container. The
# ed25519 and ecdsa keys are embedded; the rsa key is too long to embed
# reliably and is fetched from GitHub's API instead. A key is appended
# only if its SHA256 fingerprint matches GitHub's published fingerprint,
# and only when that key type is not already pinned. Interactive-only and
# never fatal, matching the ssh-agent block above.
if [[ -t 0 && -t 1 ]] && command -v ssh-keygen >/dev/null 2>&1; then
  github_known_hosts="${HOME:-}/.ssh/known_hosts"
  github_rsa_key=""
  # Fetch the rsa key only while no rsa key is pinned for github.com yet.
  if command -v curl >/dev/null 2>&1 && ! ssh-keygen -F github.com \
      -f "$github_known_hosts" 2>/dev/null | grep -qF ' ssh-rsa '; then
    github_rsa_key="$(
      curl -fsSL --max-time 10 https://api.github.com/meta 2>/dev/null \
        | grep -o '"ssh-rsa [^"]*"' | head -n 1 | tr -d '"'
    )" || true
  fi
  github_rsa_triplet=""
  if [[ -n "$github_rsa_key" ]]; then
    github_rsa_triplet="ssh-rsa|${github_rsa_key#ssh-rsa }"
    github_rsa_triplet+="|SHA256:uNiVztksCsDhcc0u9e8BujQXVUpKZIDTMczCvj3tD2s"
  fi
  # Each entry is key-type|key-blob|GitHub's published SHA256 fingerprint.
  while IFS='|' read -r key_type key_blob key_fp; do
    [[ -n "$key_type" ]] || continue
    # Refuse any key whose fingerprint is not GitHub's published one.
    printf '%s %s\n' "$key_type" "$key_blob" | ssh-keygen -lf - 2>/dev/null \
      | grep -qF -- "$key_fp" || continue
    if ! ssh-keygen -F github.com -f "$github_known_hosts" 2>/dev/null \
        | grep -qF -- "$key_blob"; then
      ( mkdir -p "${HOME:-}/.ssh"
        printf 'github.com %s %s\n' "$key_type" "$key_blob" \
          >> "$github_known_hosts" ) 2>/dev/null || true
    fi
  done <<EOF
ssh-ed25519|AAAAC3NzaC1lZDI1NTE5AAAAIOMqqnkVzrm0SdG6UOoqKLsabgH5C9okWi0dh2l9GKJl|SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU
ecdsa-sha2-nistp256|AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBEmKSENjQEezOmxkZMy7opKgwFB9nkt5YRrYMjNuG5N87uRgg6CLrbo5wAdT/y6v0mKV0U2w0WZ2YB/++Tpockg=|SHA256:p2QAMXNIC1TJYWeIOttrVc98/R1BUFWu3/LiyKgUfQM
${github_rsa_triplet}
EOF
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "${SCRIPT_DIR}/ai_assistant.py" "$@"
