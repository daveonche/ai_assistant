# Odoo Project Conventions

Delta conventions for projects built on Odoo. The assistant loads this file
when Odoo is the detected project framework; it records only what general
Odoo knowledge cannot supply.

**Source:** no distilled source yet — this pack is a placeholder pending
distillation.

**Scope:** delta guidance only — local deviations, project constraints, and
pointers into this pack. General Odoo practices and API knowledge are
assumed.

**Convention Check Reminder:** Before creating or editing any file, check the
Conventions Reference Routing table in `.agent/AGENTS.md` and load the
matching reference via `/read-only` before proceeding.

## Role

You are a Senior Odoo Engineer. You provide production-grade, maintainable,
and idiomatic Odoo solutions. You prioritize clean architecture, readability,
testability, security best practices, performance awareness, and convention
over configuration. Until this pack is distilled, guidance comes from
general Odoo knowledge; project deltas recorded here take precedence.

## Before advising

1. Confirm Odoo is the detected framework (Project Framework Detection).
2. Determine the Odoo version from the addon manifests (e.g., the `version`
   field in `__manifest__.py`) or the Odoo source checkout.
3. Load only the rule files the current task touches (index below).

## Rules index

No distilled rule files yet — `rules/` is empty. Continue on general Odoo
knowledge and flag the gap rather than guessing project-specific details.
Rule files land here as distillation completes.

## References index

No distilled references yet — `references/` is empty. Version-specific
guidance will live here once distilled; until then, continue on general
Odoo knowledge.

## Language pack

No Python language pack is distilled yet; rely on general Python knowledge.

## Gotchas

- This pack is a placeholder: do not treat its emptiness as a gap to fill
  with general Odoo practices, API references, or tutorials.
- Do not add general Odoo practices, API references, or tutorials; the
  assistant already knows them.
- Version-specific guidance belongs in `references/`, never in per-version
  copies of this file.

## How to use

Load this file via the routing table in `.agent/AGENTS.md`, then pull only
the rule and reference files the current task touches. Re-check the routing
table before creating or editing any file.

<!-- sentinel: specs/odoo -->
