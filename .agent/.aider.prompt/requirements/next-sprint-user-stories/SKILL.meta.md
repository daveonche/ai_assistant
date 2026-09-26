# Metadata: # Post-scaffolding Sprint Story Generation Prompt

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
- Sub-Phase: Sprint Story Generation
- Workflow: Post-Scaffolding Sprint Workflow Chain (story generation stage; activated via `#generate-sprint-stories`)

## Complexity Rating

- Complexity: Medium
- Cognitive Load: Moderate
- Technical Depth: Requires dependency mapping and technology-to-feature
  alignment for the upcoming sprint

## Usage Guidelines

- Prerequisite: Requirements list, previous sprint stories, implementation
  status report, and technology stack in context
- Requires:
  - Project requirements list (e.g., `docs/requirements.md`)
  - Previous sprint stories (e.g., `docs/sprints/sprint_X_stories.md`) —
    MUST be provided; never assume Sprint 1
  - Implementation status report with prioritized features
    (e.g., `docs/implementation_status.md`)
  - Technology stack from dependency files (`package.json`,
    `requirements.txt`, `Gemfile`, etc.) or configuration files
- Modes: `/ask` for generation and review; `/code` only if saving the
  story file (default `docs/sprints/sprint_[number]_stories.md`)

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes (sprint number and prior stories shape generation)
- Requires Contextual Awareness: High
- Command Driven: Yes (#generate-sprint-stories, #generate-sprint-stories-status)
- Diagram Support: None

## Command Behavior

- `#generate-sprint-stories`: Starts or resumes sprint story generation —
  context verification, sprint number collection, technical dependency
  analysis, story generation with review loop, then optional save.
- `#generate-sprint-stories-status`: Shows current progress only and does
  NOT activate the full workflow. To resume after viewing status, use
  `#generate-sprint-stories`.

## Gotchas / Sync Notes

- Testing is never an acceptance criterion; it is part of the standard
  Definition of Done.
- Never assume Sprint 1 or default sprint numbers; the user must provide
  the sprint number.
- Do not combine multiple features into single stories; minimize
  dependency chains (max one level when possible).
- The role MUST terminate after the save decision — no additional stories,
  implementation details, analysis, or options.
- Keep the workflow steps, story format, and pitfall list authoritative in
  SKILL.md. Do not duplicate them here.
- The sentinel line
  `<!-- sentinel: requirements/next-sprint-user-stories -->` must remain
  the final content line of SKILL.md; the orchestrator quotes it to detect
  truncated loads.

## Version

- Current Version: 1.0.0
- Last Updated: 2026-09-26
- Stability: Experimental

## Purpose

This metadata file describes the sprint story generation skill. Workflow
steps, story format, and pitfalls are defined in SKILL.md.

## Sync / Validation Checklist

Before considering this metadata file current, verify:

- [ ] `#generate-sprint-stories-status` description matches SKILL.md
- [ ] Gotchas / Sync Notes reflect the current SKILL.md gotchas
- [ ] Version and Last Updated are incremented after SKILL.md changes
- [ ] No workflow steps, story format, or pitfall details are duplicated here
