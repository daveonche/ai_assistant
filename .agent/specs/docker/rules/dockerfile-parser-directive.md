# Rule: Parser directive

- Start every Dockerfile with `# syntax=docker/dockerfile:1` to pin the
  stable BuildKit frontend. Newer syntax (e.g., `ADD --checksum`) fails on
  older frontends, so snippets must carry the directive too.

```dockerfile
# syntax=docker/dockerfile:1
FROM alpine:3.21
```
