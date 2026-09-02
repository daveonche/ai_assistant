# Dockerfile and Build Best Practices

Applies to every `Dockerfile*` in this repository (e.g.,
`.agent/Dockerfile.aider`) and to build configuration such as
`.dockerignore` files.

This is a delta reference: it records only repo-relevant rules and
easily-got-wrong details. General Dockerfile guidance (multi-stage builds,
instruction semantics, cache ordering, apt-get mechanics, one concern per
container) is assumed knowledge; consult the Docker documentation
([Building best practices](https://docs.docker.com/build/building/best-practices/),
[Dockerfile reference](https://docs.docker.com/reference/dockerfile/)) when
needed.

Use these rules as review criteria when creating or reviewing Dockerfiles.

## Parser directive

- Start every Dockerfile with `# syntax=docker/dockerfile:1` to pin the
  stable BuildKit frontend. Newer syntax (e.g., `ADD --checksum`) fails on
  older frontends, so snippets must carry the directive too.

```dockerfile
# syntax=docker/dockerfile:1
FROM alpine:3.21
```

## Base image digest pinning

- Tags are mutable: a publisher can repoint a tag, so the same tag may
  resolve to a different image over time. Pin the digest for supply-chain
  integrity and an audit trail. The digest below is illustrative; resolve
  the current one before pinning, e.g. with
  `docker buildx imagetools inspect alpine:3.21`:

```dockerfile
# syntax=docker/dockerfile:1
FROM alpine:3.21@sha256:a8560b36e8b8210634f77d9f7f9efd7ffa463e380b75e2e74aff4511df3ef88c
```

- Digest pinning trade-offs: updating digests is manual, and automated
  security fixes are opted out. Keep base images current with Dependabot
  (`package-ecosystem: "docker"`) or review updates with
  `docker scout recommendations`.

## Rebuild flags: `--pull` vs `--no-cache`

These flags are commonly confused: `--pull` refreshes the base image,
`--no-cache` re-executes build steps. Combine them for a fresh base image
plus re-run steps.

| Flag | Effect |
| :--- | :--- |
| `--pull` | Forces a check for and download of a newer base image, even if one is cached locally. |
| `--no-cache` | Disables the build cache and re-fetches dependency versions from package managers; does not refresh the base image. |

```bash
docker build --pull --no-cache -t my-image:my-tag .
```

## Prefer modern syntax

- Heredocs over `&&` chains for multi-command `RUN`:

```dockerfile
# syntax=docker/dockerfile:1
RUN <<EOF
apt-get update
apt-get install -y --no-install-recommends package-foo
EOF
```

- Bind mounts over `COPY` when a file is needed for a single `RUN` only;
  mounted files do not persist in the final image:

```dockerfile
RUN --mount=type=bind,source=requirements.txt,target=/tmp/requirements.txt \
    pip install --requirement /tmp/requirements.txt
```

- `ADD --checksum` over manual `wget` plus `tar` for remote artifacts:

```dockerfile
ADD --checksum=sha256:<digest> https://example.com/artifact.tar.gz /artifact.tar.gz
```

## Build hygiene

- Sort multi-line arguments alphanumerically to ease maintenance, avoid
  duplicated packages, and make PRs easier to review. Add a space before
  each line-continuation backslash.
- Exclude build-irrelevant files with `.dockerignore` (pattern syntax
  similar to `.gitignore`).
