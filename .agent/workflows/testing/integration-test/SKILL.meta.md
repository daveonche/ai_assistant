# Metadata: # Integration Testing Prompt

## AI Assistant Compatibility

- Tested With:
  - Aider
- Potential Compatible Assistants:
  - Other Claude models
  - GitHub Copilot (with modifications)
  - GPT-4 (with workflow adaptation)

## SDLC Phase

- Phase: Testing & Verification
- Sub-Phase: Per-story integration validation (quality gate, on demand)
- Workflow: Integration testing of a story's composed steps (activated via `$testing-integration-test S<X.Y>`)

## Complexity Rating

- Complexity: High
- Cognitive Load: Medium-High
- Technical Depth: Seam mapping, mocking-boundary discipline, contract and error-path validation

## Usage Guidelines

- Prerequisite: the story's steps implemented and unit-tested (Phase 4A/4B or 7A/7B iteration loop complete for that story)
- Requires:
  - Story steps report and sprint story (acceptance criteria)
  - Implementation files for all of the story's steps
  - Dependency definition file and test runner config
- Assumptions: a dedicated test database or equivalent real collaborators are available; the developer verifies all outputs
- Modes: the prompt manages its own `/ask`/`/code` transitions

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes
- Requires Contextual Awareness: High
- Command Driven: Yes (`$testing-integration-test S<X.Y>` plus `#integration-test-status`)
- Diagram Support: None
- Chained Workflow: No (on-demand quality gate, not a chain phase)

## Command Behavior

- `$testing-integration-test S<X.Y>`: Starts or resumes the integration testing workflow for the story — context verification, seam mapping, test plan, implementation, report save, handoff.
- `#integration-test-status`: Reports progress only. It NEVER advances the workflow, skips steps, or changes state.

## Gotchas / Sync Notes

- Quality gate, not a chain phase: invoked per story, after that story's implementation/unit-test loop; referenced from both chains' Quality Gates tables.
- Scope is integration only: unit testing is `$testing-unit-test`; E2E journeys are `$testing-e2e-test` (sprint close).
- The sentinel line `<!-- sentinel: testing/integration-test -->` must remain the final content line of SKILL.md; the orchestrator quotes it to detect truncated loads.

## Version

- Current Version: 1.0.0
- Last Updated: 2026-10-04
- Stability: Experimental

## Purpose

This metadata file describes the integration testing prompt. The workflow steps, core rules, and validation checklist are defined in SKILL.md.

## Sync / Validation Checklist

Before considering this metadata file current, verify:

- [ ] Command Behavior matches the commands in SKILL.md
- [ ] Gotchas / Sync Notes reflect the current SKILL.md gotchas
- [ ] Version and Last Updated are incremented after SKILL.md changes
- [ ] No workflow details, core rules, or validation points are duplicated here
