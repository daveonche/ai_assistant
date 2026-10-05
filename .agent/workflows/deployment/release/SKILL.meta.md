# Metadata: # Deployment / Release Prompt

## AI Assistant Compatibility

- Tested With:
  - Aider
- Potential Compatible Assistants:
  - Other Claude models
  - GitHub Copilot (with modifications)
  - GPT-4 (with workflow adaptation)

## SDLC Phase

- Phase: Deployment & Operations
- Sub-Phase: Production release (on-demand gate)
- Workflow: Safe production deployment with rollback capability (activated via `$deployment-release`)

## Complexity Rating

- Complexity: High
- Cognitive Load: High
- Technical Depth: Pipeline sequencing, strategy selection, backward-compatible migration planning, quantitative rollback triggers, performance gating

## Usage Guidelines

- Prerequisite: the release scope is implemented and verified (sprint-close gates passed: `$testing-e2e-test`, `$code-security-audit`)
- Requires:
  - Release scope (sprint stories, release notes, or changelog)
  - CI/CD pipeline and deployment/infrastructure configuration
  - Migration files when the release includes schema changes
  - Staging environment and monitoring platform (or an explicit plan for their absence)
- Assumptions: the user (or CI) executes deployment stages; the prompt plans, gates, and verifies
- Modes: the prompt manages its own `/ask`/`/code` transitions

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes
- Requires Contextual Awareness: High
- Command Driven: Yes (`$deployment-release` plus `#release-status`)
- Diagram Support: None
- Chained Workflow: No (on-demand gate, not a chain phase)

## Command Behavior

- `$deployment-release`: Starts or resumes the deployment/release workflow — pipeline verification, strategy selection, migration plan, rollback triggers, performance gate, runbook save, execution and confirmation.
- `#release-status`: Reports progress only. It NEVER advances the workflow, skips steps, or changes state.

## Gotchas / Sync Notes

- On-demand gate, not a chain phase: invoked when a release is ready, after the sprint-close gates; referenced from both chains' Quality Gates tables.
- Covers the deployment TODO item in both chains; CI/CD pipeline design is `$ci-pipeline` (this skill verifies the production sequence in STEP 2 only) and always-on monitoring is `$monitoring-observability` (this skill defines release-specific triggers and logging in STEP 5 only).
- The sentinel line `<!-- sentinel: deployment/release -->` must remain the final content line of SKILL.md; the orchestrator quotes it to detect truncated loads.

## Version

- Current Version: 1.0.0
- Last Updated: 2026-10-04
- Stability: Experimental

## Purpose

This metadata file describes the deployment/release prompt. The workflow steps, core rules, and validation checklist are defined in SKILL.md.

## Sync / Validation Checklist

Before considering this metadata file current, verify:

- [ ] Command Behavior matches the commands in SKILL.md
- [ ] Gotchas / Sync Notes reflect the current SKILL.md gotchas
- [ ] Version and Last Updated are incremented after SKILL.md changes
- [ ] No workflow details, core rules, or validation points are duplicated here
