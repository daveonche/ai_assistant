# Rule: All commands run in the container

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

`docker compose run` without `--rm` leaves stopped one-off containers
behind.
