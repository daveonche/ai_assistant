# Metadata: Command Suggestions Prompt

## AI Assistant Compatibility

- Tested With:
  - Aider
- Potential Compatible Assistants:
  - Other CLI coding assistants that offer to execute suggested commands

## SDLC Phase

- Phase: Any (cross-cutting utility)
- Sub-Phase: Session communication
- Workflow: Verification and command hand-off

## Complexity Rating

- Complexity: Low
- Cognitive Load: Low
- Technical Depth: Requires knowledge of aider command recognition and pager behavior

## Usage Guidelines

- Prerequisite: A need to suggest CLI commands to the user
- Requires:
  - Awareness of which commands may produce long output
- Activated by: `$core-command-suggestions`

## Prompt Characteristics

- Input Driven: Yes (the commands being suggested)
- State Dependent: Yes (aider session, active shell)
- Requires Contextual Awareness: Low
- Command Driven: Yes (`$core-command-suggestions`)
- Diagram Support: None

## Command Behavior

- `$core-command-suggestions`: Activates the command-suggestion formatting rules, applied whenever CLI commands are suggested to the user.

## Gotchas / Sync Notes

- The long-output rules (e.g., git `--no-pager`) apply only to commands that may produce long output; do not rewrite short, quiet commands.
- Verification commands go in fenced code blocks tagged with a shell language, with no `/run` prefix, so aider offers to execute them directly.
- Ask the user to reply "done" after running verification commands; never ask for pasted output.
- Keep the formatting rules authoritative in SKILL.md. Do not duplicate them here.

## Version

- Current Version: 1.0.0
- Last Updated: 2026-09-19
- Stability: Experimental

## Purpose

This metadata file describes the command suggestions utility prompt. The formatting rules for long-output commands and verification commands are defined in SKILL.md.

## Sync / Validation Checklist

Before considering this metadata file current, verify:

- [ ] `$core-command-suggestions` description matches SKILL.md
- [ ] Gotchas / Sync Notes reflect the current SKILL.md gotchas
- [ ] SKILL.md contains the Convention Check Reminder line required by the orchestrator's routing rules
- [ ] Version and Last Updated are incremented after SKILL.md changes
- [ ] No formatting rules or implementation details are duplicated here
