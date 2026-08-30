# Scaffolding Sprint Stories

## Story S1.1: Initial Project Creation and Configuration

As a developer, I want to set up the basic project structure with core configuration so that we have a working foundation for the AIAssistant repository.

Acceptance Criteria:

- Project is created as a git repository with the layered layout: `agent.sh`, `.agent/`, `docs/`, `scripts/`, `src/`
- `docs/`, `scripts/`, `src/` exist with `.gitkeep` placeholders
- `.gitignore` excludes transient/runtime artifacts (logs, secrets, container output)
- `LICENSE` and `README.md` are in place
- Structure matches `docs/architecture/architecture.md` layer definitions

Dependencies: None

Developer Notes:

- No framework CLI applies; this is a stdlib-only Python launcher + configuration-as-code project
- Keep `.agent/` as the single home for all assistant configuration
- Follow team's agreed-upon project structure per `docs/architecture/architecture.md`

Definition of Done:

- Repository clones cleanly with the documented layout
- Required configuration files exist (`.gitignore`, `LICENSE`, `README.md`)
- All tracked markdown files pass GFM conventions checks

## Story S1.2: Development Environment Setup

As a developer, I want a single-command host entry script with documented prerequisites so that launching the assistant is frictionless and free of local dependency conflicts.

Acceptance Criteria:

- `agent.sh` delegates all lifecycle logic to `.agent/ai_assistant.py` via `.agent/ai-assistant.sh` (REQ-FR-ENV-2, REQ-FR-ENV-5)
- `agent.sh` forwards the debug flag and assistant arguments to the launcher
- Prerequisites documented: Docker (CLI & Compose Plugin), Bash, Python >=3.8 (host)
- Script is executable and passes shellcheck per `.agent/.aider.conventions/references/bash-scripts.md`
- Supports both standalone clone use and copy-into-project use (REQ-FR-ENV-3, REQ-FR-ENV-5)

Dependencies: S1.1

Developer Notes:

- Keep `agent.sh` a thin wrapper; all container lifecycle logic lives in the Python launcher
- Python >=3.8 is a minimum constraint from `.agent/pyproject.toml` — ⚠ FLAGGED: pin the exact host runtime version before release
- Docker and Bash versions are host-provided; no pin required

Definition of Done:

- `./agent.sh` starts the launcher on a clean machine with prerequisites installed
- Missing-prerequisite path exits with a clear error message
- shellcheck passes with no warnings

## Story S1.3: Core Architecture Implementation (Launcher Layer)

As a developer, I want the Python launcher implementing Docker availability check, image build, container run/cleanup, and config argument assembly so that the full container lifecycle is managed (REQ-FR-ENV-1).

Acceptance Criteria:

- `.agent/ai_assistant.py` uses only the Python standard library (>=3.8)
- Implements `_docker_available()` gate with clear exit errors; `build_image()`; `run_container()`; `cleanup_containers()`
- Config argument assembly via `_aider_config_args()` reading `.agent/` config files
- Command tracing via `_trace_command()`; `--debug` flag for verbose output
- Container identity derived from workspace hash + session ID

Dependencies: S1.2

Developer Notes:

- Honor the interface contract: `agent.sh` → `.agent/ai_assistant.py` CLI arguments (debug flag, assistant args forwarded to aider)
- Match launcher-layer responsibilities in `docs/architecture/architecture.md`

Definition of Done:

- Launcher runs with `--debug` and traces every Docker command
- Missing Docker exits with a clear, actionable error
- Python syntax/lint checks pass

## Story S1.4: Basic App Structure (Aider Configuration Files)

As a developer, I want the aider configuration files in place so that runtime behavior, model settings, and context filtering are controlled as code.

Acceptance Criteria:

- `.agent/.aider.conf.yml` defines runtime behavior (on-demand prompt loading, conventions routing)
- `.agent/.aider.model.settings.yml` defines model settings
- `.agent/pyproject.toml` declares `requires-python = ">=3.8"` — ⚠ FLAGGED: pin exact minimum version before release
- `.agent/.aiderignore` excludes non-essential paths from context (REQ-NFR-PERF-1, REQ-FR-TM-2)
- All config files are git-tracked and referenced in `docs/tech_stack.md`

Dependencies: S1.1

Developer Notes:

- `.aiderignore` directly supports isolated context per atomic step (REQ-FR-TM-2)
- Keep config minimal; add entries only when a workflow requires them

Definition of Done:

- Launcher assembles correct aider args from these configs (verified via `--debug` trace)
- All config files parse as valid YAML/TOML

## Story S1.5: Essential Infrastructure (Containerization Layer)

As a developer, I want the Dockerfile and container runtime wiring so that aider runs in an isolated container with full access to the host project.

Acceptance Criteria:

- `.agent/Dockerfile.aider` builds `FROM paulgauthier/aider-full:latest` — ⚠ FLAGGED: "latest" must be pinned to an exact tag/digest before implementation
- Host project root (including `.agent/`) is bind-mounted read-write into the container (REQ-FR-ENV-4)
- Docker socket GID mapped via `_get_docker_gid()` so the container can run Docker commands
- Container named from workspace hash + session ID; `cleanup_containers()` removes session containers
- API keys passed through the launcher as environment variables only (no secrets in tracked files)

Dependencies: S1.3, S1.4

Developer Notes:

- Pin the base image tag/digest and record it in `docs/tech_stack.md` before implementation
- Docker and Bash versions inside the image are base-image-provided; no pin required

Definition of Done:

- Image builds successfully from `.agent/Dockerfile.aider`
- Container starts, mounts the project root, and reaches the aider prompt
- Docker-in-container works (socket GID mapping verified)
- Session container is removed on exit

## Story S1.6: Initial Build Pipeline (CI Validation)

As a developer, I want a CI pipeline validating the launcher, scripts, and image build so that regressions are caught early.

Acceptance Criteria:

- `.github/workflows/ci.yml` validates: Python syntax/lint of `.agent/ai_assistant.py`, shellcheck of `*.sh` scripts, Docker image build
- CI config follows `.agent/.aider.conventions/references/ci-cid-best-practices.md`
- Pipeline fails on any validation error; passes on a clean tree
- All actions pinned to exact versions — ✓ SATISFIED: `actions/checkout` pinned to full SHA `11bd71901bbe5b1630ceea73d27597364c9af683` (v4.2.2), verified per `docs/tech_stack.md`

Dependencies: S1.5

Developer Notes:

- Keep CI minimal: lint + build smoke test; no test framework exists yet
- The Docker build job must mirror the launcher's `build_image()` invocation

Definition of Done:

- CI runs green on the scaffolding commit
- Failed lint or build blocks merge

## Story S1.7: Basic Developer Workflow (Orchestration & Prompt Library)

As a developer, I want `AGENTS.md` orchestration, the SDLC prompt library, and conventions loaded on demand so that workflows run with minimal token usage.

Acceptance Criteria:

- `.agent/AGENTS.md` routes `$` commands to `.agent/.aider.prompt/**/SKILL.md` via `/read-only` and `/drop` (REQ-FR-WF-2)
- Prompt library covers SDLC phases: planning, requirements, architecture, code, testing, documentation, workflows (REQ-FR-WF-1)
- Conventions in `.agent/.aider.conventions/` routed by file type per the routing table (REQ-FR-WF-3)
- Prompts loaded via `/read-only` only; nothing auto-loaded at startup (REQ-FR-TM-2, REQ-NFR-PERF-1)
- Every `SKILL.md` contains the Convention Check Reminder line

Dependencies: S1.4

Developer Notes:

- Orchestration enforces `[STOP]` gates and re-prompts on invalid input
- Context management is critical: drop prompts when a workflow finishes

Definition of Done:

- `$agent-orchestrator` lists built-in commands and loads a workflow on demand
- A full chain phase (e.g., `$planning-vision-statement`) runs end-to-end in `/ask` mode
- No prompt file is loaded unless its command was used

## Story S1.8: Logging, Configuration & Environment Management

As a developer, I want launcher logging, spinner feedback, and environment/secret handling so that operation is observable and credentials stay out of the repository.

Acceptance Criteria:

- `_trace_command()` logs every Docker command; `--debug` enables verbose output and log tailing via `_tail_lines()`
- `_print_spinner_update()` provides progress feedback during long operations
- API keys passed via environment variables at launch; never written to tracked files
- `_remove_if_empty()` cleans up empty artifacts
- Logging/debug behavior documented in `README.md`

Dependencies: S1.3

Developer Notes:

- Logging is launcher-level only; inside the container, aider handles its own output
- Never echo secret values in command traces

Definition of Done:

- Debug run shows the full command trace without leaking secrets
- Non-debug run shows spinner updates only
- No credentials present in git-tracked files

## Technical Dependencies Graph

```text
S1.1 (Project Creation & Configuration)
├── S1.2 (Development Environment Setup)
│   └── S1.3 (Launcher Layer)
│       ├── S1.5 (Containerization Layer)  ← also depends on S1.4
│       │   └── S1.6 (CI Validation)
│       └── S1.8 (Logging & Environment Management)
└── S1.4 (Aider Configuration Files)
    ├── S1.5 (Containerization Layer)
    └── S1.7 (Orchestration & Prompt Library)
```

Execution order: S1.1 → S1.2 → S1.3 → S1.4 → S1.5 → S1.6 → S1.7 → S1.8 (S1.4 may proceed in parallel after S1.1; S1.8 may proceed in parallel after S1.3)

## Verification Checkpoints

- After S1.1: repository clones cleanly; layout matches architecture docs
- After S1.2: `./agent.sh` reaches the launcher; shellcheck passes
- After S1.3: launcher traces Docker commands with `--debug`; clean exit on missing Docker
- After S1.4: launcher assembles correct aider args from config files
- After S1.5: container builds, starts, mounts project root, Docker-in-container works, cleanup removes container
- After S1.6: CI green on scaffolding commit
- After S1.7: on-demand prompt loading verified end-to-end in `/ask` mode
- After S1.8: debug trace shows no secrets; no credentials in tracked files
