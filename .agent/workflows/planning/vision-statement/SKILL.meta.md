# Metadata: # Vision Statement Generation Prompt

## AI Assistant Compatibility

- Tested With:
  - Aider
  - GLM 5.3 Flash (August 27, 2026 release)
- Potential Compatible Assistants:
  - Claude models
  - Other GPT-4o models
  - GitHub Copilot (with modifications: requires explicit mode management equivalent to `/ask` and `/code`)

## SDLC Phase

- Phase: Planning
- Sub-Phase: Vision Definition
- Workflow: Initial Project Vision (part of `$workflows-project-scaffolding-chain`; also usable standalone)

## Complexity Rating

- Complexity: Medium
- Cognitive Load: Moderate
- Technical Depth: Focuses on business/user value over technical details

## Usage Guidelines

- Prerequisite: Project concept or idea
- Required User Inputs:
  - Problem statement / purpose
  - Target audience
  - Value proposition
  - Key feature concepts
  - Future growth vision
  - Project requirements document (optional; grounds generation when available)
- Modes: `/ask` for generation/modification; `/code` for saving
- File Dependency: existing vision file (`docs/vision/project_vision.md`) must be loaded for `#modify-vision`
- Default Output: `docs/vision/project_vision.md` (custom path on request)

## Workflow Chain

- Parent workflow: `$workflows-project-scaffolding-chain`
- Related skills: `requirements/initial-project`, `architecture/design`, `planning/story-analysis`

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes (conversation-scoped only; no persistence)
- Requires Contextual Awareness: Moderate
- Command Driven: Yes ($planning-vision-statement activation; #generate-vision, #modify-vision, #vision-status)
- Diagram Support: None
- Example Based: Provides clear examples for each section
- Interactive Guidance: Multi-option input approach

## Command Behavior

- `$planning-vision-statement`: Orchestrator activation command for the skill.
- `#generate-vision`: Starts new vision statement generation — mode check, requirements grounding, staged Q&A with examples, draft approval loop, then save via `/code`.
- `#modify-vision`: Modifies an existing saved vision statement, section by section; requires the vision file loaded in chat first.
- `#vision-status`: Shows current progress in the vision workflow (current conversation only). To resume generation, use `#generate-vision`; to modify, use `#modify-vision`.

## Gotchas / Sync Notes

- Progress is tracked in the current conversation only; it is not persisted automatically unless a separate state file is maintained.
- `#modify-vision` requires the current vision statement file to be loaded in the chat before modifying it.
- Saving requires switching from `/ask` to `/code`; the file is not saved while still in ask mode.
- Vision generation must be grounded in the project's actual requirements; do not generate from generic assumptions if requirements are unavailable.
- When saving, output the full markdown content at save time to avoid context loss across the mode switch.
- Keep the workflow steps, section templates, and examples authoritative in SKILL.md. Do not duplicate them here.
- The sentinel line `<!-- sentinel: planning/vision-statement -->` must remain the final content line of SKILL.md; the orchestrator quotes it to detect truncated loads.

## Version

- Current Version: 1.2.1
- Last Updated: 2026-09-26
- Stability: Beta

## Purpose

This metadata file describes the vision statement generation skill. Workflow steps, section templates, and examples are defined in SKILL.md.

## Sync / Validation Checklist

Before considering this metadata file current, verify:

- [ ] `#vision-status` description matches SKILL.md
- [ ] Gotchas / Sync Notes reflect the current SKILL.md gotchas
- [ ] Version and Last Updated are incremented after SKILL.md changes
- [ ] No workflow steps, section templates, or examples are duplicated here
