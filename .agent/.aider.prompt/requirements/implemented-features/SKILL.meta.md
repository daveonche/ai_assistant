# Metadata: # Implementation Status Analysis Prompt

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
- Sub-Phase: Implementation Status Analysis
- Workflow: On-demand analysis (standalone `$requirements-implemented-features` command)

## Complexity Rating

- Complexity: Medium
- Cognitive Load: Moderate
- Technical Depth: Requires cross-checking requirements and user stories
  against actual source files with evidence citations

## Usage Guidelines

- Prerequisite: Requirements, user stories, and tech stack in context
- Requires:
  - Project requirements (`docs/requirements/core_requirements.md` when
    present; otherwise `docs/requirements.md` — at least one of the two)
  - User stories (`docs/user_stories.md`)
  - Core technology stack (`docs/tech_stack.md`)
  - Source code directories (e.g., `src/`, `tests/`) as evidence
- Modes: Analysis in `/ask`; saving requires a controlled transition to
  code mode via `/code proceed` (SKILL.md Step 4)
- Default output: `docs/implementation_status.md` (overwrite or timestamped
  copy on request)

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes (progress tracked in the active conversation)
- Requires Contextual Awareness: High
- Command Driven: Yes ($requirements-implemented-features, $requirements-implemented-features-status)
- Diagram Support: None

## Command Behavior

- `$requirements-implemented-features`: Starts or resumes implementation
  analysis — mode check, context verification, codebase analysis with
  evidence citations, validation loop, then optional save via `/code`.
- `$requirements-implemented-features-status`: Shows current progress in
  the active conversation only and does NOT activate the full workflow. To
  resume after viewing status, use `$requirements-implemented-features`.

## Gotchas / Sync Notes

- Strictly read-only: never modify code, make implementation suggestions,
  propose code changes, create components, refactor, generate snippets, or
  provide coding guidance.
- Do not invent or reuse technology stack values that are not present in
  the loaded `docs/tech_stack.md`.
- The `REQ-3` requirement-ID format in the report templates is illustrative
  only; use the actual requirement IDs exactly as they appear in the loaded
  requirements files, and invent no format if none is defined.
- Keep the report structure, validation steps, and workflow steps
  authoritative in SKILL.md. Do not duplicate them here.
- The sentinel line `<!-- sentinel: requirements/implemented-features -->`
  must remain the final content line of SKILL.md; the orchestrator quotes
  it to detect truncated loads.

## Version

- Current Version: 1.0.0
- Last Updated: 2026-09-26
- Stability: Experimental

## Purpose

This metadata file describes the implementation status analysis skill.
Report structure, validation steps, and workflow steps are defined in
SKILL.md.

## Sync / Validation Checklist

Before considering this metadata file current, verify:

- [ ] `$requirements-implemented-features-status` description matches SKILL.md
- [ ] Gotchas / Sync Notes reflect the current SKILL.md gotchas
- [ ] Version and Last Updated are incremented after SKILL.md changes
- [ ] No report structure, validation steps, or workflow steps are duplicated here
