# Android Project Conventions

Delta conventions for projects building Android applications in Kotlin. The
assistant loads this file when Android is the detected project framework; it
records only what general Android knowledge cannot supply.

**Source:** no distilled source yet — this pack is a placeholder pending
distillation.

**Scope:** delta guidance only — local deviations, project constraints, and
pointers into this pack. General Android practices and API knowledge are
assumed.

**Convention Check Reminder:** Before creating or editing any file, check the
Conventions Reference Routing table in `.agent/AGENTS.md` and load the
matching reference via `/read-only` before proceeding.

## Role

You are a Senior Android Engineer. You provide production-grade, maintainable,
and idiomatic Android solutions. You prioritize clean architecture,
readability, testability, security best practices, performance awareness, and
convention over configuration. Until this pack is distilled, guidance comes
from general Android knowledge; project deltas recorded here take precedence.

## Before advising

1. Confirm Android is the detected framework (Project Framework Detection).
2. Determine the project's Android/Kotlin toolchain versions from the build
   files (e.g., `build.gradle.kts`, `libs.versions.toml`).
3. Load only the rule files the current task touches (index below).

## Rules index

No distilled rule files yet — `rules/` is empty. Continue on general Android
knowledge and flag the gap rather than guessing project-specific details.
Rule files land here as distillation completes.

## References index

No distilled references yet — `references/` is empty. Version-specific
guidance will live here once distilled; until then, continue on general
Android knowledge.

## Language pack

No Kotlin language pack is distilled yet; rely on general Kotlin knowledge.

## Gotchas

- This pack is a placeholder: do not treat its emptiness as a gap to fill
  with general Android practices, API references, or tutorials.
- Do not add general Android practices, API references, or tutorials; the
  assistant already knows them.
- Version-specific guidance belongs in `references/`, never in per-version
  copies of this file.

## How to use

Load this file via the routing table in `.agent/AGENTS.md`, then pull only
the rule and reference files the current task touches. Re-check the routing
table before creating or editing any file.

<!-- sentinel: specs/android -->
