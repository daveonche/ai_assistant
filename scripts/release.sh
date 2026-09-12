#!/usr/bin/env bash
# Release automation for the AIAssistant assistant files.
#
# Cuts a release in one command from a main checkout: verifies the
# repository state, runs a clean-tree preflight of the project's test
# suite, bumps the pinned release reference across the enforced trio
# (scripts/install.sh DEFAULT_REF, README.md curl URLs,
# tests/test_s2_1_step5.py INSTALL_COMMAND) plus the fixture references
# in the S2.1 test suites, re-validates with the test suite, records the
# bump as one commit, tags it, and pushes main and the tag.
# The CI release-tag-guard job re-checks the tag/DEFAULT_REF pin on the
# tag push, so a stale pin fails the release even when this script is
# bypassed. The new reference is passed explicitly or derived with
# --auto by incrementing the current pinned reference's patch segment.

set -euo pipefail

readonly DEFAULT_REPO_URL="https://github.com/daveonche/ai_assistant.git"
readonly RAW_URL_HOST="https://raw.githubusercontent.com/daveonche"
readonly RAW_URL_REPO="ai_assistant"
readonly BUMP_FILES=(
  "scripts/install.sh"
  "README.md"
  "tests/test_s2_1_step1.py"
  "tests/test_s2_1_step2.py"
  "tests/test_s2_1_step3.py"
  "tests/test_s2_1_step4.py"
  "tests/test_s2_1_step5.py"
)

# Globals: None
# Arguments: Variable list of message words, joined into one message
# Outputs: Error message prefixed with the script name to STDERR
# Returns: None
die() {
  printf '%s: error: %s\n' "${0##*/}" "$*" >&2
}

# Globals: None
# Arguments: None
# Outputs: Usage text with examples to STDOUT
# Returns: None
usage() {
  cat <<EOF
Usage: release.sh [options] [NEW_REF]

Cut a release of the AIAssistant assistant files from the current main
checkout. The pinned release reference is bumped across the enforced
trio (scripts/install.sh DEFAULT_REF, README.md curl URLs,
tests/test_s2_1_step5.py INSTALL_COMMAND) and the S2.1 fixture suites,
validated with the project's test suite, recorded as one commit, tagged,
and pushed together with main.

Options:
  NEW_REF     The release reference to cut (for example v1.0.3); it
              must be a v-prefixed version that has no tag yet
  --auto      Derive the release reference from the current pinned
              reference by incrementing its patch segment
              (v1.0.2 -> v1.0.3); mutually exclusive with NEW_REF
  --dry-run   Report the planned action without changing anything
  --verbose   Print per-file bump detail as it runs
  --debug     Enable shell tracing for troubleshooting
  --help      Show this help and exit

The repository must be on main, clean, and in sync with origin/main
before the bump starts; --dry-run previews the plan without the
repository-state checks. The test gate runs with the first
pytest-capable interpreter among the PYTHON_BIN override,
.venv/bin/python3, and python3 from the PATH. The suite runs twice: a
clean-tree preflight before the bump proves the environment can pass
it (a missing module or tool aborts with a clean tree), then the
post-bump run validates the bump itself. The bump replaces every
occurrence of the current pinned reference in the release files; the
--ref example arguments in the documentation keep their older tag on
purpose.

Examples:
  ./scripts/release.sh --dry-run v1.0.3
  ./scripts/release.sh v1.0.3
  ./scripts/release.sh --auto --dry-run
  ./scripts/release.sh --auto
  ./scripts/release.sh v1.0.3 --verbose
  ./scripts/release.sh v1.0.3 --debug
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
    die "run the release script from inside the project repository"
    return 1
  fi
}

# Globals: OLD_REF (set)
# Arguments: None
# Outputs: Error messages to STDERR
# Returns: 0 when DEFAULT_REF was read, 1 otherwise
read_current_ref() {
  local ref
  ref="$(sed -n 's/^readonly DEFAULT_REF="\(.*\)"$/\1/p' scripts/install.sh)"
  if [[ -z "${ref}" ]]; then
    die "could not read DEFAULT_REF from scripts/install.sh"
    return 1
  fi
  OLD_REF="${ref}"
}

# Globals: PYTHON_BIN (set); optional PYTHON_BIN env override (read)
# Arguments: None
# Outputs: Progress to STDOUT; error messages to STDERR
# Returns: 0 when a pytest-capable interpreter was selected, 1 otherwise
resolve_python() {
  # The test gate needs a pytest-capable interpreter. Precedence: the
  # PYTHON_BIN override, then the project virtual environment (.venv),
  # then python3 from the PATH. The probe runs here, before any file is
  # modified, so a missing pytest aborts the release with a clean tree.
  local candidate
  local -a candidates
  if [[ -n "${PYTHON_BIN:-}" ]]; then
    candidates=("${PYTHON_BIN}")
  elif [[ -x ".venv/bin/python3" ]]; then
    candidates=(".venv/bin/python3" "python3")
  else
    candidates=("python3")
  fi
  for candidate in "${candidates[@]}"; do
    if "${candidate}" -m pytest --version >/dev/null 2>&1; then
      PYTHON_BIN="${candidate}"
      printf 'release: test interpreter: %s\n' "${PYTHON_BIN}"
      return 0
    fi
  done
  die "no pytest-capable python interpreter found; tried:"
  die "${candidates[*]}"
  die "install pytest or set PYTHON_BIN to an interpreter that"
  die "has it"
  return 1
}

# Globals: OLD_REF, AUTO (read); NEW_REF (set)
# Arguments: None
# Outputs: Progress to STDOUT; error messages to STDERR
# Returns: 0 when NEW_REF is resolved, 1 otherwise
resolve_new_ref() {
  # With --auto, derive the release reference from the current pinned
  # reference by incrementing its patch segment (v1.0.2 -> v1.0.3).
  if [[ "${AUTO}" != true ]]; then
    return 0
  fi
  local version_re='^v([0-9]+)\.([0-9]+)\.([0-9]+)$'
  if [[ ! "${OLD_REF}" =~ ${version_re} ]]; then
    die "cannot auto-increment ${OLD_REF};"
    die "the current DEFAULT_REF must be vMAJOR.MINOR.PATCH"
    return 1
  fi
  local major="${BASH_REMATCH[1]}"
  local minor="${BASH_REMATCH[2]}"
  local patch="${BASH_REMATCH[3]}"
  NEW_REF="v${major}.${minor}.$((patch + 1))"
  printf 'release: auto: derived %s from %s\n' "${NEW_REF}" "${OLD_REF}"
}

# Globals: OLD_REF, NEW_REF (read)
# Arguments: None
# Outputs: Error messages to STDERR
# Returns: 0 when both references are valid and distinct, 1 otherwise
validate_refs() {
  local version_re='^v[0-9]+\.[0-9]+\.[0-9]+$'
  if [[ ! "${OLD_REF}" =~ ${version_re} ]]; then
    die "current DEFAULT_REF ${OLD_REF} is not a v-prefixed version"
    return 1
  fi
  if [[ ! "${NEW_REF}" =~ ${version_re} ]]; then
    die "release reference ${NEW_REF} must be a v-prefixed version"
    die "(for example v1.0.3)"
    return 1
  fi
  if [[ "${NEW_REF}" == "${OLD_REF}" ]]; then
    die "release reference ${NEW_REF} equals the current DEFAULT_REF"
    return 1
  fi
}

# Globals: NEW_REF (read)
# Arguments: None
# Outputs: Error messages to STDERR
# Returns: 0 when the repository is ready for a release, 1 otherwise
check_repo_state() {
  local branch
  branch="$(git rev-parse --abbrev-ref HEAD)"
  if [[ "${branch}" != "main" ]]; then
    die "releases are cut from main; the current branch is ${branch}"
    return 1
  fi
  if [[ -n "$(git status --porcelain)" ]]; then
    die "the work tree is not clean; commit or stash before releasing"
    return 1
  fi
  if ! git fetch --quiet origin; then
    die "failed to fetch origin; check the network and remote access"
    return 1
  fi
  if ! git rev-parse -q --verify origin/main >/dev/null 2>&1; then
    die "origin/main not found; push main to origin before releasing"
    return 1
  fi
  if [[ "$(git rev-parse HEAD)" != "$(git rev-parse origin/main)" ]]; then
    die "main is not in sync with origin/main; push or pull first"
    return 1
  fi
  if git rev-parse -q --verify "refs/tags/${NEW_REF}" >/dev/null 2>&1; then
    die "tag ${NEW_REF} already exists; choose a new reference"
    return 1
  fi
}

# Globals: OLD_REF, NEW_REF, VERBOSE (read)
# Arguments: None
# Outputs: Progress to STDOUT; error messages to STDERR
# Returns: 0 when every release file was bumped, 1 otherwise
bump_refs() {
  # BSD sed needs an explicit empty backup suffix; GNU sed takes -i bare.
  local sed_args=(-i)
  if ! sed --version >/dev/null 2>&1; then
    sed_args=(-i "")
  fi
  local file
  for file in "${BUMP_FILES[@]}"; do
    if [[ ! -f "${file}" ]]; then
      die "release file not found: ${file}"
      return 1
    fi
    sed "${sed_args[@]}" "s/${OLD_REF}/${NEW_REF}/g" "${file}"
    if [[ "${VERBOSE}" == true ]]; then
      printf 'release: bumped %s\n' "${file}"
    fi
  done
  if git diff --quiet -- "${BUMP_FILES[@]}"; then
    die "the bump changed nothing; ${OLD_REF} was not found in the"
    die "release files; check the pinned reference and the file list"
    return 1
  fi
  printf 'release: bumped the pinned reference in %s files\n' \
    "${#BUMP_FILES[@]}"
  if [[ "${VERBOSE}" == true ]]; then
    git --no-pager diff --stat
  fi
}

# Globals: PYTHON_BIN (read)
# Arguments: None
# Outputs: Test output passthrough; error messages to STDERR
# Returns: 0 when the clean-tree suite passes, 1 otherwise
preflight_tests() {
  # Prove the environment can pass the full suite before any file is
  # modified: a missing module or tool (pytest, PyYAML, shellcheck)
  # aborts the release with a clean tree instead of after the bump.
  printf 'release: preflight: validating the clean tree with the'
  printf ' project test suite\n'
  if ! "${PYTHON_BIN}" -m pytest -q; then
    die "the preflight suite failed; the environment cannot validate"
    die "the release; fix it and re-run; no files were modified"
    return 1
  fi
}

# Globals: BUMP_FILES, PYTHON_BIN (read)
# Arguments: None
# Outputs: Test output passthrough; error messages to STDERR
# Returns: 0 when the test suite passes, 1 otherwise
run_tests() {
  printf 'release: validating the bump with the project test suite\n'
  if ! "${PYTHON_BIN}" -m pytest -q; then
    die "the test suite failed; inspect the output above and restore"
    die "the bump with: git restore ${BUMP_FILES[*]}"
    return 1
  fi
}

# Globals: NEW_REF, BUMP_FILES (read)
# Arguments: None
# Outputs: Progress to STDOUT; error messages to STDERR
# Returns: 0 when the bump commit was recorded, 1 otherwise
record_bump() {
  if ! git add -- "${BUMP_FILES[@]}"; then
    die "failed to stage the bumped release files"
    return 1
  fi
  if ! git commit --quiet \
      -m "chore(release): bump pinned reference to ${NEW_REF}"; then
    die "failed to record the bump as a commit"
    return 1
  fi
  printf 'release: recorded the bump as commit %s\n' \
    "$(git rev-parse --short HEAD)"
}

# Globals: NEW_REF (read)
# Arguments: None
# Outputs: Progress to STDOUT; error messages to STDERR
# Returns: 0 when the annotated tag was created, 1 otherwise
tag_release() {
  if ! git tag -a "${NEW_REF}" -m "Release ${NEW_REF}"; then
    die "failed to create the annotated tag ${NEW_REF}"
    return 1
  fi
  printf 'release: tagged the bump commit as %s\n' "${NEW_REF}"
}

# Globals: NEW_REF (read)
# Arguments: None
# Outputs: Progress to STDOUT; error messages to STDERR
# Returns: 0 when main and the tag were pushed, 1 otherwise
push_release() {
  if ! git push --quiet origin main "${NEW_REF}"; then
    die "failed to push main and ${NEW_REF} to origin;"
    die "re-run the push with: git push origin main ${NEW_REF}"
    return 1
  fi
  printf 'release: pushed main and %s to origin\n' "${NEW_REF}"
}

# Globals: OLD_REF, NEW_REF (read)
# Arguments: None
# Outputs: Planned action to STDOUT
# Returns: None
report_plan() {
  printf 'release: dry run: would bump the pinned reference from'
  printf ' %s to %s in %s files\n' "${OLD_REF}" "${NEW_REF}" \
    "${#BUMP_FILES[@]}"
  printf 'release: dry run: would check the repository state, run the'
  printf ' clean-tree preflight, then bump, validate, commit, tag'
  printf ' %s, and push main and the tag\n' "${NEW_REF}"
  printf 'release: dry run complete; no changes were made\n'
}

# Globals: NEW_REF, DRY_RUN, DEBUG, VERBOSE, AUTO (modified)
# Arguments: Command-line arguments
# Outputs: Usage to STDOUT for --help; errors to STDERR
# Returns: 0 on success, 1 on invalid usage
parse_args() {
  NEW_REF=""
  DRY_RUN=false
  DEBUG=false
  VERBOSE=false
  AUTO=false

  while [[ "$#" -gt 0 ]]; do
    case "${1}" in
      --auto)
        AUTO=true
        shift
        ;;
      --dry-run)
        DRY_RUN=true
        shift
        ;;
      --verbose | -v)
        VERBOSE=true
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
      --*)
        die "unknown option: ${1}"
        usage >&2
        return 1
        ;;
      *)
        if [[ -n "${NEW_REF}" ]]; then
          die "unexpected argument: ${1}"
          usage >&2
          return 1
        fi
        if [[ "${AUTO}" == true ]]; then
          die "NEW_REF and --auto are mutually exclusive"
          usage >&2
          return 1
        fi
        NEW_REF="${1}"
        shift
        ;;
    esac
  done

  if [[ -z "${NEW_REF}" && "${AUTO}" != true ]]; then
    die "a release reference is required (for example v1.0.3),"
    die "or pass --auto to increment the current patch segment"
    usage >&2
    return 1
  fi
}

# Globals: NEW_REF, DRY_RUN, DEBUG, VERBOSE, AUTO, OLD_REF, PYTHON_BIN
# (read/set)
# Arguments: Command-line arguments passed through to parse_args
# Outputs: Progress and planned action to STDOUT; errors to STDERR
# Returns: 0 on success, 1 otherwise
main() {
  parse_args "$@"

  if [[ "${DEBUG}" == true ]]; then
    set -x
  fi

  printf 'release: repository: %s\n' "${DEFAULT_REPO_URL}"

  check_prerequisites
  # Anchor to the repository root so the release file lists resolve
  # regardless of the invocation directory inside the work tree.
  cd "$(git rev-parse --show-toplevel)" || exit 1
  read_current_ref
  resolve_new_ref
  validate_refs
  printf 'release: cutting %s\n' "${NEW_REF}"
  printf 'release: pinned reference: %s -> %s\n' "${OLD_REF}" "${NEW_REF}"

  if [[ "${DRY_RUN}" == true ]]; then
    report_plan
    return 0
  fi

  resolve_python
  check_repo_state
  preflight_tests
  bump_refs
  run_tests
  record_bump
  tag_release
  push_release

  printf 'release: %s pushed; once the release-tag-guard job passes,\n' \
    "${NEW_REF}"
  printf 'release: verify the served installer at\n'
  printf 'release: %s/%s/%s/scripts/install.sh\n' \
    "${RAW_URL_HOST}" "${RAW_URL_REPO}" "${NEW_REF}"
}

# Entry point: run main only on direct execution.
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  main "$@"
fi
