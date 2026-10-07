# Rule: Compose gotchas

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
