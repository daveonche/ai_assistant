# Technology Stack Documentation

## Core Technology

- Aider (via `paulgauthier/aider-full:v0.86.2@sha256:ba4d51b3c846b89d0f261f88dd712b9ce62968d3844c73fe2b3353ae65b11ea4`)

## Required Dependencies

### Environment Containerization

- Docker (CLI & Compose Plugin)
  - Purpose: Providing the Dockerized environment for running Aider and allowing Aider to run docker commands.
  - Chosen because: Standard containerization tool required to fulfill REQ-FR-ENV-1 and REQ-FR-ENV-3.

### Launch Scripting

- Bash
  - Purpose: Providing the single `.sh` script to launch the environment, manage container lifecycle, and map local repositories.
  - Chosen because: Standard shell scripting required to fulfill REQ-FR-ENV-2 and REQ-NFR-USAB-1.

### Launch Runtime

- Python (>=3.8)
  - Purpose: Provide structured language for the ai_assistant.py file used for launching the aider container.
  - Chosen because: Standard runtime required to execute the Python launcher (.agent/ai_assistant.py); version constraint matches `requires-python = ">=3.8"` declared in .agent/pyproject.toml.

### Workflow Orchestration

- AGENT.md (Configuration)
  - Purpose: Orchestrating Aider through the prompt library and enforcing SDLC best practices.
  - Chosen because: Native markdown format supported by Aider to fulfill REQ-FR-WF-2, REQ-FR-WF-3, REQ-FR-TM-1, and REQ-FR-TM-2.

## Compatibility Matrix

| Dependency | Version | Aider (latest) | Docker | Bash | Python | AGENT.md |
|------------|---------|----------------|--------|------|--------|----------|
| Docker     | N/A     | ✓              | -      | ✓    | ✓      | ✓        |
| Bash       | N/A     | ✓              | ✓      | -    | ✓      | ✓        |
| Python     | >=3.8   | ✓              | ✓      | ✓    | -      | ✓        |
| AGENT.md   | N/A     | ✓              | ✓      | ✓    | ✓      | -        |

## Version Lock Rationale

The base image `paulgauthier/aider-full:latest` is used to ensure all Aider dependencies are correctly configured. Docker and Bash versions are provided by the host system and base image respectively. The host system requires Python (>=3.8) to execute the launcher script `.agent/ai_assistant.py`, which uses only the Python standard library; the minimum version matches the `requires-python` constraint declared in `.agent/pyproject.toml`.

### Verified Action Pins

GitHub Actions `uses` references are pinned to full-length commit SHAs and verified against their upstream tags before merge; the verification procedure is documented in "Steps and actions" in `.agent/.aider.conventions/references/ci-cid-best-practices.md`.

| Action | Version | Pinned SHA | Used in |
| :--- | :--- | :--- | :--- |
| `actions/checkout` | v4.2.2 | `11bd71901bbe5b1630ceea73d27597364c9af683` | `.github/workflows/ci.yml` (both jobs) |

Verification record: `git ls-remote https://github.com/actions/checkout.git 'refs/tags/v4.2.2*'` returned exactly one line, so `v4.2.2` is a lightweight tag and the advertised SHA is the commit itself; it matches the pinned value.

### Verified Image Pins

The base image in `.agent/Dockerfile.aider` is pinned to tag + manifest-list digest.

| Image | Tag | Digest (manifest list) | Used in |
| :--- | :--- | :--- | :--- |
| `paulgauthier/aider-full` | `v0.86.2` | `sha256:ba4d51b3c846b89d0f261f88dd712b9ce62968d3844c73fe2b3353ae65b11ea4` | `.agent/Dockerfile.aider` `FROM` |

Verification record: the Docker Hub tags API for `paulgauthier/aider-full:v0.86.2` reported digest `sha256:ba4d51b3c846b89d0f261f88dd712b9ce62968d3844c73fe2b3353ae65b11ea4`, the manifest-list digest covering all architectures, matching the pinned value. (`docker buildx imagetools inspect <ref>` is the equivalent local command when the buildx plugin is installed.)
