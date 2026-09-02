# Compose File Specification Reference

Applies to every Docker Compose file in this repository (`compose.yml`,
`compose.yaml`, `docker-compose.yml`, `docker-compose.yaml`) and to Compose
snippets embedded in documentation or CI configuration. This is a delta
reference: repo routing, exact syntax that YAML and Compose silently
misparse, and validation. It is not a digest of the Compose Specification.

Sources: [Compose file reference](https://docs.docker.com/reference/compose-file.md),
[Version and name](https://docs.docker.com/reference/compose-file/version-and-name.md),
[Services](https://docs.docker.com/reference/compose-file/services.md),
[Networks](https://docs.docker.com/reference/compose-file/networks.md),
[Volumes](https://docs.docker.com/reference/compose-file/volumes.md),
[Configs](https://docs.docker.com/reference/compose-file/configs.md), and
[Secrets](https://docs.docker.com/reference/compose-file/secrets.md).

Use these rules as review criteria when creating or reviewing Compose files.

## Routing

When a Compose snippet appears inside a GitHub Actions workflow or another
CI configuration file, apply
`.agent/.aider.conventions/references/ci-cid-best-practices.md` to the
surrounding CI structure and this reference to the Compose content.

## Version and name

- Do not add top-level `version:` to new files; remove it when editing
  existing ones. It is obsolete, does not select a schema, and produces a
  warning. Compose always validates against the most recent schema.
- Optional top-level `name` sets the project name when none is provided
  via CLI or `COMPOSE_PROJECT_NAME`. The resolved name is available for
  interpolation as `COMPOSE_PROJECT_NAME`.

## Exact-syntax cheat sheet

Quote values YAML would otherwise parse as numbers or booleans:

```yaml
ports:
  - "8080:80"
restart: "no"
environment:
  ENABLED: "true"
```

### `pull_policy`

| Value | Behavior |
| :--- | :--- |
| `always` | Always pull from the registry. |
| `never` | Never pull; fail if no cached image exists. |
| `missing` | Pull only if not cached; `if_not_present` is an alias. Default when no `build` section is used. The `latest` tag is always pulled. |
| `build` | Build the image; rebuild even if already present. |
| `daily`, `weekly`, `every_<duration>` | Check the registry if the last pull is older than the interval. |

### `depends_on` long syntax

```yaml
depends_on:
  db:
    condition: service_healthy
    restart: true
    required: true
```

- Short syntax is a list of service names and does not wait for health.
- `condition`: `service_started`, `service_healthy`, or
  `service_completed_successfully`.
- `restart: true` restarts this service after the dependency is updated.
- `required` defaults to `true`; `false` downgrades a missing dependency
  to a warning.

### `external: true` and `name`

For networks, volumes, and configs, `external: true` means Compose does
not create the resource and errors if it is missing. The only other
attribute allowed is `name`. Any additional attribute makes the file
invalid.

```yaml
volumes:
  data:
    external: true
    name: ${DATA_VOLUME}
```

## Gotchas

- `version` is obsolete: adding it triggers a warning and does not select
  a schema.
- Quote port mappings (`"8080:80"`) and `restart: "no"` — YAML would
  otherwise parse them as numbers or booleans.
- `network_mode` and `networks` cannot both be set.
- `external: true` plus any other attribute except `name` is rejected as
  invalid — for networks, volumes, and configs alike.
- Relative bind paths must start with `.` or `..` and only work on local
  runtimes.
- Short-syntax bind mounts silently create missing host directories; use
  `bind.create_host_path: false` to prevent it.
- Unquoted booleans in `environment` are converted by the YAML parser.
- `environment` beats `env_file`; within `env_file`, the last file in the
  list wins.
- The `com.docker.compose` label prefix is reserved and rejected at
  runtime.
- `container_name` prevents scaling the service beyond one container.
- Feature introduction floors are not hard compatibility constraints.
  Check the Compose changelog before treating a field as required or
  available.
- Secret `uid`/`gid`/`mode` are ignored for `file`-sourced secrets.
- Port mapping with `network_mode: host` is a runtime error.
- `extends` does not import the referenced service's resource
  dependencies, and circular references are errors.
- Services without a shared network cannot communicate and Compose does
  not warn about the configuration mismatch.
- Without a host IP in `ports`, Docker binds `0.0.0.0`, bypassing host
  firewall rules.
- `command` does not run in the image `SHELL`; use
  `command: /bin/sh -c 'echo "hello $$HOSTNAME"'` when shell features are
  needed. Compose interpolates `$`; write `$$` for a container-time `$`.

## Validation

Before committing Compose file changes, verify the file parses and renders
as a valid merged model:

```bash
docker compose config --quiet
```

- Drop `--quiet` to inspect the resolved, merged configuration.
- Re-check every construct listed under Gotchas.
- Confirm `external` resources (networks, volumes, configs) exist on the
  target platform before deployment.
