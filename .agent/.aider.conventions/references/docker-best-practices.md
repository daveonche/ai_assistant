# Dockerfile and Build Best Practices

Applies to every `Dockerfile*` in this repository (e.g.,
`.agent/Dockerfile.aider`) and to build configuration such as
`.dockerignore` files. Compiled from the Docker documentation:
[Building best practices](https://docs.docker.com/build/building/best-practices/)
and the [Dockerfile reference](https://docs.docker.com/reference/dockerfile/).

Use these rules as review criteria when creating or reviewing Dockerfiles.

## Image design

- Use multi-stage builds: split instructions into distinct stages so the
  final image contains only the files needed to run the application. Stages
  can also execute build steps in parallel.
- Create reusable stages: when several images share many components, put the
  shared parts in one common stage and build the unique stages `FROM` it.
  Docker builds the common stage once, and maintaining one shared stage is
  easier than keeping several similar stages in sync (don't repeat yourself).
- Choose the right base image: build from a trusted source (look for the
  Docker Official Images, Verified Publisher, or Docker-Sponsored Open
  Source badges on Docker Hub) and keep it small. A minimal base image means
  portability, fast downloads, and a smaller vulnerability surface.
- Use two base image types where applicable: one for building and unit
  testing, a slimmer one for production (no compilers, build systems, or
  debugging tools).
- Create ephemeral containers: containers built from the image should be
  stoppable, destructible, and rebuildable with a minimum of setup and
  configuration (see the *Processes* principle of
  [The Twelve-Factor App](https://12factor.net/processes)).
- Decouple applications: one concern per container, so containers scale
  horizontally and are reusable. One process per container is a rule of
  thumb, not a hard rule. Connect dependent containers with Docker networks.
- Don't install unnecessary packages: skip "nice to have" extras (e.g., a
  text editor in a database image); they add complexity, dependencies, size,
  and build time.

## Base image pinning

- Tags are mutable: a publisher can repoint a tag, so the same tag may
  resolve to a different image over time. For supply-chain integrity and an
  audit trail, pin the digest:

```dockerfile
# syntax=docker/dockerfile:1
FROM alpine:3.21@sha256:a8560b36e8b8210634f77d9f7f9efd7ffa463e380b75e2e74aff4511df3ef88c
```

- Digest pinning trade-offs: updating digests is manual, and automated
  security fixes are opted out. Keep base images current with Dependabot
  (`package-ecosystem: "docker"`) or review updates with
  `docker scout recommendations`.

## Rebuilding and the build cache

- Rebuild images often: images are immutable snapshots. Rebuild regularly
  with updated dependencies to stay up-to-date and secure.
- Leverage the build cache: understand cache invalidation and order
  instructions so steps that change most often come last (see
  [Optimize cache usage](https://docs.docker.com/build/cache/optimize/)).
- Build and test images in CI: on every push or pull request, build, tag,
  and test the image automatically (e.g., GitHub Actions).

| Flag | Effect |
| :--- | :--- |
| `--pull` | Forces a check for and download of a newer base image, even if one is cached locally. |
| `--no-cache` | Disables the build cache and re-fetches dependency versions from package managers; does not refresh the base image. |

- The two flags serve distinct purposes and can be combined for a fresh base
  image plus re-executed build steps:

```bash
docker build --pull --no-cache -t my-image:my-tag .
```

## Build context and hygiene

- Exclude with `.dockerignore`: exclude files not relevant to the build
  without restructuring the repository. Pattern syntax is similar to
  `.gitignore` (e.g., `*.md`).
- Sort multi-line arguments alphanumerically to ease maintenance, avoid
  duplicated packages, and make PRs easier to review. Add a space before
  each line-continuation backslash.

## Dockerfile instructions

### FROM

- Use current official images as the base. Docker recommends the Alpine
  image: tightly controlled, under 6 MB, still a full Linux distribution.

### LABEL

- Use `LABEL` to organize images by project, record licensing, and aid
  automation. Quote strings containing spaces and escape inner quotes:

```dockerfile
LABEL com.example.version="0.0.1-beta"
LABEL com.example.release-date="2015-02-12"
```

- Combining labels into a single instruction (to avoid extra layers) has not
  been necessary since Docker 1.10, but remains supported.

### RUN

- Split long or complex `RUN` statements across lines with backslashes and
  chain commands with `&&` for readability and maintainability:

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    package-bar \
    package-baz \
    package-foo
```

- Use heredocs to run multiple commands without chaining with `&&`:

```dockerfile
RUN <<EOF
apt-get update
apt-get install -y --no-install-recommends \
    package-bar \
    package-baz \
    package-foo
EOF
```

#### apt-get

- Always combine `RUN apt-get update` with `apt-get install` in the same
  `RUN` statement (cache busting). A standalone `apt-get update` layer is
  reused from cache on later builds, so `apt-get install` can get outdated
  packages.
- Pin package versions (e.g., `package-foo=1.3.*`) to force retrieval of a
  known version and reduce failures from unanticipated changes.
- Remove `/var/lib/apt/lists` to reduce image size; the apt cache is not
  stored in a layer. Official Debian and Ubuntu images run `apt-get clean`
  automatically, so explicit invocation is not required.
- Well-formed example:

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    aufs-tools \
    automake \
    build-essential \
    curl \
    dpkg-sig \
    libcap-dev \
    libsqlite3-dev \
    mercurial \
    reprepro \
    ruby1.9.1 \
    ruby1.9.1-dev \
    s3cmd=1.1.* \
    && rm -rf /var/lib/apt/lists/*
```

#### Using pipes

- `RUN` commands run under `/bin/sh -c`, which only evaluates the exit code
  of the last command in a pipe; earlier failures pass unnoticed.
- Prepend `set -o pipefail &&` so an error anywhere in the pipe fails the
  build:

```dockerfile
RUN set -o pipefail && wget -O - https://some.site | wc -l > /number
```

- Not all shells support `-o pipefail` (e.g., `dash` on Debian-based
  images). Use the exec form to pick a shell that does:

```dockerfile
RUN ["/bin/bash", "-c", "set -o pipefail && wget -O - https://some.site | wc -l > /number"]
```

### CMD

- Use the exec-array form to run the image's software:
  `CMD ["executable", "param1", "param2"]` (e.g.,
  `CMD ["apache2", "-DFOREGROUND"]`).
- For tool images, give `CMD` an interactive shell (e.g., `CMD ["python"]`)
  so `docker run -it <image>` drops into a usable shell.
- Avoid `CMD ["param", "param"]` with `ENTRYPOINT` unless you and your users
  already know exactly how `ENTRYPOINT` behaves.

### EXPOSE

- Declare the common, traditional port for the application (`EXPOSE 80` for
  Apache, `EXPOSE 27017` for MongoDB). Users map ports at `docker run` time.

### ENV

- Use `ENV` to extend `PATH`, provide service-specific variables (e.g.,
  `PGDATA`), and define version constants so a version bump is a one-line
  change:

```dockerfile
ENV PG_MAJOR=9.3
ENV PG_VERSION=9.3.4
```

- Each `ENV` line creates an intermediate layer; the value persists even if
  unset in a later layer. Set, use, and unset the variable within a single
  `RUN` layer instead:

```dockerfile
RUN export ADMIN_USER="mark" \
    && echo $ADMIN_USER > ./mark \
    && unset ADMIN_USER
```

### ADD or COPY

- Prefer `COPY` for copying files from the build context or from another
  stage in a multi-stage build.
- Prefer a bind mount over `COPY` when a file is needed only for one `RUN`
  instruction; mounted files do not persist in the final image:

```dockerfile
RUN --mount=type=bind,source=requirements.txt,target=/tmp/requirements.txt \
    pip install --requirement /tmp/requirements.txt
```

- Reserve `ADD` for downloading remote artifacts: it gives more precise
  build caching, supports checksum validation, and parses Git URLs. Use it
  instead of manual `wget` plus `tar`:

```dockerfile
ADD --checksum=sha256:<digest> https://example.com/artifact.tar.gz /artifact.tar.gz
```

- If files from the build context must end up in the final image, use
  `COPY`.

### ENTRYPOINT

- Best use: set the image's main command and let `CMD` supply default flags;
  the image name then doubles as the binary reference
  (`docker run s3cmd ls s3://mybucket`):

```dockerfile
ENTRYPOINT ["s3cmd"]
CMD ["--help"]
```

- When startup needs more than one step, combine `ENTRYPOINT` with a helper
  script. Use the `exec` builtin in the script so the application becomes
  PID 1 and receives Unix signals:

```dockerfile
COPY ./docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["postgres"]
```

### VOLUME

- Use `VOLUME` to expose database storage areas, configuration storage, or
  files and folders created by the container; strongly encouraged for any
  mutable or user-serviceable parts of the image.

### USER

- If the service runs without privileges, create a user and group and switch
  with `USER`:

```dockerfile
RUN groupadd -r postgres && useradd --no-log-init -r -g postgres postgres
```

- Assign an explicit UID/GID when it matters: the "next" UID/GID is assigned
  non-deterministically across image rebuilds.
- Pass `--no-log-init` to `useradd` to avoid disk exhaustion from the
  `faillog` sparse-file bug; the Debian/Ubuntu `adduser` wrapper does not
  support this flag.
- Avoid installing or using `sudo` (unpredictable TTY and signal-forwarding
  behavior); use `gosu` if you need root-then-drop-privileges behavior.
- Avoid switching `USER` back and forth frequently; it adds layers and
  complexity.

### WORKDIR

- Always use absolute paths for `WORKDIR`, and prefer it over proliferating
  `RUN cd … && do-something` instructions, which are hard to read and
  maintain.

### ONBUILD

- `ONBUILD` commands execute in any child image built `FROM` the current
  image, before the child's own commands. Useful for language stack images
  that build arbitrary user software.
- Tag ONBUILD variants separately (e.g., `ruby:1.9-onbuild`).
- Be careful with `ADD` or `COPY` in `ONBUILD`: the child build fails
  catastrophically if its context lacks the resource.

## Syntax essentials

- Start every Dockerfile with the parser directive
  `# syntax=docker/dockerfile:1` to pin the stable BuildKit frontend.
- The default escape character is `\`; change it with the `escape` directive
  when needed.
- Instructions accept shell form (`RUN apt-get update`) and exec form
  (`RUN ["/bin/bash", "-c", "..."]`); exec form bypasses shell interpolation
  and lets you choose the shell.
- Heredocs (`RUN <<EOF … EOF`) hold multi-command blocks without `&&` chains.
- `RUN --mount` (e.g., `type=bind`, `type=from`) mounts files or stages
  temporarily for a single instruction.
