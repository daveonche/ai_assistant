# Metadata: # Story Analysis Prompt

## AI Assistant Compatibility

- Tested With:
  - Aider
  - GLM 5.3 Flash (August 27, 2026 release)
- Potential Compatible Assistants:
  - Other GLM models
  - GitHub Copilot (with modifications)

## SDLC Phase

- Phase: Planning
- Sub-Phase: Story Decomposition
- Workflow: Post-Scaffolding Sprint Workflow Chain (story analysis stage; activated via `#analyze-story S<X.Y>`)

## Complexity Rating

- Complexity: Medium
- Cognitive Load: Moderate
- Technical Depth: Requires atomic, technology-neutral decomposition of
  user stories into sequentially implementable steps

## Usage Guidelines

- Prerequisite: Sprint story S<X.Y> in context
- Requires:
  - User story details
  - Project requirements
  - Project context (may include a technology stack; it must NOT influence step wording)
- Progressive Disclosure: Core workflow in SKILL.md; implementation-steps
  template in `references/story-template.md`, loaded on demand in Step 4

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes (stage tracking via #analysis-status)
- Requires Contextual Awareness: High
- Command Driven: Yes (#analyze-story, #analysis-status, #implement-step)
- Diagram Support: None

## Command Behavior

- `#analyze-story S<X.Y>`: Starts or resumes story analysis — mode check,
  story verification, criteria mapping, step generation with the Step 4a
  validation loop, review, then save via `/code`.
- `#analysis-status`: Shows current workflow-stage progress only and does
  NOT activate the full workflow. To resume after viewing status, use
  `#analyze-story S<X.Y>`.

## Gotchas / Sync Notes

- Commands use a `#` prefix (`#analyze-story`, `#analysis-status`,
  `#implement-step`), not the orchestrator's `$` shorthand; use them
  exactly as written.
- Developer Notes must stay technology-neutral: never name specific tools,
  libraries, frameworks, or languages, not even in notes.
- Default save location is `docs/analysis/S<X.Y>-story-steps.md`; deviate
  only when the user explicitly provides a path in Step 6.
- The implementation-steps template must be reproduced with no additional
  formatting, headings, or commentary beyond what the template shows.
- The mode-gate message must say "story analysis", not "test generation".
- Keep the workflow steps, validation checklist, and template
  authoritative in SKILL.md and `references/`. Do not duplicate them here.
- The sentinel line `<!-- sentinel: planning/story-analysis -->` must
  remain the final content line of SKILL.md; the orchestrator quotes it to
  detect truncated loads.

## Version

- Current Version: 1.1.1
- Last Updated: 2026-09-26
- Stability: Experimental

## Purpose

This metadata file describes the story analysis skill. Workflow steps, the
Step 4a validation checklist, and the implementation-steps template are
defined in SKILL.md and `references/story-template.md`.

## Sync / Validation Checklist

Before considering this metadata file current, verify:

- [ ] `#analysis-status` description matches SKILL.md
- [ ] Gotchas / Sync Notes reflect the current SKILL.md gotchas
- [ ] Version and Last Updated are incremented after SKILL.md changes
- [ ] No workflow steps, validation checklist, or template details are duplicated here
