# Sprint 4 Stories

## Story S4.1: Mergeable Aider Configuration with Project Root

As a developer, I want the launcher to make `.agent/`'s `.aider.conf.yml`, `.aider.model.settings.yml`, and `.aiderignore` mergeable with same-named files found in the project root, so that consumer projects can override or extend assistant defaults without editing the installed assistant files.

Acceptance Criteria:

- When a project-root counterpart of any of the three config files exists, the launcher combines the `.agent/` and project-root versions instead of passing only the `.agent/` copy
- Project-root values take precedence over `.agent/` defaults for `.aider.conf.yml` and `.aider.model.settings.yml`; ignore patterns are combined (union) for `.aiderignore`
- When no project-root counterpart exists, launcher behavior is unchanged from the current single-file pass-through
- Merging is deterministic and the merge behavior is documented (README or prerequisite docs)
- Verification suites cover: merge case, no-counterpart case, and precedence rules

Dependencies: None

Developer Notes:

- Maps to environment/launcher requirements REQ-1, REQ-2
- Current behavior: `_aider_config_args()` in `.agent/ai_assistant.py` passes `--config`, `--model-settings-file`, and `--aiderignore` pointing solely at the `.agent/` copies
- The launcher is stdlib-only Python (host pin 3.12.12) — implement YAML-aware merging within that constraint
- Shell/Python changes must pass the existing static checks and verification suites

## Story S4.2: Framework Detection and Conventions Recommendation

As a developer, I want the assistant to detect the framework used in the `src/` directory and recommend the matching conventions file from `.agent/.aider.conventions/` (e.g., `ELGG.md`, `RAILS.md`), so that coding guidance automatically follows the detected framework's conventions.

Acceptance Criteria:

- The assistant inspects the project (framework indicators under `src/` and root manifests/config files) to identify the framework in use
- When a detected framework has a matching conventions file in `.agent/.aider.conventions/`, the assistant recommends loading it via `/read-only`, following the routing conventions in `.agent/AGENTS.md`
- When no matching conventions file exists for the detected framework, no recommendation is made
- Seed convention files `ELGG.md` and `RAILS.md` are added to `.agent/.aider.conventions/` with meaningful starter content and pass the markdown conventions
- The framework-based routing rule is documented in the conventions routing table in `.agent/AGENTS.md`

Dependencies: None

Developer Notes:

- Maps to REQ-7 (project-specific prompt library) and REQ-9 (SDLC best practices enforcement)
- Detection is performed by the LLM via AGENT.md orchestration instructions (indicators such as `composer.json`, `Gemfile`, `package.json`), not by launcher code
- Creating/editing `ELGG.md`, `RAILS.md`, and `AGENT.md` requires the GFM conventions reference (already in context) and, per the routing table, the agent-skills reference for `SKILL.md` files if any are touched

## Story S4.3: README `--auto` Release Example Fix

As a developer, I want the `--auto` increment example in the README "Cutting a release" section corrected, so that it shows the patch segment changing and matches the usage text in `scripts/release.sh`.

Acceptance Criteria:

- The README `--auto` example shows the patch segment changing (e.g., `v1.0.3` -> `v1.0.4`), consistent with the correct usage example in `scripts/release.sh` (`v1.0.2` -> `v1.0.3`)
- The full test suite remains green (release-reference consistency checks unaffected)
- Documentation passes the markdown conventions

Dependencies: None

Developer Notes:

- Supports REQ-15 (release-reference consistency across documented instructions)
- Resolves the non-blocking nit recorded in `docs/implementation_status.md`; documentation-only
- GFM conventions reference already in context

## Story S4.4: Sprint 4 Record Documentation

As a developer, I want the Sprint 4 work recorded in the project docs, so that the sprint history and implementation status reflect the config-merging, framework-detection, and README-fix work.

Acceptance Criteria:

- `docs/implementation_status.md` gains a Sprint 4 section listing the S4.1, S4.2, and S4.3 work as completed steps, and its Priority Order section is updated to reflect the new backlog state
- Documentation passes the markdown conventions

Dependencies: S4.1, S4.2, S4.3

Developer Notes:

- Follows the Sprint 3 record-keeping pattern (S3.3, Sprint 3 section in `docs/implementation_status.md`)
- Documentation-only; GFM conventions reference already in context

## Sprint Technical Rationale

These stories pair the two user-introduced features (config merging, framework-aware conventions) with the one recorded documentation nit, then close the sprint by recording all three. S4.1 and S4.2 are independent and have no dependency on S4.3, so the three feature stories can proceed in any order; S4.4 depends on all of them.
