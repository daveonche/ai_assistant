# Metadata: # Requirements Revision Prompt

## AI Assistant Compatibility

- Tested With:
  - Aider
  - GLM 5.3 Flash (August 27, 2026 release)
- Potential Compatible Assistants:
  - Other Claude models
  - GitHub Copilot (with modifications)
  - GPT-4

## SDLC Phase

- Phase: Requirements
- Sub-Phase: Requirements Revision
- Workflow: On-demand revision (standalone `$requirements-revised-project` command)

## Complexity Rating

- Complexity: Low
- Cognitive Load: Low
- Technical Depth: Requires dependency/impact checking and sequential
  renumbering of requirements

## Usage Guidelines

- Prerequisite: Existing requirements document in context
- Requires:
  - The requirements file to revise (e.g., `docs/requirements/core_requirements.md`)
  - User selections for each requirement (revise/remove/add)
- Modes: `/ask` for the interactive revision loop; `/code` only when saving
  the revised file

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes (each revision builds on the current list)
- Requires Contextual Awareness: Moderate
- Command Driven: Yes ($requirements-revised-project)
- Diagram Support: None

## Command Behavior

- `$requirements-revised-project`: Starts the revision workflow — review
  current requirements, collect revision selections, per-requirement
  revise/remove/add loop with validation, then renumber, regroup, and
  output the clean list.

## Gotchas / Sync Notes

- Adding a new requirement is chosen from the step 2 prompt and is not tied
  to a selected requirement; collect its details directly instead of
  presenting the revise/remove options.
- If validation fails, propose a reworded requirement and re-confirm with
  the user before applying it.
- After all revisions, renumber requirements sequentially and group by
  category before output.
- Keep the workflow steps and output template authoritative in SKILL.md.
  Do not duplicate them here.
- The sentinel line `<!-- sentinel: requirements/revised-project -->` must
  remain the final content line of SKILL.md; the orchestrator quotes it to
  detect truncated loads.

## Version

- Current Version: 1.0.0
- Last Updated: 2026-09-26
- Stability: Experimental

## Purpose

This metadata file describes the requirements revision skill. Workflow
steps and the output template are defined in SKILL.md.

## Sync / Validation Checklist

Before considering this metadata file current, verify:

- [ ] Command description matches SKILL.md
- [ ] Gotchas / Sync Notes reflect the current SKILL.md behavior
- [ ] Version and Last Updated are incremented after SKILL.md changes
- [ ] No workflow steps or output template details are duplicated here
