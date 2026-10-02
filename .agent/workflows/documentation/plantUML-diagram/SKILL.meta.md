# Metadata: # PlantUML Diagram Generator Prompt

## AI Assistant Compatibility

- Tested With:
  - Aider
  - GLM 5.3 Flash (August 27, 2026 release)
- Potential Compatible Assistants:
  - Other Claude models
  - GitHub Copilot (with modifications)
  - GPT-4

## SDLC Phase

- Phase: Documentation
- Sub-Phase: Diagram Generation
- Workflow: On-demand diagram generation (standalone `$documentation-plantUML-diagram` command)

## Complexity Rating

- Complexity: Medium
- Cognitive Load: Medium
- Technical Depth: Requires codebase analysis for component discovery and
  PlantUML syntax validation

## Usage Guidelines

- Prerequisite: Run in `/ask` mode; no code changes required
- Requires:
  - Relevant project source files in context (user-provided on request)
  - User answers for diagram type, scope, entry point, and relationship depth
  - A PlantUML renderer or validator for syntax validation

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes (each step builds on prior answers)
- Requires Contextual Awareness: Medium
- Command Driven: Yes ($documentation-plantUML-diagram)
- Diagram Support: PlantUML (not Mermaid)

## Command Behavior

- `$documentation-plantUML-diagram`: Starts the staged diagram workflow —
  mode check, diagram type, scope, entry point, relationship depth,
  component selection, generation with validation, review/refine loop,
  then optional save.

## Gotchas / Sync Notes

- PlantUML themes may not be available in all renderers; verify theme
  support in the user's environment.
- Rendering varies between PlantUML versions; confirm the user's version
  if issues are reported.
- Special characters in component, class, or actor names may need quoting
  or escaping.
- Keep the step-by-step workflow, templates, and gotcha details
  authoritative in SKILL.md. Do not duplicate them here.
- The sentinel line `<!-- sentinel: documentation/plantUML-diagram -->`
  must remain the final content line of SKILL.md; the orchestrator quotes
  it to detect truncated loads.

## Version

- Current Version: 1.0.0
- Last Updated: 2026-09-26
- Stability: Experimental

## Purpose

This metadata file describes the PlantUML diagram generator skill.
Workflow steps, templates, and gotchas are defined in SKILL.md.

## Sync / Validation Checklist

Before considering this metadata file current, verify:

- [ ] Command description matches SKILL.md
- [ ] Gotchas / Sync Notes reflect the current SKILL.md gotchas
- [ ] Version and Last Updated are incremented after SKILL.md changes
- [ ] No workflow steps, templates, or gotcha details are duplicated here
