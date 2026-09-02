# Compose File Specification Reference

Applies to every Docker Compose file in this repository (`compose.yml`,
`compose.yaml`, `docker-compose.yml`, `docker-compose.yaml`) and to Compose
snippets embedded in documentation or CI configuration. Compiled from the
Docker Compose Specification documentation:
[Compose file reference](https://docs.docker.com/reference/compose-file.md),
[Version and name](https://docs.docker.com/reference/compose-file/version-and-name.md),
[Services](https://docs.docker.com/reference/compose-file/services.md),
[Networks](https://docs.docker.com/reference/compose-file/networks.md),
[Volumes](https://docs.docker.com/reference/compose-file/volumes.md),
[Configs](https://docs.docker.com/reference/compose-file/configs.md), and
[Secrets](https://docs.docker.com/reference/compose-file/secrets.md).

Use these rules as review criteria when creating or reviewing Compose files.

Routing note: when a Compose snippet appears inside a GitHub Actions
workflow or another CI configuration file, apply
`.agent/.aider.conventions/references/ci-cid-best-practices.md` to the
surrounding CI structure and this reference to the Compose content.

## Overview

- The Compose Specification is the current, recommended Compose file
  format; legacy `version:` 2.x/3.x schemes were merged into it.
- It is implemented by Compose v2 (the current Go CLI) and by the legacy
  Python Compose v1 from 1.27.0 onward; treat v2 as the reference
  implementation.
- A Compose file defines `services` (required) plus optional top-level
  elements (`networks`, `volumes`, `configs`, `secrets`, …).
  Implementations ignore optional sub-specifications they do not support
  (Build, Deploy, Develop) and the file remains valid.

## Version and name top-level elements

### `version` (obsolete)

- Informative only, kept for backward compatibility: Compose always
  validates the file against the most recent schema, regardless of the
  `version` field. Using it produces an "obsolete" warning — do not add
  it to new files; remove it when editing existing ones.
- Fields unknown to the implementation (typically from a newer
  Specification) produce a warning.

### `name`

- Optional top-level `name` sets the project name used when none is
  provided through another mechanism (CLI flag, `COMPOSE_PROJECT_NAME`);
  the resolved name is exposed for interpolation as
  `COMPOSE_PROJECT_NAME`.

## Services

- `services` is the required top-level element: a map whose keys are
  service names and whose values are service definitions.
- A service definition is applied identically to every container of the
  service.
- Each service may include a `build` section (Compose Build Specification)
  and a `deploy` section (Compose Deploy Specification).

### Images, build, and pulls

- `image`: the source image, in OCI addressable format
  `[<registry>/][<project>/]<image>[:<tag>|@<digest>]`. May be omitted only
  when a `build` section is declared.
- `build`: build configuration per the Compose Build Specification; ignored
  by implementations without build support.
- `pull_policy`: decides when Compose pulls the image.

| Value | Behavior |
| :--- | :--- |
| `always` | Always pull from the registry. |
| `never` | Never pull; fail if no cached image exists. |
| `missing` | Pull only if not cached; `if_not_present` is an alias. Default when no `build` section is used. The `latest` tag is always pulled. |
| `build` | Build the image; rebuild even if already present. |
| `daily`, `weekly`, `every_<duration>` | Check the registry if the last pull is older than the interval. |

- `platform`: target platform in `os[/arch[/variant]]` syntax conforming to
  the OCI Image Spec (e.g. `linux/arm64/v8`).

### Commands and entrypoint

- `command` overrides the image's default command (Dockerfile `CMD`).
- `entrypoint` overrides the image's `ENTRYPOINT`; when non-null, any
  default command from the image is ignored.
- For both: `null` keeps the image default; `[]` or `''` overrides it to
  be empty.
- `command` does not run inside the image's `SHELL` context; run a shell
  explicitly when shell features are needed:
  `command: /bin/sh -c 'echo "hello $$HOSTNAME"'`
- `working_dir` overrides the image's working directory (Dockerfile
  `WORKDIR`).

### Environment, files, and labels

- `environment` sets container environment variables as a map or array. A
  key with no value defers resolution to the runtime; unresolved keys are
  removed from the container environment.
- Quote booleans (`"true"`, `"false"`, `"yes"`, `"no"`) so the YAML parser
  does not convert them.
- `env_file` loads variables from one or more files. Relative paths resolve
  from the Compose file's parent folder; Compose warns on absolute paths.
  Files in a list are processed top down and the last file wins for
  duplicate keys.
- `env_file` list items may be mappings: `required` (default `true`;
  `false` silently ignores a missing file) and `format` (e.g. `raw` to pass
  values through without interpolation).
- `environment` values always override `env_file` values, even when empty
  or undefined.
- `.env` file format: one `VAR[=[VAL]]` per line, `=` or `:` delimiter;
  `#` comments; inline comments on unquoted values need a preceding space;
  single-quoted values are literal; double-quoted values support
  interpolation and `\n`, `\r`, `\t`, `\\`; escape quotes with `\`.
- `labels` (map or array) adds metadata; `label_file` loads labels from
  key-value files (last file wins). `labels` takes precedence over
  `label_file`. Use reverse-DNS notation; the `com.docker.compose` prefix
  is reserved and rejected at runtime.

### Networking

- `networks` (service attribute) attaches the service to networks declared
  under the top-level `networks` element.
- If `networks` is absent, the service joins the implicit `default`
  network. To disable networking entirely, set `network_mode: none`.
- `network_mode` and `networks` are mutually exclusive; Compose rejects a
  file containing both. Values: `bridge` (no service-name DNS resolution),
  `none`, `host`, `service:{name}`, `container:{name}`.
- Per-network long-syntax settings include `aliases`,
  `ipv4_address`/`ipv6_address` (static IPs; the network's `ipam` subnets
  must cover them), `mac_address`, `interface_name`, `driver_opts`,
  `gw_priority`, `priority`, and `link_local_ips`.
- `ports` publishes host/container port mappings. Port mapping must not be
  used with `network_mode: host` (runtime error).
- Short syntax: `[HOST:]CONTAINER[/PROTOCOL]`. Always quote the string to
  avoid YAML base-60 float parsing. Without a host IP, Docker binds to all
  interfaces (`0.0.0.0`), bypassing host firewall rules.
- `expose` declares internal ports as `<portnum>/[<proto>]` (ranges
  allowed) for linked services; they are not published to the host.
  Dockerfile `EXPOSE` ports are reachable on the network regardless.
- `links` is legacy: services on a shared network are already reachable by
  service name. Links also express an implicit startup dependency.
- `extra_hosts` adds `/etc/hosts` entries: short syntax strings
  `HOSTNAME=IP` (`:` separator supported since Compose 2.24.1) or a
  hostname-to-IP map.

### Storage

- `volumes` (service attribute) mounts named volumes, host paths (binds),
  `tmpfs`, `npipe`, or `image` mounts into the container.
- Long-syntax mount `type`: `volume`, `bind`, `tmpfs`, `npipe`, `image`,
  or `cluster`.
- Declare a named volume under the top-level `volumes` element to reuse it
  across services; a host path used by a single service may be declared
  inline.
- Short syntax: `VOLUME:CONTAINER_PATH[:ACCESS_MODE]` with access modes
  `rw` (default), `ro`, `z` (SELinux shared), `Z` (SELinux private;
  ignored on platforms without SELinux).
- Relative host paths are local-runtime only and must begin with `.` or
  `..` to avoid ambiguity with named volumes.
- Short-syntax bind mounts create a missing host directory by default;
  prevent this with long syntax `bind.create_host_path: false`.
- Long syntax extras: `read_only`; `bind.propagation`, `bind.selinux`;
  `volume.nocopy`, `volume.subpath`; `tmpfs.size`, `tmpfs.mode`;
  `image.subpath` (Compose 2.35.0+); `consistency` (platform-specific).
- `volumes_from` mounts all volumes of another service or of a
  `container:<name>`; optional `ro`/`rw` (default `rw`).
- `tmpfs` mounts a temporary filesystem as `path` or `path:options` with
  options `mode`, `uid`, `gid`.
- `read_only` creates the container with a read-only filesystem.
- `shm_size` sets the shared-memory size (`/dev/shm` on Linux).

### Configs and secrets (service grant)

- Defining a config or secret at top level grants nothing; access is
  granted per service with the `configs` / `secrets` attributes.
- Short syntax: name only. Configs mount at `/<config-name>` (Linux,
  `C:\<config-name>` on Windows); secrets mount read-only at
  `/run/secrets/<secret_name>`.
- Long syntax: `source`, `target`, `uid`, `gid`, `mode` (octal; default
  world-readable `0444`; the writable bit is ignored, the executable bit
  may be set).
- Compose errors if the referenced config or secret is neither defined in
  the top-level element nor present on the platform.
- Secret `uid`/`gid`/`mode` are honored only for `environment`-sourced
  secrets; `file`-sourced secrets are bind-mounted and the attributes are
  silently ignored.

### Dependencies and lifecycle

- `depends_on` controls startup and shutdown ordering.
- Short syntax: list of service names. Services are created, started, and
  removed in dependency order; health is not awaited.
- Long syntax per dependency: `condition` (`service_started`,
  `service_healthy`, `service_completed_successfully`), `restart: true`
  (restart this service after the dependency is updated; Compose 2.17.0+),
  and `required` (default `true`; `false` downgrades a missing dependency
  to a warning; Compose 2.20.0+).
- `restart` policy on termination: `no` (default; quote it in YAML),
  `always`, `on-failure[:max-retries]`, `unless-stopped`.
- `stop_signal` (default `SIGTERM`) and `stop_grace_period` (default
  `10s`) control shutdown timing and signaling.
- Lifecycle hooks (Compose 2.30.0+ for `post_start`/`pre_stop`;
  `pre_start` is a recent Compose 2.3x addition):
  - `post_start` / `pre_stop`: commands run inside the service container
    (`command` required; `user`, `privileged`, `working_dir`,
    `environment`). `post_start` timing is not guaranteed; `pre_stop`
    hooks do not run after an unexpected stop.
  - `pre_start`: ephemeral init containers that run to completion, in
    declared order, before the service container starts; a non-zero exit
    fails bring-up. Steps run after `depends_on` conditions are satisfied,
    join the service's networks, and share named/bind mounts. Successful
    steps are not re-run until their definition changes, they fail, or the
    service is recreated. `per_replica` runs a step once for the whole
    service rather than per replica (shared mounts only).

### Resource limits

- Service-level limits (`cpus`, `mem_limit`, `mem_reservation`,
  `pids_limit`, `scale`, `ulimits`, `blkio_config`, …) mirror their
  Deploy Specification equivalents; when both are set, values must be
  consistent.
- `memswap_limit`: total memory plus swap; `0` is ignored; equal to
  `mem_limit` means no swap; unset means swap up to `mem_limit`; `-1`
  means unlimited swap.

### Healthcheck and runtime behavior

- `healthcheck` mirrors the Dockerfile `HEALTHCHECK` instruction. `test`
  accepts a list whose first item is `NONE`, `CMD`, or `CMD-SHELL`, or a
  string (equivalent to `CMD-SHELL`). Durations: `interval`, `timeout`,
  `start_period`, `start_interval`. `disable: true` and `NONE` turn the
  check off.
- `privileged` runs the container with elevated privileges.
- `user` overrides the container user (image `USER`, otherwise root);
  `group_add` adds supplementary groups by name or number.
- `cap_add` / `cap_drop` add or drop Linux capabilities as strings (e.g.
  `ALL`, `NET_ADMIN`, `SYS_ADMIN`).
- `init: true` runs an init process as PID 1 (signal forwarding, reaping).
- Isolation knobs: `ipc` (`shareable` or `service:{name}`), `pid`, `uts`
  (`host`), `userns_mode`, `cgroup` (`host` or `private`),
  `cgroup_parent`, `device_cgroup_rules`, `devices` (also CDI syntax such
  as `vendor1.com/device=gpu`), `isolation`, `runtime` (default `runc`),
  `security_opt`, `sysctls` (namespaced kernel parameters only),
  `storage_opt`.
- `tty` and `stdin_open` allocate a TTY / open stdin (as `-t` / `-i`).
- `container_name` pins a custom container name matching
  `[a-zA-Z0-9][a-zA-Z0-9_.-]+`; the service cannot then be scaled beyond
  one container.
- `logging` sets the log `driver` and driver-specific `options`.
- `annotations` adds container annotations (map or array); `attach: false`
  stops Compose from collecting service logs (default `true`).
- `profiles` lists profiles that must be activated to start the service;
  unassigned services always start. Pattern:
  `[a-zA-Z0-9][a-zA-Z0-9_.-]+`.
- `provider` (Compose 2.29.0+) delegates the service lifecycle to an
  external component (`type` required; `options` provider-specific and
  unvalidated).
- `models` (recent Compose 2.3x addition) attaches AI model references
  (short syntax or long syntax with `endpoint_var` / `model_var`); Compose
  injects connection environment variables.
- `gpus` (Compose 2.30.0+) allocates GPU devices (list of `driver`/`count`
  or `gpus: all`).
- `credential_spec` for Windows gMSA: `file://<filename>`,
  `registry://<value-name>`, or a `config` reference.
- `use_api_socket` (recent Compose 2.3x addition) mounts engine credentials
  so the container can act as a delegate for engine commands (e.g. `pull`,
  `push`).

### `extends`

- Shares common service configuration across files; value is a mapping
  with required `service` and optional `file` (relative to the main
  Compose file, or absolute).
- Not supported with `docker stack deploy`; circular references are
  errors.
- The referenced service's resource dependencies (`volumes`, `networks`,
  `configs`, `secrets`, `links`, `volumes_from`, `depends_on`, and
  `service:{name}` namespace references) are NOT imported; declare them
  explicitly in the extending model.
- `healthcheck` exception: the main mapping cannot specify
  `disable: true` unless the referenced mapping also does (error
  otherwise).

## Networks

- By default Compose creates a single `default` network; every service
  container joins it and is reachable and discoverable by service name.
- Grant services access with the service `networks` attribute; define
  shared networks under the top-level `networks` element. The implicit
  `default` network can be customized with an explicit declaration
  (custom `name`, `driver_opts`, and other attributes).
- `driver`: network driver; Compose errors if unavailable on the platform.
- `attachable: true`: standalone containers may attach to the network and
  communicate with services on it.
- `enable_ipv4: false` / `enable_ipv6: true`: control address assignment
  (`enable_ipv4` is a recent Compose 2.3x addition).
- `internal: true`: externally isolated network (Compose provides external
  connectivity by default).
- `external: true`: the network's lifecycle is managed outside the
  application; Compose does not create it and errors if missing. All
  attributes apart from `name` are irrelevant; any other attribute makes
  the file invalid.
- `ipam`: custom IPAM configuration with optional `driver`, `config` (list
  of `subnet`, `ip_range`, `gateway`, `aux_addresses`), and `options`.
- `name`: custom network name, used as is (not project-scoped); combinable
  with `external` and interpolation for runtime lookup.

## Volumes

- Named volumes are persistent data stores managed by the container
  engine; declare them under the top-level `volumes` element and grant
  per-service access with the service `volumes` attribute.
- `docker compose up` creates a missing volume; an existing volume is
  reused, and recreated if manually deleted outside Compose.
- `driver`: volume driver; Compose errors if unavailable. An empty entry
  uses the engine's default configuration.
- `driver_opts`: driver-dependent options; the local driver supports a
  bind-mount pattern (`type: none`, `o: bind`, `device:` absolute host
  path) mapping a stable volume name to a host path — the device path
  must already exist.

- `external: true`: the volume already exists on the platform; Compose
  does not create it and errors if missing. All attributes apart from
  `name` are irrelevant; any other attribute makes the file invalid.
- `labels` apply to named volumes only (visible via
  `docker volume inspect`), not to bind mounts, and do not change mount
  semantics.
- `name`: custom volume name, used as is (not project-scoped); may be
  interpolated and combined with `external`.

## Configs

- Configs mount as files, defaulting to `/<config-name>` in Linux
  containers and `C:\<config-name>` in Windows containers; owned by the
  container user and world-readable (`0444`) unless overridden per
  service. Grant per-service access with the service `configs` attribute.
- Sources for a top-level config:

| Source | Behavior |
| :--- | :--- |
| `file` | Created from the contents of the file at the given path. |
| `environment` | Created from the value of a host environment variable (Compose 2.23.1+). |
| `content` | Created from the inlined value, with interpolation (Compose 2.23.1+). |
| `external` | Already exists on the platform; not created; error if missing. |
| `name` | Platform lookup name, used as is (not project-scoped); usable with `external`. |

- With `external: true`, all attributes apart from `name` are irrelevant;
  any other attribute makes the file invalid.

## Secrets

- Secrets are a flavor of configs focused on sensitive data; grant
  per-service access with the service `secrets` attribute.
- Sources: `file` (contents of the file at the given path) and
  `environment` (value of a host environment variable).
- `environment` secrets are not supported when deploying with
  `docker stack deploy`; use `file` or `external` instead.

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
- Version annotations here reflect the Compose release that introduced a
  feature; items marked "recent Compose 2.3x addition" do not pin an
  exact release. Verify exact floors against the Compose changelog
  before using them as hard compatibility constraints.
- Secret `uid`/`gid`/`mode` are ignored for `file`-sourced secrets.
- Port mapping with `network_mode: host` is a runtime error.
- `extends` does not import the referenced service's resource
  dependencies, and circular references are errors.
- Services without a shared network cannot communicate and Compose does
  not warn about the configuration mismatch.
- Without a host IP in `ports`, Docker binds `0.0.0.0`, bypassing host
  firewall rules.

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
