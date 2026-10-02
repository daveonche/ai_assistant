# Docker Project Layout Reference

Applies to every Docker/Compose-orchestrated project in this repository:
where Compose files live, per-service build contexts, the `.log/` log
directory, and how commands are executed. It composes with
`compose-file-spec.md` (Compose file syntax) and
`docker-best-practices.md` (Dockerfile content); this reference governs
structure and command execution.

Use these rules as review criteria when creating or reviewing a
Docker/Compose project layout, and whenever running any command in such a
project.

## Canonical layout

```text
project-root/
├── compose.yml              # base file — always at the project root
├── compose.override.yml     # local dev overrides (auto-merged)
├── compose.prod.yml         # optional; used via -f
├── .gitignore               # ignores .log/
├── .log/                    # flat log files per service, gitignored
│   ├── web.log
│   ├── web.test.log
│   └── worker.log
├── src/                     # source code, bind-mounted into containers
├── docker/                  # per-service build contexts
│   ├── web/
│   │   ├── Dockerfile
│   │   └── .dockerignore
│   └── worker/
│       ├── Dockerfile
│       └── .dockerignore
├── config/                  # mounted read-only where needed
└── scripts/
```

## Service name is the key

Service names are unique within a Compose project, so the service name in
`compose.yml` is the single identifier tying the structure together — no
per-service subdirectories are needed anywhere. For each service `<name>`:

- build context: `docker/<name>/`, with its own `Dockerfile` and
  `.dockerignore`;
- log files: `.log/<name>.log` plus per-purpose variants such as
  `.log/<name>.test.log` (flat files, created on demand);
- `services:` entry in the root `compose.yml`.

Renaming a service renames the build context with it; the log file needs
no rename because its name is derived from the service at capture time. A
`.log/<name>.log` file without a matching service key is a defect.

## Compose files stay at the project root

- Keep every Compose file at the project root; never nest them under
  `docker/` or per-service directories.
- Bind-mount required directories into services instead of baking them
  into images: `./src` for source code, `./.log` for logs, `./config`
  read-only where needed.
- Relative bind paths must start with `.` or `..`.
- Mount `.log/` as a whole directory (e.g., at `/app/logs`); never
  bind-mount a single `.log/<name>.log` file (see Gotchas).

```yaml
services:
  web:
    build:
      context: ./docker/web
    volumes:
      - ./src:/app/src
      - ./.log:/app/logs
```

## Logging: `.log/<service>.log`

- `.log/` is gitignored. Create the directory once as the invoking user
  (`mkdir -p .log`); per-service files are created on demand by the
  capture commands below. Do not rely on Compose to auto-create `.log/`:
  a missing short-syntax bind-mount host path is created as root on
  Linux, which can block non-root container users from writing.
- Capture a service's output (errors included) into its log file:

```bash
docker compose logs -f --tail=0 <service> >> .log/<service>.log 2>&1
```

- Error-only capture, appending into the same per-service log file:

```bash
docker compose logs <service> 2>&1 | grep -iE 'error|fatal|exception' >> .log/<service>.log
```

  Use a distinct `.log/<service>.errors.log` instead if error-only lines
  must not interleave with the full log.
- Apps that write their own log files write them into the mounted `.log/`
  directory as `/app/logs/<service>.log` — one file per service, matching
  the host layout.

## All commands run in the container

Never run project commands (tests, linters, formatters, builds, one-off
scripts, dependency installs) on the host. Always execute them through
Compose inside the service container:

```bash
docker compose run --rm <service> <command>   # one-off: tests, migrations, codegen
docker compose exec <service> <command>       # inside an already-running service
```

- `run --rm` is the default for one-off commands; it removes the
  container afterwards.
- `run` does not publish service ports unless `--service-ports` is
  passed; add it when the command needs the mapped ports.
- `run` starts the service's `depends_on` dependencies unless
  `--no-deps` is passed; prefer `exec` (or `--no-deps`) against an
  already-running stack.
- The host needs only Docker, Compose, and git; every other tool lives in
  the images.

## Test output: minimal for chat, full to `.log/`

Failed-test output is pasted into the chat for debugging, so it must
stay small enough to paste directly. Run tests quiet, colorless, and
with short tracebacks; save the full run to `.log/` and surface only
the failure summary:

```bash
docker compose run --rm -e NO_COLOR=1 <service> \
    python -m pytest -q --tb=short --no-header \
    > .log/<service>.test.log 2>&1
grep -E '^(FAILED|ERROR)' .log/<service>.test.log
```

- Prefer quiet flags and short tracebacks (`-q --tb=short --no-header`
  for pytest; the framework's equivalents elsewhere). When iterating on
  a single failure, add `-x --maxfail=1`; use `--tb=line` when even
  short tracebacks are more than needed.
- Always disable color (`NO_COLOR=1` or the framework's flag): ANSI
  escape sequences bloat pasted output and add noise.
- Full output belongs in `.log/<service>.test.log` (same flat,
  gitignored `.log/` rule). Paste only the failure lines into the chat:
  failing test IDs plus their assertion messages — the few lines the
  LLM needs to start debugging.
- Need more context? Slice the saved log (`grep -n`, `tail -n 40`) and
  paste the slice. Never re-run the suite verbose to "see more", and
  never paste whole logs.
- The same discipline applies to any verbose in-container command
  (builds, migrations): redirect full output to `.log/` and paste only
  the error lines.

## Gotchas

- Never bind-mount a single log file
  (`./.log/web.log:/app/logs/web.log`): if the host file does not exist
  yet, Docker creates a *directory* at that path, and editors that
  save-by-rename break single-file mounts. Mount `.log/` as a whole.
- A service renamed in `compose.yml` but not on disk orphans
  `docker/<name>/`; rename the build context together with the service.
- Forgetting `2>&1` drops stderr from the captured log file.
- `docker compose run` without `--rm` leaves stopped one-off containers
  behind.
- Dev images must not `COPY` `./src`; bind-mount it. `COPY` belongs in
  production-oriented stages (see `docker-best-practices.md`).

## Validation

Before committing layout changes:

```bash
docker compose config --quiet
git check-ignore -q .log && echo ".log/ is gitignored"
```

- Every service with a `build:` section has a
  `docker/<service>/Dockerfile`.
- `.log/` contains only flat files named after existing services
  (`<service>.log`, `<service>.test.log`, …); no per-service
  subdirectories.
- No Compose file exists outside the project root.
