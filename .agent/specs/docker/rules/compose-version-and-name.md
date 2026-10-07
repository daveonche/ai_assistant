# Rule: Version and name

- Do not add top-level `version:` to new files; remove it when editing
  existing ones. It is obsolete, does not select a schema, and produces a
  warning. Compose always validates against the most recent schema.
- Optional top-level `name` sets the project name when none is provided
  via CLI or `COMPOSE_PROJECT_NAME`. The resolved name is available for
  interpolation as `COMPOSE_PROJECT_NAME`.
