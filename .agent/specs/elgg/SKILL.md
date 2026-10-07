# Elgg Framework Conventions

| Field | Value |
| --- | --- |
| Name | `elgg` |
| Description | Delta conventions for projects using Elgg. Use when writing or reviewing Elgg plugins, events, views, routing, web services, or upgrades. Triggers on "Elgg plugin", "Elgg upgrade", or Elgg reported by Project Framework Detection. |
| Source | Distilled from the Elgg manual: <https://learn.elgg.org/en/stable/guides/index.html> |
| Scope | Delta guidance only: local deviations, project constraints, and pointers into this pack. General Elgg practices and API knowledge are assumed. |

**Convention Check Reminder:** Before creating or editing any file, check
the Conventions Reference Routing table in `.agent/AGENTS.md` and load the
matching reference via `/read-only` before proceeding.

## Role

You are a Senior Elgg Engineer. You provide production-grade, maintainable,
and idiomatic Elgg solutions. You prioritize:

- Clean architecture
- Readability
- Testability
- Security best practices
- Performance awareness
- Convention over configuration

You follow modern Elgg standards — the plugin architecture of events,
hooks, views, routing, and services — and avoid legacy patterns unless
explicitly required. You never modify Elgg core; plugins extend it. This
role governs how guidance is delivered; the rules and references indexed
below govern what it contains.

## Before advising

1. Confirm Elgg is the detected framework (Project Framework Detection).
2. Determine the site's Elgg version from the `elgg/elgg` constraint in
   `composer.json` or `composer.lock`.
3. For any upgrade task or work crossing a version boundary, load
   `references/upgrading.md` via `/read-only` first, then the matching
   `references/upgrade-notes/<from>-to-<to>.md` file for each boundary
   crossed.
4. Load only the rule files the current task touches (index below).

## Rules index

Atomic conventions, one topic per file, loaded on demand via
`/read-only .agent/specs/elgg/rules/<topic>.md` (grouped topics:
`/read-only .agent/specs/elgg/rules/<group>/<topic>.md`).
`rules/index.md` is the descriptive topic map; a topic still marked
`pending` there means the distilled file does not exist yet — continue on
general knowledge and flag the gap rather than guessing current API
details.

- Core: `access`, `accessibility`, `actions`, `ajax`, `authentication`,
  `capabilities`, `context`, `cron`, `database`, `dont-modify-core`,
  `email`, `errors`, `events-list`, `file-system`, `group-tools`,
  `guidelines`, `helpers`, `i18n`, `javascript`, `menus`, `notifications`,
  `page-owner`, `permissions-check`, `plugins`, `restore`, `river`,
  `routing`, `search`, `services`, `settings`, `themes`, `upgrading-data`,
  `views`, `walled-garden`, `web-services`, `widgets`
- `events-list/`: `access`, `actions-ajax`, `entities`, `files`,
  `notifications`, `other`, `permissions`, `routing`, `search`, `system`,
  `users`, `views`
- `plugins/`: `bootstrap`, `dependencies`, `plugin-skeleton`
- `views/`: `foot-vs-footer`, `page-structure`, `simplecache`
- `web-services/`: `hmac`, `result`

## References index

- `references/upgrading.md` — version-independent upgrade rules: the
  standard procedure applied one major version at a time from any site on
  Elgg `2.3.*` or later, the composer patch policy, and the legacy manual
  approach for earlier versions.
- `references/upgrade-notes/` — per-version change list
  (`<from>-to-<to>.md`) that drives updates to `rules/`; load the notes
  for each boundary crossed.
- `references/source-listing-7.1.json` — provenance manifest for the 7.1
  distillation pass; machine-readable, not loaded for guidance.

## Language pack

Elgg is PHP. For language-level guidance (type system, PSR, SOLID, modern
PHP), load `.agent/specs/php-best-practices/SKILL.md` via `/read-only`.

## Gotchas

- Rules are delta guidance only; do not add general Elgg practices, API
  references, or tutorials.
- Version-specific guidance lives in `references/upgrade-notes/`, not
  per-version directories; route version questions through
  `references/upgrading.md`.
- `references/upgrade-notes/` drives `rules/` updates: when a note
  changes, update the affected rule files in the same change.

## How to use

Load this file via the routing table in `.agent/AGENTS.md`, then pull only
the rule and reference files the current task touches. Re-check the
routing table before creating or editing any file.

<!-- sentinel: specs/elgg -->
