# Metadata: # Monitoring / Observability Prompt

## AI Assistant Compatibility

- Tested With:
  - Aider
- Potential Compatible Assistants:
  - Other Claude models
  - GitHub Copilot (with modifications)
  - GPT-4 (with workflow adaptation)

## SDLC Phase

- Phase: Operations & Observability
- Sub-Phase: Always-on monitoring stack (on demand)
- Workflow: SLIs/SLOs, instrumentation, dashboards, alerting, runbooks, on-call, chaos validation (activated via `$monitoring-observability`)

## Complexity Rating

- Complexity: High
- Cognitive Load: High
- Technical Depth: SLO/error-budget definition, three-pillar instrumentation, multi-burn-rate alerting, runbook authoring, chaos validation

## Usage Guidelines

- Prerequisite: at least one service running in staging or production
- Requires:
  - Services and their user-facing functionality
  - Performance expectations (or staging proxy baselines)
  - Monitoring platform details (or a selection decision)
  - On-call availability and escalation contacts
- Assumptions: dashboards/alerts live in the monitoring platform; runbooks and SLO definitions live in the repo; the developer verifies all outputs
- Modes: the prompt manages its own `/ask`/`/code` transitions

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes
- Requires Contextual Awareness: High
- Command Driven: Yes (`$monitoring-observability` plus `#observability-status`)
- Diagram Support: None
- Chained Workflow: No (on-demand skill, not a chain phase)

## Command Behavior

- `$monitoring-observability`: Starts or resumes the monitoring/observability workflow — context verification, SLIs/SLOs, instrumentation, dashboards, alert strategy, runbooks, on-call, chaos validation, artifact save.
- `#observability-status`: Reports progress only. It NEVER advances the workflow, skips steps, or changes state.

## Gotchas / Sync Notes

- On-demand skill, not a chain phase: referenced from both chains' Quality Gates tables; always-on cadence, not release-bound.
- Covers the monitoring/observability TODO item in both chains; release-specific rollback triggers stay in `$deployment-release` STEP 5; incident response remains a TODO item with this skill's STEP 7 as its foundation.
- The sentinel line `<!-- sentinel: monitoring/observability -->` must remain the final content line of SKILL.md; the orchestrator quotes it to detect truncated loads.

## Version

- Current Version: 1.0.0
- Last Updated: 2026-10-04
- Stability: Experimental

## Purpose

This metadata file describes the monitoring/observability prompt. The workflow steps, core rules, and validation checklist are defined in SKILL.md.

## Sync / Validation Checklist

Before considering this metadata file current, verify:

- [ ] Command Behavior matches the commands in SKILL.md
- [ ] Gotchas / Sync Notes reflect the current SKILL.md gotchas
- [ ] Version and Last Updated are incremented after SKILL.md changes
- [ ] No workflow details, core rules, or validation points are duplicated here
