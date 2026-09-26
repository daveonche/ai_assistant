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

- Phase: Planning
- Sub-Phase: Sprint Preparation
- Workflow: Post-Scaffolding Sprint Workflow Chain (analysis stage; activated via `$planning-implementation-analysis`)

## Complexity Rating

- Complexity: Medium
- Cognitive Load: Moderate
- Technical Depth: Requires cross-checking requirements and user stories
  against actual source files

## Usage Guidelines

- Prerequisite: Requirements list, user stories, and tech stack in context
- Requires:
  - Project requirements list (e.g., `docs/requirements/core_requirements.md`)
  - Current user stories (e.g., `docs/sprints/`)
  - Technology stack documentation (e.g., `docs/tech_stack.md`)
  - Source, config, and script files needed as evidence
  - Previous implementation status report (optional, for comparison)
- Modes: Analysis in `/ask`; save the approved report in `/code`
- Default output: `docs/implementation_status.md` (update only changed
  sections; preserve history unless explicitly overwritten)

## Workflow Chain

- Previous: `$planning-scaffolding-sprint-story`
- Current: `$planning-implementation-analysis`
- Next: `$planning-sprint-story` (report ends with `Next workflow step: #generate-sprint-stories`)

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes (resumes from the workflow checklist)
- Requires Contextual Awareness: High
- Command Driven: Yes (#analyze-impl, #analyze-impl-status)
- Diagram Support: None

## Command Behavior

- `#analyze-impl`: Starts or resumes the analysis — mode check, context
  verification, codebase analysis with evidence citations, review loop,
  then save via `/code`.
- `#analyze-impl-status`: Shows current progress only and does NOT activate
  the full workflow. To resume after viewing status, use `#analyze-impl`.

## Gotchas / Sync Notes

- Never classify a feature as Complete or Partially Implemented without at
  least one source-file citation; features with no source evidence must be
  classified Not Yet Implemented.
- Documentation can drift: requirements and user stories may describe
  features that no longer match the code. Verify claims against source
  files, not documentation alone.
- Features are often split across multiple files (models, handlers/views,
  templates). Search broadly before marking something Partially Implemented.
- Re-running the analysis must preserve historical records in
  `docs/implementation_status.md` unless the user explicitly asks to
  overwrite them.
- Keep the analysis methodology, report template, and workflow steps
  authoritative in SKILL.md. Do not duplicate them here.
- The sentinel line `<!-- sentinel: planning/implementation-analysis -->`
  must remain the final content line of SKILL.md; the orchestrator quotes
  it to detect truncated loads.

## Version

- Current Version: 1.2.1
- Last Updated: 2026-09-26
- Stability: Experimental

## Purpose

This metadata file describes the implementation status analysis skill.
Analysis methodology, report structure, and workflow steps are defined in
SKILL.md.

## Sync / Validation Checklist

Before considering this metadata file current, verify:

- [ ] `#analyze-impl-status` description matches SKILL.md
- [ ] Gotchas / Sync Notes reflect the current SKILL.md gotchas
- [ ] Version and Last Updated are incremented after SKILL.md changes
- [ ] No methodology, report templates, or workflow steps are duplicated here
