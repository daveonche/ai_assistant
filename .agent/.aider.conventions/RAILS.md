# Rails Project Conventions

Delta conventions for projects using Rails. The assistant loads this file when
Rails is the detected project framework; it records only what general Rails
knowledge cannot supply.

## Scope

Entries here are delta guidance only:

- Local deviations from Rails defaults and conventions
- Project- or environment-specific constraints the assistant cannot infer
- Pointers to version-specific conventions under
  `.agent/.aider.conventions/references/`

Do not add general Rails practices, API references, or tutorials; the assistant
already knows them.

## Version-specific conventions

Version-specific guidance lives in
`.agent/.aider.conventions/references/RAILS/<version>/` (for example,
`.agent/.aider.conventions/references/RAILS/v7`). When a directory matching the
detected framework version exists, load its files via `/read-only` before offering
coding guidance. When it does not, continue without them: this file is valid on its
own.
