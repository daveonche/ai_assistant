# Metadata: # Initial Project Requirements Management Prompt

## AI Assistant Compatibility

- Tested With:
  - Aider
  - GLM 5.3 Flash (August 27, 2026 release)
- Potential Compatible Assistants:
  - Other modern LLMs (the interactive workflow may require minor prompt adaptations)

## SDLC Phase

- Phase: Requirements
- Sub-Phase: Initial Requirements Definition
- Workflow: Project Scaffolding Sprint Workflow Chain (requirements stage; activated via `$requirements-initial-project`)

## Complexity Rating

- Complexity: Medium
- Cognitive Load: Moderate
- Technical Depth: Requires understanding of requirements engineering
  principles (atomicity, ID uniqueness, assumption marking)

## Usage Guidelines

- Prerequisite: project idea or problem statement (minimal or ambiguous
  ideas are fine; the workflow asks clarifying questions)
- Helpful inputs:
  - Clear project vision
  - Basic project context
  - Understanding of target users
  - Desired feature set outline
- Modes: interactive, step-by-step execution in `/ask`; switch to `/code`
  only for the 'save to file' step, then return to `/ask`
- Default output: `docs/requirements/core_requirements.md` (custom path on
  request)

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes (checklist-based status tracking across both workflows)
- Requires Contextual Awareness: Moderate
- Command Driven: Yes ($requirements-initial-project activation; #generate-requirements, #modify-requirements, #requirements-status)
- Diagram Support: None

## Command Behavior

- `$requirements-initial-project`: Orchestrator activation command for the skill.
- `#generate-requirements`: Starts new requirements generation — mode check, project idea verification and assessment, generation with the [VALIDATE] loop, review/revision loop, then save via `/code`.
- `#modify-requirements`: Modifies existing requirements (add/modify/delete) with validation before saving.
- `#requirements-status`: Reports progress from the tracked checklist; does not activate the full workflow.

## Gotchas / Sync Notes

- This skill uses `#`-prefixed commands, which intentionally differ from the orchestrator's `$<category>-<promptname>` shorthand; do not rename them without coordinating changes across the other workflow files.
- Saving requires a mode sequence: stay in `/ask` for every review step, switch to `/code` only for the 'save to file' step, then return to `/ask`. Never emit SEARCH/REPLACE blocks during review steps.
- REQ-IDs must remain unique across both the generate and modify flows; reuse the `[CAT]` abbreviation scheme when adding categories.
- The `[Assumed]` prefix is permitted only when the user explicitly chose option 2 in STEP 2 of the generate workflow; never add it retroactively.
- Keep the workflow steps, requirement formats, and validation rules authoritative in SKILL.md. Do not duplicate them here.
- The sentinel line `<!-- sentinel: requirements/initial-project -->` must remain the final content line of SKILL.md; the orchestrator quotes it to detect truncated loads.

## Version

- Current Version: 1.2.1
- Last Updated: 2026-09-26
- Stability: Beta

## Purpose

This metadata file describes the initial project requirements management
skill. Workflow steps, requirement formats, and validation rules are
defined in SKILL.md.

## Sync / Validation Checklist

Before considering this metadata file current, verify:

- [ ] `#requirements-status` description matches SKILL.md
- [ ] Gotchas / Sync Notes reflect the current SKILL.md gotchas
- [ ] Version and Last Updated are incremented after SKILL.md changes
- [ ] No workflow steps, requirement formats, or validation rules are duplicated here
