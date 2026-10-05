# Metadata: # Incident Response Prompt

## AI Assistant Compatibility

- Tested With:
  - Aider
- Potential Compatible Assistants:
  - Other Claude models
  - GitHub Copilot (with modifications)
  - GPT-4 (with workflow adaptation)

## SDLC Phase

- Phase: Operations & Observability
- Sub-Phase: Incident Response
- Workflow: Incident command and postmortem facilitation (activated via `$incident-response`)

## Complexity Rating

- Complexity: High
- Cognitive Load: High
- Technical Depth: Severity triage under pressure, incident communication cadence, mitigation coordination with human-approved changes, timeline discipline, blameless postmortem facilitation

## Usage Guidelines

- Prerequisite: an active or recent incident — a firing alert, user report, or production anomaly with impact evidence
- Requires:
  - Incident description and impact evidence (alerts, dashboards, error rates, user reports)
  - On-call availability and escalation contacts (from `docs/operations/on-call.md` when present)
  - Runbooks for affected services (from `docs/operations/runbooks/` when present)
- Assumptions: dashboards and alerting live in the monitoring platform; incident artifacts live in the repo; the developer verifies all outputs and approves every change
- Modes: the prompt manages its own `/ask`/`/code` transitions

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes
- Requires Contextual Awareness: High
- Command Driven: Yes (`$incident-response` plus `#incident-update` and `#incident-response-status`)
- Diagram Support: None
- Chained Workflow: No (on-demand skill, not a chain phase)

## Command Behavior

- `$incident-response`: Starts or resumes the incident response workflow — intake and context verification, severity and roles, first status update and cadence, mitigation and resolution confirmation, blameless postmortem, artifact save.
- `#incident-update`: Renders and records a status update from the current incident state. It NEVER advances the workflow, skips steps, or changes state.
- `#incident-response-status`: Reports progress only. It NEVER advances the workflow, skips steps, or changes state.

## Gotchas / Sync Notes

- On-demand skill, not a chain phase: referenced from both chains' Quality Gates tables; runs when an incident is active or a postmortem is due.
- Closes the Incident response TODO item in both chains' SDLC Gaps sections; on-call rotation and the incident workflow from `$monitoring-observability` STEP 7 are its foundations.
- Release-specific rollback triggers stay in `$deployment-release` STEP 5; this skill consumes them during mitigation but does not redefine them.
- Postmortem action items feed the next sprint via `$planning-sprint-story` in the post-scaffolding chain.
- The sentinel line `<!-- sentinel: incident/response -->` must remain the final content line of SKILL.md; the orchestrator quotes it to detect truncated loads.

## Version

- Current Version: 1.0.0
- Last Updated: 2026-10-05
- Stability: Experimental

## Purpose

This metadata file describes the incident response prompt. The workflow steps, core rules, and validation checklist are defined in SKILL.md.

## Sync / Validation Checklist

Before considering this metadata file current, verify:

- [ ] Command Behavior matches the commands in SKILL.md
- [ ] Gotchas / Sync Notes reflect the current SKILL.md gotchas
- [ ] Version and Last Updated are incremented after SKILL.md changes
- [ ] No workflow details, core rules, or validation points are duplicated here
