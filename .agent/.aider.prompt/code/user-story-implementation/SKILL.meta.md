# Metadata: # User Story Implementation Prompt

## AI Assistant Compatibility

- Tested With:
  - Aider
  - GLM 5.3 Flash (August 27, 2026 release)
- Potential Compatible Assistants:
  - Other Claude models
  - GitHub Copilot (with modifications)
  - GPT-4

## SDLC Phase

- Phase: Code
- Sub-Phase: Story Implementation
- Workflow: Post-scaffolding sprint chain (implementation stage); usable standalone

## Complexity Rating

- Complexity: High
- Cognitive Load: High
- Technical Depth: Requires dependency compatibility analysis, incremental
  planning, and acceptance-criteria tracing across increments

## Usage Guidelines

- Prerequisite: The user story S<X.Y> to implement, loaded in context
- Requires:
  - Project technology stack documentation
  - Current dependency files (e.g., `package.json`, `requirements.txt`)
  - Existing project patterns for the assistant to follow
  - User availability to approve each step and run all tests

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes (resumes from the maintained progress checklist)
- Requires Contextual Awareness: High
- Command Driven: Yes (#implement-story, #implement-story-status)
- Diagram Support: None

## Command Behavior

- `#implement-story S<X.Y>`: Starts or resumes incremental implementation of
  the named story, gated on user approval at each `[STOP]` point.
- `#implement-story-status`: Reads the assistant's maintained progress
  checklist and formats it; does not advance the workflow.

## Gotchas / Sync Notes

- Never suggest direct package installation commands; update dependency files
  first. The Critical Dependency Management Rules in SKILL.md are authoritative.
- The user runs and verifies all tests; the assistant only proposes them.
- The progress checklist is private to the assistant; `#implement-story-status`
  reads from it.
- Keep the step-by-step workflow, dependency examples, and output templates
  authoritative in SKILL.md. Do not duplicate them here.
- The sentinel line `<!-- sentinel: code/user-story-implementation -->` must
  remain the final content line of SKILL.md; the orchestrator quotes it to
  detect truncated loads.

## Version

- Current Version: 1.0.0
- Last Updated: 2026-09-26
- Stability: Experimental

## Purpose

This metadata file describes the user story implementation skill. Workflow
steps, dependency rules, and templates are defined in SKILL.md.

## Sync / Validation Checklist

Before considering this metadata file current, verify:

- [ ] `#implement-story-status` description matches SKILL.md
- [ ] Gotchas / Sync Notes reflect the current SKILL.md gotchas
- [ ] Version and Last Updated are incremented after SKILL.md changes
- [ ] No workflow steps, dependency examples, or output templates are duplicated here
