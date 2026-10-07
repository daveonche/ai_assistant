# Rule: Canonical layout

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

A service renamed in `compose.yml` but not on disk orphans
`docker/<name>/`; rename the build context together with the service.

## Validation

Before committing layout changes:

```bash
git check-ignore -q .log && echo ".log/ is gitignored"
```

- Every service with a `build:` section has a
  `docker/<service>/Dockerfile`.
- `.log/` contains only flat files named after existing services
  (`<service>.log`, `<service>.test.log`, …); no per-service
  subdirectories.
- No Compose file exists outside the project root.
