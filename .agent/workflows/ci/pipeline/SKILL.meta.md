# Metadata: # CI/CD Pipeline Prompt

## AI Assistant Compatibility

- Tested With:
  - Aider
- Potential Compatible Assistants:
  - Other Claude models
  - GitHub Copilot (with modifications)
  - GPT-4 (with workflow adaptation)

## SDLC Phase

- Phase: CI/CD & Automation
- Sub-Phase: Continuous pipeline design, review, and hardening (on demand)
- Workflow: GitHub Actions pipeline audit or from-scratch design, implementation, and validation (activated via `$ci-pipeline`)

## Complexity Rating

- Complexity: Medium
- Cognitive Load: Medium
- Technical Depth: SHA pinning verification, least-privilege permissions, tiered test architecture, caching and artifact strategy, workflow validation

## Usage Guidelines

- Prerequisite: none chain-specific — invoked when designing or changing CI/CD workflows
- Requires:
  - CI/CD workflow files (`.github/workflows/`), when any exist
  - The conventions reference `.agent/specs/references/ci-cd-best-practices.md` (required ruleset)
  - Test suite entry points and branching strategy
- Assumptions: GitHub Actions is the CI platform (per repository conventions); the developer verifies all outputs
- Modes: the prompt manages its own `/ask`/`/code` transitions

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes
- Requires Contextual Awareness: Medium
- Command Driven: Yes (`$ci-pipeline` plus `#ci-pipeline-status`)
- Diagram Support: None
- Chained Workflow: No (on-demand skill, not a chain phase)

## Command Behavior

- `$ci-pipeline`: Starts or resumes the CI/CD pipeline workflow — context verification, audit or architecture design, plan, implementation, validation, summary and handoff.
- `#ci-pipeline-status`: Reports progress only. It NEVER advances the workflow, skips steps, or changes state.

## Gotchas / Sync Notes

- On-demand skill, not a chain phase: referenced from both chains' Quality Gates tables; runs per PR/merge, not release-bound.
- Covers the CI/CD TODO item in both chains; monitoring/observability is `$monitoring-observability`; incident response remains a TODO item.
- Deployment-stage hardening stays in `$deployment-release` STEP 2; containerization is delegated to the Docker conventions references.
- The sentinel line `<!-- sentinel: ci/pipeline -->` must remain the final content line of SKILL.md; the orchestrator quotes it to detect truncated loads.

## Version

- Current Version: 1.0.0
- Last Updated: 2026-10-04
- Stability: Experimental

## Purpose

This metadata file describes the CI/CD pipeline prompt. The workflow steps, core rules, and validation checklist are defined in SKILL.md.

## Sync / Validation Checklist

Before considering this metadata file current, verify:

- [ ] Command Behavior matches the commands in SKILL.md
- [ ] Gotchas / Sync Notes reflect the current SKILL.md gotchas
- [ ] Version and Last Updated are incremented after SKILL.md changes
- [ ] No workflow details, core rules, or validation points are duplicated here
