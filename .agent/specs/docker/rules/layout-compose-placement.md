# Rule: Compose file placement and bind mounts

- Keep every Compose file at the project root; never nest them under
  `docker/` or per-service directories.
- Bind-mount required directories into services instead of baking them
  into images: `./src` for source code, `./.log` for logs, `./config`
  read-only where needed.
- Relative bind paths must start with `.` or `..` (see
  `compose-gotchas.md` for the full bind-mount rules).
- Mount `.log/` as a whole directory (e.g., at `/app/logs`); never
  bind-mount a single `.log/<name>.log` file (see
  `layout-log-capture.md`).

```yaml
services:
  web:
    build:
      context: ./docker/web
    volumes:
      - ./src:/app/src
      - ./.log:/app/logs
```

- Dev images must not `COPY` `./src`; bind-mount it. `COPY` belongs in
  production-oriented stages (see `dockerfile-modern-syntax.md`).
