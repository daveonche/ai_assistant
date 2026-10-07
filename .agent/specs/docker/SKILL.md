# Docker Conventions

Delta conventions for Dockerfiles, `.dockerignore` files, Docker
Compose files, and Docker/Compose project layout in this repository.
This pack records only repo-relevant rules and easily-got-wrong
details; general Docker knowledge (multi-stage build semantics,
instruction reference, cache ordering, Compose service concepts) is
assumed. Consult the Docker documentation when needed.

**Source:** Docker documentation — [Building best practices](https://docs.docker.com/build/building/best-practices/), [Dockerfile reference](https://docs.docker.com/reference/dockerfile/), [Compose file reference](https://docs.docker.com/reference/compose-file.md) — and the docker-expert skill from [claude-code-templates](https://github.com/davila7/claude-code-templates/blob/main/cli-tool/components/skills/development/docker-expert/SKILL.md) (persona and diagnostics only).

**Scope:** Every `Dockerfile*` (e.g., `.agent/Dockerfile.aider`),
`*.dockerfile`, and `.dockerignore`; every Compose file (`compose.yml`,
`compose.yaml`, `docker-compose*.yml`/`*.yaml`); Compose snippets
embedded in documentation or CI configuration; and the project layout
and command execution of any Docker/Compose-orchestrated project
(compose file placement, `docker/<service>/` build contexts,
`.log/<service>.log` logs, in-container commands). When a Compose
snippet appears inside a CI workflow, apply
`.agent/specs/references/ci-cd-best-practices.md` to the surrounding CI
structure and this pack to the Compose content.

**Convention Check Reminder:** Before creating or editing any file, check the Conventions Reference Routing table in `.agent/AGENTS.md` and load the matching reference via `/read-only` before proceeding.

## Role

You are a Docker conventions reviewer for this repository. Priorities,
in order:

1. Supply-chain integrity: pinned parser directives and base-image
   digests.
2. Exact syntax that the Dockerfile parser, YAML, or Compose silently
   misparse.
3. Layout and execution discipline: compose files at the project root,
   per-service build contexts, flat `.log/` files, every project
   command run in the container.
4. Delta-only guidance: never restate general Docker practices, API
   references, or tutorials.

## Before advising

1. Locate the files in scope: `Dockerfile*`, `.dockerignore`, and
   Compose files. Detection is read-only; it never modifies project
   files.
2. Check each Dockerfile for the `# syntax=docker/dockerfile:1`
   directive and digest-pinned base images.
3. Check Compose files for an obsolete top-level `version:` key and
   unquoted port or boolean values.
4. Check the layout: compose files at the project root, a
   `docker/<service>/` context for every `build:` service, `.log/`
   holding only flat files named after existing services.
5. Load the task-matched rule files from the index below before giving
   guidance.

## Rules index

- `rules/dockerfile-parser-directive.md` — pin the BuildKit frontend with `# syntax=docker/dockerfile:1`; snippets carry it too.
- `rules/dockerfile-base-image-pinning.md` — pin base images by digest; resolve with `docker buildx imagetools inspect`; stay current via Dependabot or `docker scout`.
- `rules/dockerfile-rebuild-flags.md` — `--pull` refreshes the base image, `--no-cache` re-runs steps; combine for both.
- `rules/dockerfile-modern-syntax.md` — heredocs over `&&` chains, bind mounts over single-use `COPY`, `ADD --checksum` over manual fetch.
- `rules/dockerfile-build-hygiene.md` — sorted multi-line arguments, space before continuation backslashes, `.dockerignore` for build-irrelevant files.
- `rules/dockerfile-secrets.md` — no secrets in `ENV`, build args, or layers; BuildKit secret mounts; Compose `secrets:` at runtime.
- `rules/compose-version-and-name.md` — no top-level `version:`; optional top-level `name:` and `COMPOSE_PROJECT_NAME`.
- `rules/compose-exact-syntax.md` — quote ports and booleans; `pull_policy` values; `depends_on` long syntax; `external: true` allows only `name`.
- `rules/compose-gotchas.md` — the full Compose trap list (network mode vs networks, env precedence, `$$` interpolation, reserved labels, …).
- `rules/layout-canonical.md` — canonical layout tree; the service name ties together build context, log file, and `services:` entry; rename them together.
- `rules/layout-compose-placement.md` — compose files stay at the project root; bind-mount `./src`, `./.log`, `./config` instead of baking them into images.
- `rules/layout-command-execution.md` — every project command runs in the container (`run --rm` / `exec`); the host needs only Docker, Compose, and git.
- `rules/layout-log-capture.md` — flat `.log/<service>.log` files, capture commands, error-only variant, app-written logs.
- `rules/layout-test-output.md` — test output minimal for chat, full to `.log/<service>.test.log`; paste only failure lines.

## References index

- `references/diagnostics-playbook.md` — symptom → root cause → solution patterns for build performance, security, image size, networking, and dev-workflow problems.
- `references/provenance.md` — upstream source manifest and migration record for this pack.

## Language pack

None — Docker is a technology pack, not a framework pack.

## Gotchas

- Tags are mutable: the same tag can resolve to a different image over
  time — pin digests.
- `--pull` and `--no-cache` are commonly confused; `--pull` does not
  re-run build steps.
- A missing `# syntax=` directive makes newer syntax (e.g.,
  `ADD --checksum`) fail on older frontends.
- Top-level `version:` in Compose is obsolete; it only produces a
  warning.
- Unquoted `8080:80` parses as a number; unquoted `no` parses as a
  boolean.
- `external: true` rejects every attribute except `name`.
- Compose interpolates `$` in `command:`; write `$$` for a container-time
  `$`.
- Never bind-mount a single `.log/<name>.log` file: a missing host file
  becomes a *directory*, and save-by-rename editors break single-file
  mounts. Mount `.log/` as a whole.
- The full Compose trap list lives in `rules/compose-gotchas.md`.

## How to use

- Load only the rule files matching the file type and task at hand; never
  load the pack "just in case".
- Validate Compose changes with `docker compose config --quiet` and
  layout changes with `git check-ignore -q .log && echo ".log/ is gitignored"`
  before committing.
- After editing anything in this pack, run
  `python3 -m pytest tests/test_s4_2_step1.py`.

<!-- sentinel: specs/docker -->
