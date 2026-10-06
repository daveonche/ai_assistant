# Sprint 6 Stories

## Story S6.1: Install-Surface Consolidation (Single-Directory Install)

As a developer, I want all core assistant files consolidated under `.agent/` so that installing into other projects copies only `.agent/` into the project root.

Acceptance Criteria:

- `.agent/ai-assistant.sh` is renamed to `.agent/start.sh` (same content: SSH agent bootstrap + exec `ai_assistant.py`); root `agent.sh` is removed; launch becomes `./.agent/start.sh`
- `.githooks/commit-msg` is relocated to `.agent/githooks/commit-msg`
- `scripts/install.sh` install mode copies only `.agent/`; `detect_mode()` keys on `.agent` alone; executability is recorded via `git update-index --chmod=+x` for `.agent/start.sh`
- Update mode: the staged-scope guard, preview list, and apply path all reduce to `.agent`; the refresh records a single reviewable, revertable commit scoped to `.agent` (REQ-6 behavior preserved, including the unborn-HEAD case)
- Entry scripts in this repo are committed with mode `100755` so the update path preserves executability
- Verification suites covering the entry chain, installer, and tracked layout are updated and green (e.g., `tests/test_s1_2_step5.py`, `tests/test_s2_1_step2.py`, `tests/test_s1_1_step2.py`)

Dependencies: None

Developer Notes:

- Maps to REQ-3, REQ-6; defines the target layout every later change depends on
- Load the bash conventions reference before implementation (routing table)
- The per-project args-file override stays as-is: custom override files remain in the project root (session decision)
- Consumers receive the new layout only after the next release cut (installer is served from the pinned tag)

## Story S6.2: Launcher & Hook Gate Rewiring

As a developer, I want the commit-msg gate and CI validation rewired to the relocated hook path so that gate activation keeps working after the consolidation.

Acceptance Criteria:

- `_ensure_commit_msg_gate()` in `.agent/ai_assistant.py` sets `core.hooksPath` to `.agent/githooks` (still only when unset; never overwrites pre-commit/husky values)
- Installer `configure_commit_gate()` sets the same `.agent/githooks` value
- The CI commit-subject validation step in `.github/workflows/ci.yml` invokes `.agent/githooks/commit-msg`
- Hook tests and the CI-range test are updated and green (e.g., `tests/test_commit_msg_hook.py`, `tests/test_ci_commit_subject_range.py`, `tests/test_commit_msg_gate_activation.py`)

Dependencies: S6.1

Developer Notes:

- Maps to REQ-2, REQ-9; the gate must remain active after relocation
- CI workflow edits require the CI/CD conventions reference (routing table)

## Story S6.5: Project Rename to dev-orchestrator

As a developer, I want the repository and launcher module renamed to match the project's evolution from a peer programming assistant into an integrated agentic AI harness for orchestrating development workflows, so that the project's naming reflects what it has become.

Acceptance Criteria:

- `DEFAULT_REPO_URL` in `scripts/install.sh` points at `https://github.com/daveonche/dev-orchestrator.git`; the canonical URL in the offline-test `insteadOf` rewrites (e.g., `tests/test_s2_1_step3.py`, `tests/test_s2_1_step4.py`) and every other pinned reference (e.g., `tests/test_release_ref_consistency.py`) is updated to match
- `.agent/ai_assistant.py` is renamed to `.agent/launcher.py`; the exec line in `.agent/start.sh` invokes `.agent/launcher.py`; no tracked code or test file references the old repository URL or the old module path (documentation references are updated in S6.3)
- Launcher-driving and tracked-layout suites are updated and green (e.g., `tests/test_s1_2_step5.py`, `tests/test_s1_3_step1.py`, `tests/test_s5_1_step7.py`)
- Release-reference consistency stays green; the commit subject scope `chore(agent)` and `DEFAULT_REF` (`v1.0.24`) are unchanged
- README and architecture-doc naming updates are deferred to S6.3's single documentation pass
- Consumers receive the new repository URL only after the next release cut (the installer is served from the pinned tag; GitHub redirects the old URL in the meantime)

Dependencies: S6.2

Developer Notes:

- New user-introduced requirement (naming alignment); no existing REQ covers the rename
- Tool-agnostic module name (`launcher.py`) decouples code from product naming so future renames do not touch code
- Product title becomes `Agentic AI Development-Workflow`; the README title change is executed in S6.3's documentation pass
- Load the bash conventions reference before implementation (routing table)

## Story S6.3: Documentation Alignment for Single-Directory Install

As a developer, I want the README and architecture documentation updated to the single-directory install so that the documented install method matches shipped behavior.

Acceptance Criteria:

- README H1 title reads `Agentic AI Development-Workflow` (replacing `AIAssistant`)
- README usage shows `./.agent/start.sh`; copy/install instructions copy only `.agent/`; the project-structure tree and commit-gate section reflect `.agent/githooks`
- `docs/architecture/architecture.md` Host Entry Layer describes `.agent/start.sh` → `.agent/launcher.py` (root `agent.sh` no longer referenced)
- README install/copy instructions reference the `dev-orchestrator` repository URL; the architecture doc references `.agent/launcher.py`
- Release-reference consistency stays green (`tests/test_release_ref_consistency.py`, `tests/test_s2_1_step5.py` updated where they pin paths)

Dependencies: S6.1, S6.2, S6.5

Developer Notes:

- Maps to REQ-3, REQ-14, REQ-15
- README edit requires the GFM conventions reference at implementation time (routing table)

## Story S6.4: Sprint 6 Record Documentation

As a developer, I want the Sprint 6 work recorded in the project docs, so that the sprint history and implementation status reflect the install-surface consolidation.

Acceptance Criteria:

- `docs/implementation_status.md` gains a Sprint 6 section listing the S6.1–S6.3 and S6.5 work as completed steps, and its Priority Order section is updated to reflect the new backlog state
- Documentation passes the markdown conventions

Dependencies: S6.1, S6.2, S6.3

Developer Notes:

- Follows the S4.4/S5.2 record-keeping pattern
- Documentation-only; load the GFM conventions reference before editing (routing table)

## Sprint Technical Rationale

These stories follow the minimal dependency chain of the approved Priority Order: S6.1 defines the target layout, S6.2 rewires the gate and CI to it, S6.3 aligns the docs with shipped behavior, and S6.4 records the sprint. Priority 3 (verification alignment) is distributed into each story's acceptance criteria per the project's green-suite discipline, so no standalone verification story is needed.
