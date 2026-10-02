# Metadata: # Project Scaffolding Story Generator

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
- Sub-Phase: Scaffolding Story Generation
- Workflow: Project Scaffolding Sprint Workflow Chain (sprint 0 story generation; activated via `$requirements-scaffolding-user-stories`)

## Complexity Rating

- Complexity: Medium
- Cognitive Load: Moderate
- Technical Depth: Requires translating architecture and tech stack into a
  minimal structural story set with pinned dependency versions

## Usage Guidelines

- Prerequisite: Requirements, architecture, tech stack, and component
  structure defined (graceful degradation with a user warning if some are
  missing)
- Requires:
  - Project requirements (e.g., `docs/requirements/core_requirements.md`)
  - Architecture decisions (e.g., `docs/architecture/architecture.md`)
  - Technology stack (e.g., `docs/tech_stack.md`)
  - Component structure (component section of the architecture doc)
  - Worked example: `docs/sprints/sprint_1_stories.md` (format reference)
- Modes: `/ask` for generation and review; `/code` only when saving
- Default output: `docs/sprints/sprint_0_stories.md` (or user-specified path)

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes (stories derive from the loaded architecture and stack)
- Requires Contextual Awareness: Medium
- Command Driven: Yes ($requirements-scaffolding-user-stories)
- Diagram Support: None

## Command Behavior

- `$requirements-scaffolding-user-stories`: Starts the scaffolding story
  workflow — context review with user confirmation, understanding summary
  with insufficiency warning, generation of 2-3 structural stories from the
  template, validation loop, then save via `/code`.

## Gotchas / Sync Notes

- Never include data persistence, security, or business logic in
  scaffolding stories, even if the tech stack lists a database or an auth
  provider; those belong to later stories.
- Pin exact dependency versions in acceptance criteria and technical notes
  (e.g., `flask==3.0.3`), not version ranges.
- Keep stories strictly structural: a story that requires data migration
  or production secrets is out of scope.
- Keep the story template, validation loop, and workflow steps
  authoritative in SKILL.md. Do not duplicate them here.
- The sentinel line
  `<!-- sentinel: requirements/scaffolding-user-stories -->` must remain
  the final content line of SKILL.md; the orchestrator quotes it to detect
  truncated loads.

## Version

- Current Version: 1.0.0
- Last Updated: 2026-09-26
- Stability: Experimental

## Purpose

This metadata file describes the project scaffolding story generator
skill. Workflow steps, story template, and validation loop are defined in
SKILL.md.

## Sync / Validation Checklist

Before considering this metadata file current, verify:

- [ ] Command description matches SKILL.md
- [ ] Gotchas / Sync Notes reflect the current SKILL.md gotchas
- [ ] Version and Last Updated are incremented after SKILL.md changes
- [ ] No workflow steps, story template, or validation details are duplicated here
