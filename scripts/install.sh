#!/usr/bin/env bash
# Agentic AI Development-Workflow installer entry point (story S2.1, steps 1-4).
#
# Retrieves this script with a single command from inside a project
# repository, validates the documented host prerequisites (Bash and git),
# and performs a clean install: it clones the pinned release reference
# into a temporary directory, copies .agent/ into the project root, and
# removes the temporary directory on exit. When .agent/ already
# exists, it refreshes it through the consumer's own git
# (ai-assistant remote -> fetch -> diff preview -> confirmation ->
# checkout -> commit) so the change is recorded as a normal, reviewable
# project change. The entry script (.agent/start.sh) is recorded
# executable in the project's git index (update-index --chmod=+x) so
# executability survives environments that do not preserve file modes.
# The commit-msg hook ships inside .agent/ (.agent/githooks/commit-msg);
# gate enablement is handled by configure_commit_gate (see update mode).

set -euo pipefail

readonly DEFAULT_REPO_URL="https://github.com/daveonche/dev-orchestrator.git"
readonly DEFAULT_REF="v1.0.24"

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

Prepare the Agentic AI Development-Workflow installation in the
current project repository. When .agent/ already exists, the run
switches to update mode and refreshes the files through this
repository's git as one reviewable, revertable commit.

Options:
  --ref REF   Install from REF instead of the pinned default
              (${DEFAULT_REF})
  --dry-run   Report the planned action without changing anything
  --yes       Skip the update confirmation prompt (non-interactive use)
  --debug     Enable shell tracing for troubleshooting
  --help      Show this help and exit

Update mode replaces .agent/ with the pinned release, so local
customizations inside .agent/ (for example the read: list in
.aider.conf.yml) are overwritten after a warning; re-apply them.
Before applying, the incoming changes are shown and the update must be
confirmed on the terminal; pass --yes to skip that prompt.

When the retrieved reference ships the commit-msg hook, update mode
enables the commit message gate in this repository
(core.hooksPath=.agent/githooks) unless core.hooksPath is already set; an
existing value is left untouched with a warning. Unset anytime with:
  git config --unset core.hooksPath

Examples:
  curl -fsSL https://raw.githubusercontent.com/daveonche/dev-orchestrator/v1.0.24/scripts/install.sh | bash
  curl -fsSL https://raw.githubusercontent.com/daveonche/dev-orchestrator/v1.0.24/scripts/install.sh | bash -s -- --ref v1.0.0
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
  if [[ -e ".agent" ]]; then
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
  if [[ ! -d "${TMP_CLONE}/.agent" ||
      ! -f "${TMP_CLONE}/.agent/start.sh" ]]; then
    die "ref ${REF} does not contain the .agent files"
    return 1
  fi
  cp -R "${TMP_CLONE}/.agent" .agent
  chmod +x .agent/start.sh
  # Record executability explicitly so the consumer's next commit stores
  # 100755 for the entry script even with core.fileMode=false, and the
  # script runs immediately after the install.
  if ! git update-index --add --chmod=+x .agent/start.sh; then
    die "failed to record executability in the git index"
    return 1
  fi
  printf 'installer: placed .agent/ into the project root\n'
}

# Globals: None
# Arguments: None
# Outputs: None
# Returns: 0 when FETCH_HEAD ships .agent/githooks/commit-msg, 1 otherwise
fetch_has_githooks() {
  git cat-file -e "FETCH_HEAD:.agent/githooks/commit-msg" 2>/dev/null
}

# Globals: None
# Arguments: None
# Outputs: Progress to STDOUT; warnings to STDERR; errors to STDERR
# Returns: 0 when the gate is enabled or an existing setting is kept
configure_commit_gate() {
  local existing
  if existing="$(git config --get core.hooksPath 2>/dev/null)" \
      && [[ -n "${existing}" ]]; then
    if [[ "${existing}" == ".agent/githooks" ]]; then
      printf 'installer: commit message gate already active\n'
      return 0
    fi
    printf 'installer: WARNING: core.hooksPath is already set to %s\n' \
      "${existing}" >&2
    printf 'installer:   leaving it untouched; enable the gate later\n' >&2
    printf 'installer:   with: git config core.hooksPath .agent/githooks\n' >&2
    return 0
  fi
  if ! git config core.hooksPath .agent/githooks; then
    die "failed to enable the commit message gate (core.hooksPath)"
    return 1
  fi
  printf 'installer: commit message gate enabled (core.hooksPath=%s)\n' \
    '.agent/githooks'
  printf 'installer:   unset anytime with: git config --unset core.hooksPath\n'
}

# Globals: None
# Arguments: None
# Outputs: Overwrite warning to STDERR
# Returns: None
warn_overwrite() {
  printf 'installer: WARNING: the update replaces .agent/\n' >&2
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
      .agent/*) ;;
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
# Returns: 0 when the ai-assistant remote is available, 1 otherwise
ensure_assistant_remote() {
  local existing_url
  if existing_url="$(git remote get-url ai-assistant 2>/dev/null)"; then
    if [[ "${existing_url}" != "${REPO_URL}" ]]; then
      die "remote 'ai-assistant' exists but points to ${existing_url};"
      die "expected ${REPO_URL}"
      return 1
    fi
    return 0
  fi
  if ! git remote add ai-assistant "${REPO_URL}"; then
    die "failed to configure the ai-assistant remote (${REPO_URL})"
    return 1
  fi
}

# Globals: REF (read)
# Arguments: None
# Outputs: Error messages to STDERR
# Returns: 0 on successful fetch, 1 otherwise
fetch_assistant_ref() {
  if ! git fetch --quiet --depth 1 ai-assistant "${REF}"; then
    die "failed to retrieve ref ${REF}"
    return 1
  fi
}

# Globals: REF (read)
# Arguments: None
# Outputs: Change preview to STDOUT; warnings to STDERR
# Returns: None
preview_refresh() {
  printf 'installer: incoming changes from ref %s:\n' "${REF}"
  local base
  if git rev-parse --verify --quiet HEAD >/dev/null 2>&1; then
    base="HEAD"
  else
    # Unborn HEAD (no commits yet): diff against the empty tree so the
    # preview lists every .agent file as new instead of failing with
    # "bad revision 'HEAD'".
    base="$(git hash-object -t tree /dev/null)"
    printf 'installer: no commits yet; all .agent files are new\n'
  fi
  local paths=(.agent)
  git --no-pager diff --stat "${base}" FETCH_HEAD -- "${paths[@]}"
  if ! git diff --quiet -- "${paths[@]}"; then
    printf 'installer: WARNING: uncommitted local changes will be' >&2
    printf ' overwritten:\n' >&2
    git --no-pager diff --stat -- "${paths[@]}"
  fi
}

# Globals: ASSUME_YES (read)
# Arguments: None
# Outputs: Confirmation prompt to STDERR; error messages to STDERR
# Returns: 0 when the update is confirmed, 1 otherwise
confirm_refresh() {
  if [[ "${ASSUME_YES}" == true ]]; then
    return 0
  fi
  local reply
  printf 'installer: apply the update? [y/N] ' >&2
  if ! IFS= read -r reply < /dev/tty 2>/dev/null; then
    die "no terminal available for confirmation;"
    die "re-run with --yes to update non-interactively"
    return 1
  fi
  case "${reply}" in
    y | Y | yes | YES) ;;
    *)
      die "update aborted; no changes were made"
      return 1
      ;;
  esac
}

# Globals: REF (read)
# Arguments: None
# Outputs: Progress to STDOUT; errors to STDERR
# Returns: 0 when the refresh was applied or is already up to date
apply_refresh() {
  local paths=(.agent)
  # A path-limited checkout only copies paths present in FETCH_HEAD and
  # never removes paths that upstream renamed away, so clear the managed
  # paths from the index and worktree first: the refresh becomes a true
  # replacement and upstream deletions are staged in the same commit.
  # --ignore-unmatch keeps the removal safe when a path is untracked,
  # and the command does not reference HEAD, preserving the unborn-HEAD
  # handling of the no-op probe below.
  if ! git rm -r -f --quiet --ignore-unmatch -- "${paths[@]}"; then
    die "failed to clear the existing .agent files"
    return 1
  fi
  if ! git checkout FETCH_HEAD -- "${paths[@]}"; then
    die "failed to check out the .agent files from ref ${REF}"
    return 1
  fi
  # Record executability explicitly before the no-op probe: the index
  # stores 100755 for the entry script and the commit-msg hook even
  # with core.fileMode=false, and a mode-only difference still yields a
  # reviewable commit.
  if ! git update-index --chmod=+x .agent/start.sh; then
    die "failed to record executability in the git index"
    return 1
  fi
  chmod +x .agent/start.sh
  if fetch_has_githooks; then
    if ! git update-index --chmod=+x .agent/githooks/commit-msg; then
      die "failed to record commit-msg hook executability in the index"
      return 1
    fi
    chmod +x .agent/githooks/commit-msg
  fi
  # No explicit HEAD in the probe: git compares the index against HEAD
  # implicitly and treats an unborn HEAD as the empty tree, so a
  # repository with no commits reaches the commit below instead of
  # dying with "bad revision 'HEAD'".
  if git diff --cached --quiet -- "${paths[@]}"; then
    printf 'installer: already up to date at ref %s\n' "${REF}"
    return 0
  fi
  # Subject conforms to the commit-msg gate this installer may have
  # just enabled in the consumer's repository.
  if ! git commit --quiet \
      -m "chore(agent): update .agent files to ${REF}" \
      -- "${paths[@]}"; then
    die "failed to record the refresh as a commit"
    return 1
  fi
  printf 'installer: recorded the refresh as commit %s\n' \
    "$(git rev-parse --short HEAD)"
}

# Globals: REPO_URL, REF, ASSUME_YES (read)
# Arguments: None
# Outputs: Progress to STDOUT; warning and errors to STDERR
# Returns: 0 when the update completed, 1 otherwise
update_files() {
  printf 'installer: updating an existing install\n'
  warn_overwrite
  check_staged_scope
  ensure_assistant_remote
  fetch_assistant_ref
  preview_refresh
  confirm_refresh
  # Enable the gate after confirmation so an aborted update leaves the
  # repository configuration untouched, and before the refresh commit so
  # the installer's own commit passes through the gate it installs.
  if fetch_has_githooks; then
    configure_commit_gate
  fi
  apply_refresh
  printf 'installer: update complete\n'
}

# Globals: REPO_URL, REF, DRY_RUN, DEBUG, ASSUME_YES (modified)
# Arguments: Command-line arguments
# Outputs: Usage to STDOUT for --help; errors to STDERR
# Returns: 0 on success, 1 on invalid usage
parse_args() {
  REPO_URL="${DEFAULT_REPO_URL}"
  REF="${DEFAULT_REF}"
  DRY_RUN=false
  DEBUG=false
  ASSUME_YES=false
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
      --yes | -y)
        ASSUME_YES=true
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

# Globals: REPO_URL, REF, DRY_RUN, DEBUG, ASSUME_YES, INSTALL_MODE
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
      printf ' from ref %s\n' "${REF}"
    else
      printf 'installer: dry run: would install .agent/'
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
