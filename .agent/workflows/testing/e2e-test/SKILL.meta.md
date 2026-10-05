# Metadata: # E2E Testing Prompt

## AI Assistant Compatibility

- Tested With:
  - Aider
- Potential Compatible Assistants:
  - Other Claude models
  - GitHub Copilot (with modifications)
  - GPT-4 (with workflow adaptation)

## SDLC Phase

- Phase: Testing & Verification
- Sub-Phase: Sprint-close end-to-end validation (quality gate, on demand)
- Workflow: E2E testing of the sprint's critical user journeys (activated via `$testing-e2e-test`)

## Complexity Rating

- Complexity: High
- Cognitive Load: Medium-High
- Technical Depth: Journey scoping from acceptance criteria, tool-idiom test authoring, flake elimination

## Usage Guidelines

- Prerequisite: the sprint's stories implemented and unit-tested (Phase 4A/4B or 7A/7B iteration loop complete)
- Requires:
  - Sprint stories and story steps reports (acceptance criteria)
  - Dependency definition file and E2E tooling (or a decision to add/defer)
- Assumptions: the application can run locally against real collaborators; the developer verifies all outputs
- Modes: the prompt manages its own `/ask`/`/code` transitions

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes
- Requires Contextual Awareness: High
- Command Driven: Yes (`$testing-e2e-test` plus `#e2e-test-status`)
- Diagram Support: None
- Chained Workflow: No (on-demand quality gate, not a chain phase)

## Command Behavior

- `$testing-e2e-test`: Starts or resumes the E2E testing workflow — context verification, journey scoping, test plan, implementation, report save, sprint-close handoff.
- `#e2e-test-status`: Reports progress only. It NEVER advances the workflow, skips steps, or changes state.

## Gotchas / Sync Notes

- Quality gate, not a chain phase: invoked at sprint close alongside `$code-security-audit`; referenced from both chains' Quality Gates tables.
- Scope is E2E only: unit testing is `$testing-unit-test`; integration testing remains an SDLC Gaps TODO item in both chains.
- The sentinel line `<!-- sentinel: testing/e2e-test -->` must remain the final content line of SKILL.md; the orchestrator quotes it to detect truncated loads.

## Version

- Current Version: 1.0.0
- Last Updated: 2026-10-04
- Stability: Experimental

## Purpose

This metadata file describes the E2E testing prompt. The workflow steps, core rules, and validation checklist are defined in SKILL.md.

## Sync / Validation Checklist

Before considering this metadata file current, verify:

- [ ] Command Behavior matches the commands in SKILL.md
- [ ] Gotchas / Sync Notes reflect the current SKILL.md gotchas
- [ ] Version and Last Updated are incremented after SKILL.md changes
- [ ] No workflow details, core rules, or validation points are duplicated here
