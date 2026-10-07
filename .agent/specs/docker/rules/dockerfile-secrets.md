# Rule: Secrets

- Never pass secrets through `ENV` or hard-coded instructions: `ENV`
  values persist in the image config and are visible via
  `docker inspect` and `docker history`.
- Avoid secret-bearing build args: Docker warns their values are visible
  to any user of the image via `docker history`.
- Inject build-time secrets with a BuildKit secret mount; the mounted
  value never enters an image layer:

```dockerfile
# syntax=docker/dockerfile:1
RUN --mount=type=secret,id=api_key \
    API_KEY="$(cat /run/secrets/api_key)" && ./build.sh
```

- Prefer runtime secrets over build-time ones. At runtime, use Compose
  `secrets:` (file- or external-sourced) instead of environment
  variables; note that `uid`/`gid`/`mode` are ignored for `file`-sourced
  secrets.
