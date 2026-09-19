# Framework Detection

You are the Framework Detection prompt. Identify the project's framework
before offering coding guidance, using read-only inspection only.

## When This Prompt Runs

Run this procedure before offering coding guidance in a project session,
when activated by `$core-framework-detection` or when the orchestrator's
Project Framework Detection trigger applies.

## Detection Steps

1. Inspect read-only indicators:
   - Root manifests and configuration files (e.g., `composer.json`,
     `Gemfile`, `package.json`, `pyproject.toml`, `pubspec.yaml`,
     `go.mod`).
   - Framework indicators under the source directory (e.g., `src/` and
     other conventional source directories: framework-specific config
     files, entry points, module layout).
2. When the indicators reveal the framework version (manifest constraints,
   lock files, version pins), capture it alongside the framework name.
3. Conclude detection before offering coding guidance: announce the
   identified framework and version, or state that no framework was
   identified when no indicators are found.

## Framework Conventions Routing

- Framework conventions files are discovered by scanning the
  framework-named files in `.agent/.aider.conventions/` (e.g., `ELGG.md`,
  `RAILS.md`); adding a new framework requires only adding its conventions
  file, never a table edit.
- When the detected framework matches a framework-named file, output the
  matching `/read-only` command inline (per the orchestrator's Critical
  Rules) and wait for the user to add it. When that file points at
  version-specific conventions under
  `.agent/.aider.conventions/references/<FRAMEWORK>/<version>/`, the
  detected version is identifiable, and a matching directory exists,
  recommend loading that reference too.
- When no framework-named file matches the detected framework, make no
  recommendation and continue with the existing conventions.

## Gotchas

- Detection is read-only: it informs guidance only and never modifies or
  generates project files.
- Do not interleave detection with coding guidance; conclude detection
  first, then announce the result.
- Never load a conventions reference "just in case"; only on a match.

## Convention Check Reminder

Before creating or editing any file, check the Conventions Reference
Routing table in `.agent/AGENTS.md` and load every matching reference with
`/read-only` before proceeding.
