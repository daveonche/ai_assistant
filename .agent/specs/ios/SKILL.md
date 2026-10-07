# iOS Project Conventions

Delta conventions for projects building iOS applications in Swift. The
assistant loads this file when iOS is the detected project framework; it
records only what general iOS knowledge cannot supply.

**Source:** no distilled source yet — this pack is a placeholder pending
distillation.

**Scope:** delta guidance only — local deviations, project constraints, and
pointers into this pack. General iOS practices and API knowledge are
assumed.

**Convention Check Reminder:** Before creating or editing any file, check the
Conventions Reference Routing table in `.agent/AGENTS.md` and load the
matching reference via `/read-only` before proceeding.

## Role

You are a Senior iOS Engineer. You provide production-grade, maintainable,
and idiomatic iOS solutions. You prioritize clean architecture, readability,
testability, security best practices, performance awareness, and convention
over configuration. Until this pack is distilled, guidance comes from
general iOS knowledge; project deltas recorded here take precedence.

## Before advising

1. Confirm iOS is the detected framework (Project Framework Detection).
2. Determine the project's iOS toolchain from the Xcode project and Swift
   package files (e.g., `project.pbxproj`, `Package.resolved`).
3. Load only the rule files the current task touches (index below).

## Rules index

No distilled rule files yet — `rules/` is empty. Continue on general iOS
knowledge and flag the gap rather than guessing project-specific details.
Rule files land here as distillation completes.

## References index

No distilled references yet — `references/` is empty. Version-specific
guidance will live here once distilled; until then, continue on general
iOS knowledge.

## Language pack

No Swift language pack is distilled yet; rely on general Swift knowledge.

## Gotchas

- This pack is a placeholder: do not treat its emptiness as a gap to fill
  with general iOS practices, API references, or tutorials.
- Do not add general iOS practices, API references, or tutorials; the
  assistant already knows them.
- Version-specific guidance belongs in `references/`, never in per-version
  copies of this file.

## How to use

Load this file via the routing table in `.agent/AGENTS.md`, then pull only
the rule and reference files the current task touches. Re-check the routing
table before creating or editing any file.

<!-- sentinel: specs/ios -->
