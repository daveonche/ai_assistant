# Implementation Status

## Sprint 1

### Story S1.1: Initial Project Creation and Configuration

- [x] Step 1. Enable version-controlled repository initialization
- [x] Step 2. Enable the layered project layout
- [x] Step 3. Enable placeholder tracking for empty directories
- [x] Step 4. Enable transient artifact exclusion
- [x] Step 5. Enable project licensing and readme documentation
- [x] Step 6. Enable architecture alignment confirmation

### Story S1.2: Development Environment Setup

- [x] Step 1. Enable single-command host entry delegation
- [x] Step 2. Enable argument and debug-flag forwarding
- [x] Step 3. Enable executable entry scripts that pass static checks
- [x] Step 4. Enable prerequisite documentation for first use
- [x] Step 5. Enable dual-mode installation support

### Story S1.3: Core Architecture Implementation (Launcher Layer)

- [x] Step 1. Enable launcher entry and argument forwarding
- [x] Step 2. Enable command tracing and debug output
- [x] Step 3. Enable container engine availability gating
- [x] Step 4. Enable deterministic session container identity
- [x] Step 5. Enable container image build management
- [x] Step 6. Enable assistant configuration argument assembly
- [x] Step 7. Enable interactive assistant session launch
- [x] Step 8. Enable session container cleanup

### Story S1.4: Aider Configuration and AGENT.md Setup

- [x] Step 1. Enable Aider configuration file creation
- [x] Step 2. Enable model settings configuration
- [x] Step 3. Enable context exclusion rules
- [x] Step 4. Enable AGENT.md workflow and context management rules

### Story S1.5: Essential Infrastructure (Containerization Layer)

- [x] Step 1. Enable reproducible container image build from a pinned base image
- [x] Step 2. Enable read-write project root access inside the session container
- [x] Step 3. Enable container engine access from inside the container
- [x] Step 4. Enable deterministic session container identity and automatic cleanup
- [x] Step 5. Enable credential passing at launch only

### Story S1.6: Initial Build Pipeline (CI Validation)

- [x] Step 1. Enable the automated validation pipeline definition
- [x] Step 2. Enable launcher source code validation in the pipeline
- [x] Step 3. Enable shell script validation in the pipeline
- [x] Step 4. Enable container image build validation in the pipeline
- [x] Step 5. Enable end-to-end pipeline result confirmation on a clean tree

### Story S1.7: Basic Developer Workflow (Orchestration & Prompt Library)

- [x] Step 1. Enable prompt directory structure
- [x] Step 2. Enable prompt file creation
- [x] Step 3. Enable shorthand command mapping
- [x] Step 4. Enable context management rules in AGENT.md
- [x] Step 5. Enable prompt loading and dropping verification

### Story S1.8: Logging, Configuration & Environment Management

- [x] Step 1. Enable engine command tracing and debug logging
- [x] Step 2. Enable progress feedback during long operations
- [x] Step 3. Enable credential handling at launch
- [x] Step 4. Enable empty artifact cleanup
- [x] Step 5. Enable logging and debug documentation

## Sprint 2

### Story S2.1: Assistant-File Installer (One-Command Install & Update)

- [x] Step 1. Enable single-command acquisition of the assistant files
- [x] Step 2. Enable clean-install placement of the assistant files
- [x] Step 3. Enable repeatable updates through the project's own history
- [x] Step 4. Enable executable entry scripts that survive mode-insensitive environments
- [x] Step 5. Enable documented install and update procedures
- [x] Step 6. Enable installer conformance with project quality checks

### Story S2.2: Release Version-Pin Resolution

- [x] Step 1. Enable the exact host runtime version pin in the technology-stack documentation
- [x] Step 2. Enable the resolved minimum runtime version for the assistant package
- [x] Step 3. Enable consistent prerequisite documentation across the readme and compatibility matrix
- [x] Step 4. Enable resolved-status annotations for the flagged version items

## Sprint 3

### Story S3.1: Release Reference Consistency Verification

- [x] Step 1. Enable confirmation that the pinned release reference agrees across the installer, the documented install instructions, and the tested install command
- [x] Step 2. Enable resolution of any detected reference inconsistency within a single change
- [x] Step 3. Enable recorded evidence of the passing verification

### Story S3.2: Release Tag Guard Verification

- [x] Step 1. Enable confirmation that the release tag guard job triggers on version-tag pushes and enforces the pinned reference
- [x] Step 2. Enable confirmation that all pipeline action references remain pinned to verified full-length commit SHAs
- [x] Step 3. Enable recorded evidence of a green pipeline run on the current main branch

### Release Script Work

- [x] Enable the release script and its verification suites

## Sprint 4

### Story S4.1: Mergeable Aider Configuration with Project Root

- [x] Step 1. Enable project-root counterpart discovery for the four mergeable config files (`.agent/ai_assistant.py` `_root_config_counterparts()`; verified by `tests/test_s4_1_step1.py`)
- [x] Step 2. Enable value-based config merging with project-root precedence (`.agent/ai_assistant.py` `_deep_merge()`, `_merge_model_settings()`, `_write_merged_value_file()`; verified by `tests/test_s4_1_step2.py`)
- [x] Step 3. Enable ignore-pattern union merging (`.agent/ai_assistant.py` `_merge_aiderignore()`, `_write_merged_ignore_file()`; verified by `tests/test_s4_1_step3.py`)
- [x] Step 4. Enable documented merge behavior in the readme (`README.md` "Mergeable configuration with your project root")
- [x] Step 5. Enable end-to-end launch verification of the merge behavior (verified by `tests/test_s4_1_step5.py`)

### Story S4.2: Framework Detection and Conventions Recommendation

- [x] Step 1. Enable framework detection instructions in the orchestration config (`.agent/AGENTS.md` "Project Framework Detection")
- [x] Step 2. Enable framework-based conventions recommendation and routing rules (`.agent/AGENTS.md` framework conventions rules; verified by `tests/test_s4_2_step2.py`)
- [x] Step 3. Enable unit-test verification of the detection and recommendation behavior (verified by `tests/test_s4_2_step3.py`)

### Story S4.3: README `--auto` Release Example Fix

- [x] Step 1. Enable a corrected automatic-increment example in the release documentation (`README.md` "Cutting a release" `--auto` example; verified by `tests/test_s4_3_step1.py`)
- [x] Step 2. Enable confirmation that the documentation edit preserves release-reference consistency (full verification suite green, including `tests/test_release_ref_consistency.py`)
- [x] Step 3. Enable documentation-conventions conformance for the edited section (verified by `tests/test_s4_3_step3.py`)

### Story S4.5: Container SSH Support for Git Remotes

- [x] Step 1. Enable read-only host `~/.ssh` mount and ssh-agent socket forwarding (`.agent/ai_assistant.py` `run_container()`; `openssh-client` in `.agent/Dockerfile.aider` Layer A; verified by `tests/test_s1_5_step2.py`)
- [x] Step 2. Enable guarded per-user ssh-agent bootstrap in the entry script (`.agent/ai-assistant.sh`; interactive-only, best-effort, never fails the launch)
- [x] Step 3. Enable fingerprint-verified GitHub host-key pinning for `github.com` (`.agent/ai-assistant.sh`; embedded ed25519/ecdsa blobs split into 80-character literals, rsa key fetched from `api.github.com` and fingerprint-gated, idempotent via `ssh-keygen -F`; verified by fingerprint re-derivation and `tests/test_s1_2_step3.py`)
- [x] Step 4. Enable documented SSH usage and the key-rotation caveat (`README.md` "SSH access for git remotes")

### Story S4.6: Container Build Tooling Fixes

- [x] Step 1. Enable docker-buildx-plugin in the image for in-container compose builds (`.agent/Dockerfile.aider` Layer C; exercised by the CI image build smoke test)
- [x] Step 2. Enable Buildx state redirection to the writable cache mount (`.agent/ai_assistant.py` `run_container()` `BUILDX_CONFIG=/home/.cache/buildx`; verified by `tests/test_s1_5_step2.py`)

### Story S4.7: Container Image Pins and Offline Pre-bakes

- [x] Step 1. Enable the image-internal component pin record (`docs/tech_stack.md` "Image-Internal Component Pins": ShellCheck v0.10.0 static binary, pytest 8.3.5, the pre-baked embedding model, Node.js 22.x, mermaid-cli ^11, distro-managed packages)
- [x] Step 2. Enable the exact-pin scope statement and accepted-deviation note (`docs/tech_stack.md` "Version Lock Rationale")

## Priority Order for Next Implementation Phase

The Sprint 3 release-management work (REQ-15) is verified and recorded:
release-reference consistency, the release tag guard, and the release script
all pass their verification suites. All Sprint 4 stories (S4.1 mergeable root
configuration, S4.2 framework detection and conventions recommendation, S4.3
README `--auto` release example fix, S4.5 container SSH support for git
remotes, S4.6 container build tooling fixes, S4.7 container image pins and
offline pre-bakes, and the S4.4 record-keeping story) are implemented and
verified; their source evidence is recorded in the Sprint 4 section above.
Every requirement (REQ-1 through REQ-15) is implemented with source evidence,
and the backlog is empty.

Post-Sprint-4 orchestration-config hygiene work (REQ-7, REQ-9, REQ-12, and
REQ-13) is also implemented and verified: one-line droppable format and
sweep-before-request context-hygiene rules in `.agent/AGENTS.md` (commit
af20f11), the one-line `/read-only`/`/add` file-request format with Critical
Rule 5 in `.agent/AGENTS.md` (commit 781ac6e), and default project input
locations baked into the implementation-analysis prompt
`.agent/.aider.prompt/planning/implementation-analysis/SKILL.md`
(commit 70d0e84); the full suite stayed green after each change.

Priority 1 - New capability intake:

- No outstanding requirements remain; the next sprint requires user-introduced features or requirements (the same pattern that produced Sprint 4's S4.1-S4.3 and S4.5-S4.7)

Next workflow step: `#generate-sprint-stories`
