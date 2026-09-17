# Elgg Project Conventions

Delta conventions for projects using Elgg. The assistant loads this file when Elgg
is the detected project framework; it records only what general Elgg knowledge
cannot supply.

## Scope

Entries here are delta guidance only:

- Local deviations from Elgg defaults and conventions
- Project- or environment-specific constraints the assistant cannot infer
- Pointers to version-specific conventions under
  `.agent/.aider.conventions/references/`

Do not add general Elgg practices, API references, or tutorials; the assistant
already knows them.

## Version-specific conventions

Version-specific guidance lives in
`.agent/.aider.conventions/references/ELGG/<version>/` (for example,
`.agent/.aider.conventions/references/ELGG/v7`). When a directory matching the
detected framework version exists, load its files via `/read-only` before offering
coding guidance. When it does not, continue without them: this file is valid on its
own.
