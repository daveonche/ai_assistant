# Metadata: # Docker Conventions

## Purpose

This metadata file describes the docker spec pack entry (`SKILL.md`). The
delta conventions, role, detection steps, indexes, and load procedure live
in `SKILL.md`; nothing here duplicates them.

## SDLC Phase

- Phase: Cross-cutting
- Sub-Phase: Conventions reference
- Workflow: Loaded on demand via the Conventions Reference Routing table
  in `.agent/AGENTS.md` when a task touches a `Dockerfile*`,
  `.dockerignore`, a Compose file, or a Docker/Compose project layout

## Complexity Rating

- Complexity: Low
- Cognitive Load: Low
- Technical Depth: Dockerfile/Compose exact syntax, supply-chain
  pinning, and project layout discipline

## Usage Guidelines

- Prerequisite: none (file-type matched; not gated on Project Framework
  Detection)
- Requires:
  - The pack entry `.agent/specs/docker/SKILL.md`
  - Task-matched rule files from `rules/`, loaded on demand
  - `references/` for diagnostics and provenance, loaded on demand

## Prompt Characteristics

- Input Driven: No (reference material, not a command workflow)
- State Dependent: No
- Requires Contextual Awareness: Medium (file type and build context)
- Command Driven: No

## Gotchas / Sync Notes

- Rules are delta guidance only; never add general Docker practices, API
  references, or tutorials to the pack.
- `rules/dockerfile-*` files were migrated from the former
  `.agent/specs/references/docker-best-practices.md`; `rules/compose-*`
  files from the former `.agent/specs/references/compose-file-spec.md`;
  `rules/layout-*` files from the former
  `.agent/specs/references/docker-project-layout.md`. All three flat
  files are deleted; upstream docs diffs map onto rule files by section
  (see `references/provenance.md`).
- Keep workflow instructions and indexes in `SKILL.md`; do not duplicate
  them here.

## Version

- Current Version: 1.0.0
- Last Updated: 2026-10-07
- Stability: Stable

## Sync / Validation Checklist

Before considering this metadata file current, verify:

- [ ] Scope description matches `SKILL.md`
- [ ] Gotchas / Sync Notes reflect the current `SKILL.md` gotchas
- [ ] Version and Last Updated are incremented after `SKILL.md` changes
- [ ] No rules, indexes, or role text are duplicated here
