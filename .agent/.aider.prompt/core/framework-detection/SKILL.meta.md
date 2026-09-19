# Metadata: Framework Detection Prompt

## AI Assistant Compatibility

- Tested With:
  - Aider
- Potential Compatible Assistants:
  - Other CLI coding assistants with read-only repository access

## SDLC Phase

- Phase: Any (cross-cutting utility)
- Sub-Phase: Pre-guidance framework identification
- Workflow: Session context preparation

## Complexity Rating

- Complexity: Low
- Cognitive Load: Low
- Technical Depth: Requires familiarity with framework manifest and source-layout conventions

## Usage Guidelines

- Prerequisite: A user request for coding guidance in a project session
- Requires:
  - Read-only access to root manifests and configuration files
  - Visibility into the source directory layout
- Activated by: `$core-framework-detection`, or the orchestrator's Project Framework Detection trigger before coding guidance

## Prompt Characteristics

- Input Driven: Yes (repository indicators)
- State Dependent: Yes (available framework-named conventions files)
- Requires Contextual Awareness: Medium
- Command Driven: Yes (`$core-framework-detection`)
- Diagram Support: None

## Command Behavior

- `$core-framework-detection`: Runs the framework detection procedure and announces the identified framework and version, or states that no framework was identified.

## Gotchas / Sync Notes

- Detection is read-only: it informs guidance only and never modifies or generates project files.
- Do not interleave detection with coding guidance; conclude detection first, then announce the result.
- Never load a conventions reference "just in case"; only on a match.
- When no framework-named conventions file matches the detected framework, make no recommendation.
- Keep the detection steps authoritative in SKILL.md. Do not duplicate them here.

## Version

- Current Version: 1.0.0
- Last Updated: 2026-09-19
- Stability: Experimental

## Purpose

This metadata file describes the framework detection utility prompt. Detection steps, the announcement format, and framework-conventions routing are defined in SKILL.md.

## Sync / Validation Checklist

Before considering this metadata file current, verify:

- [ ] `$core-framework-detection` description matches SKILL.md
- [ ] Gotchas / Sync Notes reflect the current SKILL.md gotchas
- [ ] SKILL.md contains the Convention Check Reminder line required by the orchestrator's routing rules
- [ ] Version and Last Updated are incremented after SKILL.md changes
- [ ] No detection steps, routing rules, or implementation details are duplicated here
