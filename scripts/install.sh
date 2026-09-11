#!/usr/bin/env bash
# AIAssistant installer entry point (story S2.1, steps 1-4).
#
# Retrieves this script with a single command from inside a project
# repository, validates the documented host prerequisites (Bash and git),
# and performs a clean install: it clones the pinned release reference
# into a temporary directory, copies .agent/ and agent.sh into the project
# root, and removes the temporary directory on exit. When the assistant
# files already exist, it refreshes them through the consumer's own git
# (assistant remote -> fetch -> checkout -> commit) so the change is
# recorded as a normal, reviewable project change. Both entry scripts
# are recorded executable in the project's git index
# (update-index --chmod=+x) so executability survives environments that
# do not preserve file modes.

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
project repository. When .agent/ or agent.sh already exist, the run
switches to update mode and refreshes the files through this
repository's git as one reviewable, revertable commit.

Options:
  --ref REF   Install from REF instead of the pinned default
              (${DEFAULT_REF})
  --dry-run   Report the planned action without changing anything
  --debug     Enable shell tracing for troubleshooting
  --help      Show this help and exit

Update mode replaces .agent/ and agent.sh with the pinned release, so
local customizations inside .agent/ (for example the read: list in
.aider.conf.yml) are overwritten after a warning; re-apply them.

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

# Globals: INSTALL_MODE (set)
# Arguments: None
# Outputs: None
# Returns: None
detect_mode() {
  if [[ -e ".agent" || -e "agent.sh" ]]; then
    INSTALL_MODE="update"
  else
    INSTALL_MODE="install"
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
  # Record executability explicitly so the consumer's next commit stores
  # 100755 for both entry scripts even with core.fileMode=false, and the
  # scripts run immediately after the install.
  if ! git update-index --add --chmod=+x agent.sh .agent/ai-assistant.sh; then
    die "failed to record executability in the git index"
    return 1
  fi
  printf 'installer: placed .agent/ and agent.sh into the project root\n'
}

# Globals: None
# Arguments: None
# Outputs: Overwrite warning to STDERR
# Returns: None
warn_overwrite() {
  printf 'installer: WARNING: the update replaces .agent/ and agent.sh\n' >&2
  printf 'installer:   local customizations inside .agent/ (for example\n' >&2
  printf 'installer:   the read: list in .agent/.aider.conf.yml) will be\n' >&2
  printf 'installer:   overwritten; re-apply them after the update\n' >&2
}

# Globals: None
# Arguments: None
# Outputs: Error messages to STDERR
# Returns: 0 when staged changes stay inside the update scope, 1 otherwise
check_staged_scope() {
  local path
  while IFS= read -r path; do
    case "${path}" in
      .agent/* | agent.sh) ;;
      *)
        die "staged change outside the update scope: ${path}"
        die "commit or unstage it before updating"
        return 1
        ;;
    esac
  done < <(git diff --cached --name-only)
}

# Globals: REPO_URL (read)
# Arguments: None
# Outputs: Error messages to STDERR
# Returns: 0 when the assistant remote is available, 1 otherwise
ensure_assistant_remote() {
  if ! git remote get-url assistant >/dev/null 2>&1; then
    if ! git remote add assistant "${REPO_URL}"; then
      die "failed to configure the assistant remote (${REPO_URL})"
      return 1
    fi
  fi
}

# Globals: REF (read)
# Arguments: None
# Outputs: Error messages to STDERR
# Returns: 0 on successful fetch, 1 otherwise
fetch_assistant_ref() {
  if ! git fetch --quiet --depth 1 assistant "${REF}"; then
    die "failed to retrieve the assistant ref ${REF}"
    return 1
  fi
}

# Globals: REF (read)
# Arguments: None
# Outputs: Progress to STDOUT; errors to STDERR
# Returns: 0 when the refresh was applied or is already up to date
apply_refresh() {
  if ! git checkout FETCH_HEAD -- .agent agent.sh; then
    die "failed to check out .agent and agent.sh from ref ${REF}"
    return 1
  fi
  # Record executability explicitly before the no-op probe: the index
  # stores 100755 for both entry scripts even with core.fileMode=false,
  # and a mode-only difference still yields a reviewable commit.
  if ! git update-index --chmod=+x agent.sh .agent/ai-assistant.sh; then
    die "failed to record executability in the git index"
    return 1
  fi
  chmod +x agent.sh .agent/ai-assistant.sh
  if git diff --cached --quiet HEAD -- .agent agent.sh; then
    printf 'installer: already up to date at ref %s\n' "${REF}"
    return 0
  fi
  if ! git commit --quiet -m "Update assistant files to ${REF}" \
      -- .agent agent.sh; then
    die "failed to record the refresh as a commit"
    return 1
  fi
  printf 'installer: recorded the refresh as commit %s\n' \
    "$(git rev-parse --short HEAD)"
}

# Globals: REPO_URL, REF (read)
# Arguments: None
# Outputs: Progress to STDOUT; warning and errors to STDERR
# Returns: 0 when the update completed, 1 otherwise
update_files() {
  printf 'installer: updating an existing install\n'
  warn_overwrite
  check_staged_scope
  ensure_assistant_remote
  fetch_assistant_ref
  apply_refresh
  printf 'installer: update complete\n'
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
  INSTALL_MODE="install"
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

# Globals: REPO_URL, REF, DRY_RUN, DEBUG, INSTALL_MODE
# Arguments: Command-line arguments passed through to parse_args
# Outputs: Progress and planned action to STDOUT; errors to STDERR
# Returns: 0 on success, 1 otherwise
main() {
  parse_args "$@"

  if [[ "${DEBUG}" == true ]]; then
    set -x
  fi

  printf 'installer: repository: %s\n' "${REPO_URL}"
  printf 'installer: reference: %s\n' "${REF}"

  check_prerequisites
  trap cleanup EXIT
  detect_mode

  if [[ "${DRY_RUN}" == true ]]; then
    if [[ "${INSTALL_MODE}" == "update" ]]; then
      printf 'installer: dry run: would update the existing .agent/'
      printf ' and agent.sh from ref %s\n' "${REF}"
    else
      printf 'installer: dry run: would install .agent/ and agent.sh'
      printf ' from ref %s\n' "${REF}"
    fi
    printf 'installer: dry run complete; no changes were made\n'
    return 0
  fi

  if [[ "${INSTALL_MODE}" == "update" ]]; then
    update_files
  else
    retrieve_files
    place_files
    printf 'installer: install complete\n'
  fi
}

# Entry point: the empty-BASH_SOURCE branch supports piped execution
# (curl ... | bash), where the standard main guard would skip main.
if [[ "${BASH_SOURCE[0]:-}" == "${0}" || -z "${BASH_SOURCE[0]:-}" ]]; then
  main "$@"
fi
