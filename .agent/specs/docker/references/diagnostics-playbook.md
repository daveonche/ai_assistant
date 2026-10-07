# Diagnostics Playbook

Symptom → root cause → solution patterns for Docker and Compose problems
in this repository. Narrative reference: consult it after the
exact-syntax rules in `rules/` have been applied and the problem
persists.

## Build performance

- **Symptoms:** Slow builds (10+ minutes), frequent cache invalidation.
- **Root causes:** Poor layer ordering, large build context, no caching
  strategy.
- **Solutions:** Multi-stage builds, `.dockerignore` optimization,
  dependency caching (see `rules/dockerfile-modern-syntax.md`).

## Security vulnerabilities

- **Symptoms:** Security scan failures, exposed secrets, root execution.
- **Root causes:** Outdated base images, hardcoded secrets, default
  user.
- **Solutions:** Regular base updates, secrets management (see
  `rules/dockerfile-secrets.md`), non-root configuration, digest pinning
  (see `rules/dockerfile-base-image-pinning.md`).

## Image size

- **Symptoms:** Images over 1GB, deployment slowness.
- **Root causes:** Unnecessary files, build tools in production, poor
  base selection.
- **Solutions:** Distroless images, multi-stage optimization, selective
  artifact copying.

## Networking

- **Symptoms:** Service communication failures, DNS resolution errors.
- **Root causes:** Missing networks, port conflicts, service naming.
- **Solutions:** Custom networks, health checks, proper service
  discovery (see `rules/compose-exact-syntax.md`).

## Development workflow

- **Symptoms:** Hot reload failures, debugging difficulties, slow
  iteration.
- **Root causes:** Volume mounting issues, port configuration,
  environment mismatch.
- **Solutions:** Development-specific targets, proper volume strategy,
  debug configuration.
