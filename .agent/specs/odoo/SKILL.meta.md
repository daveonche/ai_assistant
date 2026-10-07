# Metadata: # Odoo Project Conventions

## Purpose

This metadata file describes the odoo spec pack entry (`SKILL.md`), a
placeholder pending distillation. The delta conventions, role, detection
steps, indexes, and load procedure live in `SKILL.md`; nothing here
duplicates them.

## SDLC Phase

- Phase: Cross-cutting
- Sub-Phase: Conventions reference
- Workflow: Loaded on demand via the Conventions Reference Routing table
  in `.agent/AGENTS.md` when Project Framework Detection identifies Odoo

## Complexity Rating

- Complexity: Low
- Cognitive Load: Low
- Technical Depth: Odoo addon framework (Python/XML); content pending
  distillation

## Usage Guidelines

- Prerequisite: Project Framework Detection has identified Odoo
- Requires:
  - The pack entry `.agent/specs/odoo/SKILL.md`
  - No rule or reference files yet; `rules/` and `references/` are empty

## Prompt Characteristics

- Input Driven: No (reference material, not a command workflow)
- State Dependent: No
- Requires Contextual Awareness: High (Odoo version and addon set)
- Command Driven: No

## Gotchas / Sync Notes

- Placeholder pack: do not fill it with general Odoo practices, API
  references, or tutorials; content arrives via distillation.
- Version-specific guidance belongs in `references/`, never in per-version
  copies of the entry file.
- Keep workflow instructions and indexes in `SKILL.md`; do not duplicate
  them here.

## Version

- Current Version: 0.1.0
- Last Updated: 2026-10-07
- Stability: Placeholder

## Sync / Validation Checklist

Before considering this metadata file current, verify:

- [ ] Scope description matches `SKILL.md`
- [ ] Gotchas / Sync Notes reflect the current `SKILL.md` gotchas
- [ ] Version and Last Updated are incremented after `SKILL.md` changes
- [ ] No rules, indexes, or role text are duplicated here
