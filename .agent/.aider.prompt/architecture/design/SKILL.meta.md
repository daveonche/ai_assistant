# Metadata: # Architecture Design Generator Prompt

## AI Assistant Compatibility

- Tested With:
  - Aider
  - LLM: Claude 3.5 Sonnet (October 22, 2024 release)
- Potential Compatible Assistants:
  - Other Claude models
  - GitHub Copilot (with modifications)
  - GPT-4 (with architectural diagram adaptations)

## SDLC Phase

- Phase: Design
- Sub-Phase: Initial Architecture
- Workflow: Project Scaffolding

## Complexity Rating

- Complexity: High
- Cognitive Load: High
- Technical Depth: Requires comprehensive understanding of architectural patterns and principles

## Usage Guidelines

- Prerequisite: Project requirements documentation
- Requires:
  - Technology stack documentation
  - Core dependency definitions
  - Project scope understanding
  - Basic technical constraints

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes
- Requires Contextual Awareness: High
- Command Driven: Yes (#generate-architecture, #architecture-status)
- Diagram Support: Mermaid.js integration

## Command Behavior

- `#generate-architecture`: Starts or resumes the architecture design workflow.
- `#architecture-status`: Shows current progress only and does NOT activate the full workflow. To resume after viewing status, use `#generate-architecture`.

## Gotchas / Sync Notes

- Mermaid diagrams must be linked as PNG images; never embed the Mermaid diagram source in documentation markdown.
- Never assume a specific application type (UI/CLI/Service). Confirm the application type with the user before making decisions.
- Keep workflow instructions authoritative in SKILL.md. Do not duplicate full workflow steps or implementation details here.

## Version

- Current Version: 1.1.0
- Last Updated: 2026-08-26
- Stability: Experimental

## Purpose
This metadata file describes the architecture design generator skill. Workflow instructions, command behavior, and stop points are defined in SKILL.md.

## Sync / Validation Checklist

Before considering this metadata file current, verify:
- [ ] `#architecture-status` description matches SKILL.md
- [ ] Gotchas / Sync Notes reflect the current SKILL.md gotchas
- [ ] Version and Last Updated are incremented after SKILL.md changes
- [ ] No full workflow steps, command highlights, or implementation details are duplicated here
