# Provenance

Upstream sources and migration record for the docker pack. Use for
mechanical upstream diffing: when an upstream page changes, map the diff
onto the rule file listed here.

## Sources

| Upstream | Maps to |
| :--- | :--- |
| [Building best practices](https://docs.docker.com/build/building/best-practices/) | `rules/dockerfile-*.md` |
| [Dockerfile reference](https://docs.docker.com/reference/dockerfile/) | `rules/dockerfile-*.md` |
| [Compose file reference](https://docs.docker.com/reference/compose-file.md) and its sub-pages (version-and-name, services, networks, volumes, configs, secrets) | `rules/compose-*.md` |
| [docker-expert SKILL.md](https://github.com/davila7/claude-code-templates/blob/main/cli-tool/components/skills/development/docker-expert/SKILL.md) | persona (`SKILL.md` Role), `references/diagnostics-playbook.md`, `rules/dockerfile-secrets.md` |

## Migration record

- 2026-10-07: Pack created. `rules/dockerfile-*` migrated from the
  former `.agent/specs/references/docker-best-practices.md`;
  `rules/compose-*` from the former
  `.agent/specs/references/compose-file-spec.md`; `rules/layout-*` from
  the former `.agent/specs/references/docker-project-layout.md`
  (repo-authored, no upstream source). All three flat files deleted;
  routing rows in `.agent/AGENTS.md` repointed to
  `.agent/specs/docker/SKILL.md`.
- Dedupe decisions: "relative bind paths must start with `.` or `..`"
  kept only in `rules/compose-gotchas.md` (cross-referenced from
  `rules/layout-compose-placement.md`); `docker compose config --quiet`
  kept only in the pack entry's How to use; the layout intro's
  "composes with" note absorbed by the pack Scope.
- Cross-reference fixes: the dev-image `COPY` gotcha now points to
  `rules/dockerfile-modern-syntax.md` (was the deleted flat file); the
  single-log-file mount gotcha now points to
  `rules/layout-log-capture.md`.
- Discarded from docker-expert: YAML front matter, subagent handoffs,
  generic tutorial examples (multi-stage Node, distroless, dev override,
  production compose — the last also violated the no-`version:` and
  `docker compose` rules), and review checklists made redundant by
  `rules/`.
