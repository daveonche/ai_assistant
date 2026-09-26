# Metadata: # AI Code Tutor Prompt

## AI Assistant Compatibility

- Tested With:
  - Aider
  - GLM 5.3 Flash (August 27, 2026 release)
- Potential Compatible Assistants:
  - Other Claude models
  - GitHub Copilot (with modifications)
  - GPT-4

## SDLC Phase

- Phase: Learning
- Sub-Phase: Codebase Tutorial
- Workflow: On-demand tutorial (standalone `$learning-project-tutor` command)

## Complexity Rating

- Complexity: Medium
- Cognitive Load: Medium
- Technical Depth: Requires codebase analysis from user-provided files and
  interactive component-by-component explanation

## Usage Guidelines

- Prerequisite: Run in `/ask` mode; no code changes required
- Requires:
  - Target code files or directories added via `/read-only` (key entry
    points, not the entire repository)
  - User availability to answer questions at each stop point
  - User confirmation that requested files are loaded before analysis

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes (deep dives build on the overview stage)
- Requires Contextual Awareness: Medium
- Command Driven: Yes ($learning-project-tutor)
- Diagram Support: None

## Command Behavior

- `$learning-project-tutor`: Starts the interactive tutorial — mode
  verification, context verification, high-level overview, component deep
  dives, improvement analysis with learning path, then revisit-or-end check.

## Gotchas / Sync Notes

- The high-level overview is based only on files added to the chat, not the
  entire repository.
- If a directory cannot be added, ask for its individual files instead.
- The workflow waits for explicit user input at each stop point.
- Keep the step-by-step workflow and stage details authoritative in
  SKILL.md. Do not duplicate them here.
- The sentinel line `<!-- sentinel: learning/project-tutor -->` must remain
  the final content line of SKILL.md; the orchestrator quotes it to detect
  truncated loads.

## Version

- Current Version: 1.0.0
- Last Updated: 2026-09-26
- Stability: Experimental

## Purpose

This metadata file describes the AI code tutor skill. Workflow steps, stage
details, and stop points are defined in SKILL.md.

## Sync / Validation Checklist

Before considering this metadata file current, verify:

- [ ] Command description matches SKILL.md
- [ ] Gotchas / Sync Notes reflect the current SKILL.md behavior
- [ ] Version and Last Updated are incremented after SKILL.md changes
- [ ] No workflow steps or stage details are duplicated here
