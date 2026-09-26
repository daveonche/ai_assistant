# Metadata: # Scaffolding Sprint Story Generation Prompt

## AI Assistant Compatibility

- Tested With:
  - Aider
  - GLM 5.3 Flash (August 27, 2026 release)
- Potential Compatible Assistants:
  - Other Claude models
  - GitHub Copilot (with modifications)
  - GPT-4 (with command-handoff adaptations)

## SDLC Phase

- Phase: Planning
- Sub-Phase: Sprint Scaffolding
- Workflow: Project Scaffolding Sprint Workflow Chain (story generation stage; activated via `$planning-scaffolding-sprint-story`)

## Complexity Rating

- Complexity: High
- Cognitive Load: High
- Technical Depth: Requires dependency-ordered sequencing of foundational
  setup stories and exact-version tracking

## Usage Guidelines

- Prerequisite: Core requirements, tech stack, and architecture docs in
  context (generatable via `$requirements-initial-project`,
  `$architecture-tech-stack`, `$architecture-design`)
- Requires:
  - Development environment needs
  - Technical dependencies with exact versions
  - Project structure requirements
- Modes: `/ask` for story generation and review; `/code` only when saving
  the finalized story file

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes
- Requires Contextual Awareness: High
- Command Driven: Yes ($planning-scaffolding-sprint-story, $planning-scaffolding-sprint-story-status)
- Diagram Support: None
- Story Format: Standardized template in `references/story-template.md`,
  loaded on demand (progressive disclosure)

## Command Behavior

- `$planning-scaffolding-sprint-story`: Starts or resumes scaffolding story
  generation — context verification, foundation analysis, story generation
  from the template, validation, review loop, then save via `/code`.
- `$planning-scaffolding-sprint-story-status`: Shows current progress only
  and does NOT activate the full workflow. To resume after viewing status,
  use `$planning-scaffolding-sprint-story`.

## Gotchas / Sync Notes

- Exact versions must be pinned before implementation; any version marked
  "latest stable" must be explicitly flagged for pinning.
- The story-analysis handoff requires
  `.agent/.aider.prompt/planning/story-analysis/SKILL.md` to be loaded
  first; do not assume it is already in context.
- `/read-only` and `/drop` commands must be output inline as part of a
  sentence; never execute them.
- The story template lives in `references/story-template.md`; load it only
  when needed to conserve context.
- Keep workflow steps, story categories, and the story template
  authoritative in SKILL.md and `references/`. Do not duplicate them here.
- The sentinel line `<!-- sentinel: planning/scaffolding-sprint-story -->`
  must remain the final content line of SKILL.md; the orchestrator quotes
  it to detect truncated loads.

## Version

- Current Version: 1.2.1
- Last Updated: 2026-09-26
- Stability: Experimental

## Purpose

This metadata file describes the scaffolding sprint story generation
skill. Workflow steps, story categories, and the story template are
defined in SKILL.md and `references/story-template.md`.

## Sync / Validation Checklist

Before considering this metadata file current, verify:

- [ ] `$planning-scaffolding-sprint-story-status` description matches SKILL.md
- [ ] Gotchas / Sync Notes reflect the current SKILL.md gotchas
- [ ] Version and Last Updated are incremented after SKILL.md changes
- [ ] No workflow steps, story categories, or template details are duplicated here
