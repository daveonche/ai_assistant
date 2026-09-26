# Metadata: # Project README Generator Prompt

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
- Sub-Phase: Project README
- Workflow: On-demand README generation/update (standalone `$documentation-project-README` command)

## Complexity Rating

- Complexity: Medium
- Cognitive Load: Medium
- Technical Depth: Requires cross-checking generated content against
  package/config files and code structure

## Usage Guidelines

- Prerequisite: Relevant project files in context (package/config files,
  existing `README.md`, docs)
- Requires:
  - Package/config files for commands and technologies
  - Existing `README.md` if present (manual content must be preserved)
  - `docs/requirements.md`, `docs/tech_stack.md`,
    `docs/architecture/architecture.md`, `docs/user_stories.md` when present
  - `/code` mode only if saving the README directly

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes (update mode depends on existing README content)
- Requires Contextual Awareness: High
- Command Driven: Yes ($documentation-project-README)
- Diagram Support: None

## Command Behavior

- `$documentation-project-README`: Starts the README workflow — context
  setup, analysis, generation, validation loop, then output as a saved
  file (requires `/code` mode) or a copyable markdown block.

## Gotchas / Sync Notes

- Preserve manually maintained README content (badges, team documentation,
  custom sections) when updating an existing README.
- `/read-only` and `/drop` commands must use the full path including
  `.agent/`.
- Use actual commands from package/config files, never placeholders.
- Keep the README structure template and workflow steps authoritative in
  SKILL.md. Do not duplicate them here.
- The sentinel line `<!-- sentinel: documentation/project-README -->` must
  remain the final content line of SKILL.md; the orchestrator quotes it to
  detect truncated loads.

## Version

- Current Version: 1.0.0
- Last Updated: 2026-09-26
- Stability: Experimental

## Purpose

This metadata file describes the project README generator skill. Workflow
steps, README structure, and gotchas are defined in SKILL.md.

## Sync / Validation Checklist

Before considering this metadata file current, verify:

- [ ] Command description matches SKILL.md
- [ ] Gotchas / Sync Notes reflect the current SKILL.md gotchas
- [ ] Version and Last Updated are incremented after SKILL.md changes
- [ ] No workflow steps, README structure, or gotcha details are duplicated here
