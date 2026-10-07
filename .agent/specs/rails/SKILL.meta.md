# Metadata: # Rails Project Conventions

## Purpose

This metadata file describes the rails spec pack entry (`SKILL.md`). The
delta conventions, role, detection steps, indexes, and load procedure live
in `SKILL.md`; nothing here duplicates them.

## SDLC Phase

- Phase: Cross-cutting
- Sub-Phase: Conventions reference
- Workflow: Loaded on demand via the Conventions Reference Routing table
  in `.agent/AGENTS.md` when Project Framework Detection identifies Rails

## Complexity Rating

- Complexity: Low
- Cognitive Load: Low
- Technical Depth: Rails conventions and version-boundary discipline

## Usage Guidelines

- Prerequisite: Project Framework Detection has identified Rails
- Requires:
  - The pack entry `.agent/specs/rails/SKILL.md`
  - Task-matched rule files from `rules/`, loaded on demand
  - `references/<version>/` for work bound to a specific Rails version,
    when a matching directory exists

## Prompt Characteristics

- Input Driven: No (reference material, not a command workflow)
- State Dependent: No
- Requires Contextual Awareness: High (Rails version and project deltas)
- Command Driven: No

## Gotchas / Sync Notes

- Rules are delta guidance only; never add general Rails practices, API
  references, or tutorials to the pack.
- Version-specific guidance lives in `references/<version>/`; the pack has
  no per-version copies of the entry file.
- Keep workflow instructions and indexes in `SKILL.md`; do not duplicate
  them here.

## Version

- Current Version: 1.0.0
- Last Updated: 2026-10-07
- Stability: Stable

## Sync / Validation Checklist

Before considering this metadata file current, verify:

- [ ] Scope description matches `SKILL.md`
- [ ] Gotchas / Sync Notes reflect the current `SKILL.md` gotchas
- [ ] Version and Last Updated are incremented after `SKILL.md` changes
- [ ] No rules, indexes, or role text are duplicated here
