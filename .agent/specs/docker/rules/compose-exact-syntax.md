# Rule: Exact-syntax cheat sheet

Quote values YAML would otherwise parse as numbers or booleans:

```yaml
ports:
  - "8080:80"
restart: "no"
environment:
  ENABLED: "true"
```

## `pull_policy`

| Value | Behavior |
| :--- | :--- |
| `always` | Always pull from the registry. |
| `never` | Never pull; fail if no cached image exists. |
| `missing` | Pull only if not cached; `if_not_present` is an alias. Default when no `build` section is used. The `latest` tag is always pulled. |
| `build` | Build the image; rebuild even if already present. |
| `daily`, `weekly`, `every_<duration>` | Check the registry if the last pull is older than the interval. |

## `depends_on` long syntax

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

## `external: true` and `name`

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
