# Elgg Project Conventions

Delta conventions for projects using Elgg. The assistant loads this file when Elgg
is the detected project framework; it records only what general Elgg knowledge
cannot supply.

## Scope

Entries here are delta guidance only:

- Local deviations from Elgg defaults and conventions
- Project- or environment-specific constraints the assistant cannot infer
- Pointers to distilled references under
  `.agent/specs/references/`

Do not add general Elgg practices, API references, or tutorials; the assistant
already knows them.

## Version-specific conventions

Version-specific guidance lives in
`.agent/specs/references/ELGG/<version>/` (for example,
`.agent/specs/references/ELGG/v7`). When a directory matching the
detected framework version exists, load its files via `/read-only` before offering
coding guidance. When it does not, continue without them: this file is valid on its
own.

## Developer guide

Current-state subsystem and API guidance lives in
`.agent/specs/references/ELGG/developer-guide/`: distilled topic
files tracking the stable manual at
<https://learn.elgg.org/en/stable/guides/index.html> and updated in place as
it changes; the per-version change list that drives those updates lives in
`references/ELGG/upgrade-notes/`. Load `developer-guide/index.md` via
`/read-only` for the topic map, then load only the topic files the current
task touches. When a matching topic file is still `pending`, continue on
general knowledge and flag the gap rather than guessing current API details.

## Upgrading

Upgrade-path guidance lives in
`.agent/specs/references/ELGG/upgrading.md`: version-independent
upgrade rules, the standard upgrade procedure applied one major version at a
time from any site on Elgg `2.3.*` or later up to the latest stable version,
the composer patch policy, and the legacy manual approach for earlier
versions. It is distilled from the official Upgrading Elgg documentation. Load
it via `/read-only` before advising on any Elgg upgrade or on work that crosses
an Elgg version boundary.
