#!/usr/bin/env bash
# AIAssistant installer entry point (story S2.1, steps 1-2).
#
# Retrieves this script with a single command from inside a project
# repository, validates the documented host prerequisites (Bash and git),
# and performs a clean install: it clones the pinned release reference
# into a temporary directory, copies .agent/ and agent.sh into the project
# root, and removes the temporary directory on exit. Updating an existing
# install is handled in a later story step.

set -euo pipefail

readonly DEFAULT_REPO_URL="https://github.com/daveonche/ai_assistant.git"
readonly DEFAULT_REF="v1.0.0"

# Globals: None
# Arguments: Variable list of message words, joined into one message
# Outputs: Error message prefixed with the script name to STDERR
# Returns: None
die() {
  printf '%s: error: %s\n' "${0##*/}" "$*" >&2
}

# Globals: DEFAULT_REF (read)
# Arguments: None
# Outputs: Usage text with examples to STDOUT
# Returns: None
usage() {
  cat <<EOF
Usage: install.sh [options]

Prepare the AIAssistant assistant-file installation in the current
project repository.

Options:
  --ref REF   Install from REF instead of the pinned default
              (${DEFAULT_REF})
  --dry-run   Report the planned action without changing anything
  --debug     Enable shell tracing for troubleshooting
  --help      Show this help and exit

Examples:
  curl -fsSL https://raw.githubusercontent.com/daveonche/ai_assistant/v1.0.0/scripts/install.sh | bash
  curl -fsSL https://raw.githubusercontent.com/daveonche/ai_assistant/v1.0.0/scripts/install.sh | bash -s -- --ref v1.0.0
  ./scripts/install.sh --dry-run
  ./scripts/install.sh --ref v1.0.0 --debug
EOF
}

# Globals: None
# Arguments: None
# Outputs: Error messages to STDERR
# Returns: 0 when prerequisites are met, 1 otherwise
check_prerequisites() {
  if ! command -v git >/dev/null 2>&1; then
    die "git is required but was not found on the PATH"
    return 1
  fi

  local inside_work_tree
  inside_work_tree="$(git rev-parse --is-inside-work-tree 2>/dev/null || true)"
  if [[ "${inside_work_tree}" != "true" ]]; then
    die "the current directory is not a git work tree;"
    die "run the installer from inside a project repository"
    return 1
  fi
}

# Globals: TMP_CLONE (modified)
# Arguments: None
# Outputs: None
# Returns: None
cleanup() {
  if [[ -n "${TMP_CLONE:-}" && -d "${TMP_CLONE}" ]]; then
    rm -rf "${TMP_CLONE}"
  fi
}

# Globals: PROJECT_ROOT (set)
# Arguments: None
# Outputs: None
# Returns: 0 when the project has no existing assistant files, 1 otherwise
check_clean_install() {
  if [[ -e ".agent" || -e "agent.sh" ]]; then
    die "existing assistant files found (.agent/ or agent.sh);"
    die "updating an existing install is not supported yet"
    return 1
  fi
}

# Globals: REPO_URL, REF, TMP_CLONE (read/set)
# Arguments: None
# Outputs: Progress to STDOUT; errors to STDERR
# Returns: 0 on successful clone, 1 otherwise
retrieve_files() {
  TMP_CLONE="$(mktemp -d)"
  if ! git clone --quiet --depth 1 --branch "${REF}" \
      "${REPO_URL}" "${TMP_CLONE}"; then
    die "failed to retrieve ${REPO_URL} at ref ${REF}"
    return 1
  fi
  printf 'installer: retrieved ref %s\n' "${REF}"
}

# Globals: TMP_CLONE (read)
# Arguments: None
# Outputs: Progress to STDOUT; errors to STDERR
# Returns: 0 on successful placement, 1 otherwise
place_files() {
  if [[ ! -d "${TMP_CLONE}/.agent" || ! -f "${TMP_CLONE}/agent.sh" ]]; then
    die "ref ${REF} does not contain the assistant files"
    return 1
  fi
  cp -R "${TMP_CLONE}/.agent" .agent
  cp "${TMP_CLONE}/agent.sh" agent.sh
  chmod +x agent.sh .agent/ai-assistant.sh
  printf 'installer: placed .agent/ and agent.sh into the project root\n'
}

# Globals: REPO_URL, REF, DRY_RUN, DEBUG (modified)
# Arguments: Command-line arguments
# Outputs: Usage to STDOUT for --help; errors to STDERR
# Returns: 0 on success, 1 on invalid usage
parse_args() {
  REPO_URL="${DEFAULT_REPO_URL}"
  REF="${DEFAULT_REF}"
  DRY_RUN=false
  DEBUG=false
  TMP_CLONE=""

  while [[ "$#" -gt 0 ]]; do
    case "${1}" in
      --ref)
        if [[ -z "${2:-}" ]]; then
          die "--ref requires a value"
          return 1
        fi
        REF="${2}"
        shift 2
        ;;
      --dry-run)
        DRY_RUN=true
        shift
        ;;
      --debug)
        DEBUG=true
        shift
        ;;
      --help | -h)
        usage
        exit 0
        ;;
      *)
        die "unknown option: ${1}"
        usage >&2
        return 1
        ;;
    esac
  done
}

# Globals: REPO_URL, REF, DRY_RUN, DEBUG
# Arguments: Command-line arguments passed through to parse_args
# Outputs: Progress and planned action to STDOUT; errors to STDERR
# Returns: 0 when prerequisites are met, 1 otherwise
main() {
  parse_args "$@"

  if [[ "${DEBUG}" == true ]]; then
    set -x
  fi

  printf 'installer: repository: %s\n' "${REPO_URL}"
  printf 'installer: reference: %s\n' "${REF}"

  check_prerequisites
  trap cleanup EXIT

  if [[ "${DRY_RUN}" == true ]]; then
    printf 'installer: dry run: would install .agent/ and agent.sh'
    printf ' from ref %s\n' "${REF}"
    printf 'installer: dry run complete; no changes were made\n'
    return 0
  fi

  check_clean_install
  retrieve_files
  place_files
  printf 'installer: install complete\n'
}

# Entry point: the empty-BASH_SOURCE branch supports piped execution
# (curl ... | bash), where the standard main guard would skip main.
if [[ "${BASH_SOURCE[0]:-}" == "${0}" || -z "${BASH_SOURCE[0]:-}" ]]; then
  main "$@"
fi
