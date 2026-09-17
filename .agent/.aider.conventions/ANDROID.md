# Android Project Conventions

Delta conventions for projects building Android applications in Kotlin. The
assistant loads this file when Android is the detected project framework; it
records only what general Android and Kotlin knowledge cannot supply.

## Scope

Entries here are delta guidance only:

- Local deviations from Android and Kotlin defaults and conventions
- Project- or environment-specific constraints the assistant cannot infer
- Pointers to version-specific conventions under
  `.agent/.aider.conventions/references/`

Do not add general Android or Kotlin practices, API references, or tutorials; the
assistant already knows them.

## Version-specific conventions

Version-specific guidance lives in
`.agent/.aider.conventions/references/ANDROID/<version>/` (for example,
`.agent/.aider.conventions/references/ANDROID/v15`). When a directory matching the
detected framework version exists, load its files via `/read-only` before offering
coding guidance. When it does not, continue without them: this file is valid on its
own.
