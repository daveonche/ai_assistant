# Sprint 2 Stories

## Story S2.1: Assistant-File Installer (One-Command Install & Update)

As a developer, I want a single-command installer that drops `.agent/` and `agent.sh` into a project repo and keeps them updatable so that consuming projects get frictionless setup and repeatable updates.

Acceptance Criteria:

- `scripts/install.sh` installs `.agent/` and `agent.sh` into the current project repo with one command (e.g., `curl -fsSL <url>/install.sh | bash`), with no new host prerequisites beyond Bash and git
- Install mode: clones the pinned release ref (tag, not `main`), copies `.agent/` and `agent.sh`, and makes entry scripts executable
- Update mode: when `.agent/` or `agent.sh` already exist, syncs via the consumer's git (`git remote add assistant` → fetch → `git checkout <ref> -- .agent agent.sh` → commit), keeping changes diffable and revertable
- Executable bit is recorded in the git index via `git update-index --chmod=+x` for `agent.sh` and `.agent/ai-assistant.sh`, robust to `core.fileMode=false`
- Entry scripts in this repo are committed with mode `100755` so the update path preserves executability
- Update mode warns that local customizations inside `.agent/` (e.g., the `read:` list in `.aider.conf.yml`) will be overwritten
- README documents the one-command install and update flow, including the pinned-ref caveat
- Script passes shellcheck per `.agent/.aider.conventions/references/bash-scripts.md`

Dependencies: S1.1, S1.2, S1.5

Developer Notes:

- Load the bash conventions reference before implementation (routing table)
- Reuse the pinned image/ref philosophy from `docs/tech_stack.md`; pin the install ref to a tag
- Tests follow existing patterns: shellcheck/static checks (`tests/test_s1_2_step3.py` style) and sandbox behavior tests (`tests/test_s1_2_step5.py` style)
- Keep the script thin; no config or launcher changes

Definition of Done:

- One command installs into a clean project repo; `git ls-files -s` shows `100755` for both entry scripts
- Re-running the script updates an existing install through the consumer's git
- shellcheck passes; sandbox tests green

## Story S2.2: Release Version-Pin Resolution

As a developer, I want the remaining version-pin flags resolved so that the project is release-ready with a fully pinned toolchain.

Acceptance Criteria:

- Exact host Python runtime version pinned and recorded in `docs/tech_stack.md` (resolving the S1.2 ⚠ FLAGGED item)
- `requires-python` minimum in `.agent/pyproject.toml` resolved and justified (resolving the S1.4 ⚠ FLAGGED item)
- README prerequisites and `docs/tech_stack.md` compatibility matrix updated consistently
- Flag annotations in `docs/sprints/sprint_1_stories.md` updated to resolved status

Dependencies: None

Developer Notes:

- Documentation/config-level only; no launcher or script changes
- Follow the existing version-lock rationale format in `docs/tech_stack.md`

Definition of Done:

- No remaining ⚠ FLAGGED version-pin items in sprint story docs
- `docs/tech_stack.md` and README prerequisites agree with `.agent/pyproject.toml`

## Sprint Technical Rationale

These stories follow the approved priority order: S2.1 delivers the Priority 1 installer feature (extending REQ-FR-ENV-3 with a repeatable install/update path), and S2.2 clears the Priority 2 release-readiness flags. The stories are independent, so S2.2 may proceed in parallel.
