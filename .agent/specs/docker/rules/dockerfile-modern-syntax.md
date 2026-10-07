# Rule: Prefer modern syntax

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
