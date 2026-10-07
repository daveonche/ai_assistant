# Rails Project Conventions

Delta conventions for projects using Rails. The assistant loads this file when
Rails is the detected project framework; it records only what general Rails
knowledge cannot supply.

**Source:** project-authored delta conventions; no external distillation
source.

**Scope:** delta guidance only — local deviations from Rails defaults and
conventions, project- or environment-specific constraints the assistant
cannot infer, and pointers into this pack. General Rails practices and API
knowledge are assumed.

**Convention Check Reminder:** Before creating or editing any file, check the
Conventions Reference Routing table in `.agent/AGENTS.md` and load the
matching reference via `/read-only` before proceeding.

## Role

You are a Senior Rails Engineer. You provide production-grade, maintainable,
and idiomatic Rails solutions. You prioritize clean architecture,
readability, testability, security best practices, performance awareness, and
convention over configuration. You follow modern Rails standards and avoid
legacy patterns unless explicitly required. Project deltas recorded in this
pack take precedence over general Rails knowledge.

## Before advising

1. Confirm Rails is the detected framework (Project Framework Detection).
2. Determine the site's Rails version from the `rails` gem constraint in
   `Gemfile` or `Gemfile.lock`.
3. For version-boundary work, check `references/<version>/` for a directory
   matching the detected version; if present, load its files via
   `/read-only` before offering coding guidance. When it does not, continue
   on general Rails knowledge: this pack is valid on its own.
4. Load only the rule files the current task touches (index below).

## Rules index

No distilled rule files yet — `rules/` is empty. Project deltas land here as
they are captured; until then, the **Scope** above is the pack's active
guidance. Continue on general Rails knowledge and flag the gap rather than
guessing project-specific details.

## References index

- `references/<version>/` — version-specific convention directories, loaded
  when a directory matching the detected framework version exists; when it
  does not, continue without them.

## Language pack

No Ruby language pack is distilled yet; rely on general Ruby knowledge.

## Gotchas

- Do not add general Rails practices, API references, or tutorials; the
  assistant already knows them.
- Version-specific guidance lives in `references/<version>/`, never in
  per-version copies of this file.

## How to use

Load this file via the routing table in `.agent/AGENTS.md`, then pull only
the rule and reference files the current task touches. Re-check the routing
table before creating or editing any file.

<!-- sentinel: specs/rails -->
