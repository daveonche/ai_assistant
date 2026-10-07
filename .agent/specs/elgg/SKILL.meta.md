# Metadata: # Elgg Framework Conventions

## Purpose

This metadata file describes the elgg spec pack entry (`SKILL.md`). The
delta conventions, role, rules index, references index, and load
procedure live in `SKILL.md`; nothing here duplicates them.

## SDLC Phase

- Phase: Cross-cutting
- Sub-Phase: Conventions reference
- Workflow: Loaded on demand via the Conventions Reference Routing table
  in `.agent/AGENTS.md` when Project Framework Detection identifies Elgg

## Complexity Rating

- Complexity: Low
- Cognitive Load: Low
- Technical Depth: Elgg plugin architecture (events, hooks, views,
  routing, services) and upgrade-path discipline

## Usage Guidelines

- Prerequisite: Project Framework Detection has identified Elgg
- Requires:
  - The pack entry `.agent/specs/elgg/SKILL.md`
  - Task-matched rule files from `rules/`, loaded on demand
  - `references/upgrading.md` for any work crossing a version boundary

## Prompt Characteristics

- Input Driven: No (reference material, not a command workflow)
- State Dependent: No
- Requires Contextual Awareness: High (Elgg version and plugin set)
- Command Driven: No

## Gotchas / Sync Notes

- Rules are delta guidance only; never add general Elgg practices, API
  references, or tutorials to the pack.
- Version-specific guidance lives in `references/upgrade-notes/`; the
  pack has no per-version convention directories.
- `references/upgrade-notes/` drives `rules/` updates in the same change.
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
