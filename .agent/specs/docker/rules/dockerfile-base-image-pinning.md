# Rule: Base image digest pinning

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
