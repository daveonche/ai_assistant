# Metadata: Code Review Prompt

## Description

Provides a staged workflow for reviewing a target file, collecting optional coding conventions, and implementing approved improvements after a controlled `/code proceed` transition.

## AI Assistant Compatibility

- Tested With:
  - Aider
  - LLM: Claude 3.5 Sonnet (October 22, 2024 release)
- Potential Compatible Assistants:
  - Other Claude models
  - GitHub Copilot (with modifications)

## SDLC Phase

- Phase: Development
- Sub-Phase: Code Review
- Workflow: Review, Confirm, Improve

## Complexity Rating

- Complexity: Medium
- Cognitive Load: Moderate
- Technical Depth: Requires code analysis and convention awareness

## Usage Guidelines

- Prerequisite: Target file exists in the repository
- Requires:
  - Target file path via `$code-review <file>`
  - Optional coding convention or convention file
  - `/ask` mode before review
  - `/code proceed` before implementation

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes
- Requires Contextual Awareness: High
- Mode Sensitive: Yes (`/ask` for review, `/code` for implementation)
- Command Driven: Yes (`$code-review <file>`, `/code proceed`)
- Sequential Execution: Enforced stage order

## Best Practices

- Ask for coding conventions before reviewing
- Keep the review concise and focused
- Wait for user confirmation before implementation
- Require explicit `/code proceed` before editing
- Review against agreed conventions and general best practices

## Potential Challenges

- Missing or vague coding conventions
- Reviewing large files without clear scope
- User confusion around mode switching
- Implementing changes before confirmation
- Scope creep beyond confirmed improvements

## Recommended Mitigation Strategies

- Explicit convention prompt at the start
- Keep review scoped to the target file
- Use clear `[STOP]` points
- Use a short, unambiguous `/code proceed` handoff
- Confirm exact improvements before coding

## Version

- Current Version: 1.0.0
- Last Updated: 2026-08-23
- Stability: Experimental

## Integration Points

- `.aider.prompt/AGENTS.md` shorthand orchestrator
- `.aider.prompt/code/review/SKILL.md`
- `.aider.prompt/cod/implementation/SKILL.md`
- `.aider.prompt/testing/unit-test/SKILL.md`

## Success Metrics

- All workflow stages completed
- User conventions collected before review
- User confirmation before edits
- Successful `/code proceed` transition
- Confirmed improvements implemented

## Failure Modes

- Review started outside `/ask` mode
- Missing target file
- Unclear or skipped conventions
- Changes attempted before `/code proceed`
- Review scope expands beyond the target file
