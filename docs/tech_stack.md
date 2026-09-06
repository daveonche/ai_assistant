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

The base image is pinned to tag + manifest-list digest: `paulgauthier/aider-full:v0.86.2@sha256:ba4d51b3c846b89d0f261f88dd712b9ce62968d3844c73fe2b3353ae65b11ea4`. `v0.86.2` is the newest stable release tag; mutable references (`latest`, `dev`, `main`) are deliberately avoided so all Aider dependencies are correctly configured and builds are reproducible. Docker and Bash versions are provided by the host system and base image respectively. The host system requires Python (>=3.8) to execute the launcher script `.agent/ai_assistant.py`, which uses only the Python standard library; the minimum version matches the `requires-python` constraint declared in `.agent/pyproject.toml`.

### Verified Action Pins

GitHub Actions `uses` references are pinned to full-length commit SHAs and verified against their upstream tags before merge; the verification procedure is documented in "SHA pinning verification" in `.agent/.aider.conventions/references/ci-cd-best-practices.md`.

| Action | Version | Pinned SHA | Used in |
| :--- | :--- | :--- | :--- |
| `actions/checkout` | v6.1.0 | `d23441a48e516b6c34aea4fa41551a30e30af803` | `.github/workflows/ci.yml` (both jobs) |

Verification record: `git ls-remote https://github.com/actions/checkout.git 'refs/tags/v6*'` returned single-line (lightweight) entries for `v6`, `v6-beta`, `v6.0.0`, `v6.0.1`, `v6.0.2`, and `v6.1.0`, plus an annotated `v6.0.3` with a second line ending in `^{}` (commit `df4cb1c069e1874edd31b4311f1884172cec0e10`). The pinned `v6.1.0` is a lightweight tag, so the advertised SHA is the commit itself: `d23441a48e516b6c34aea4fa41551a30e30af803`; the floating `refs/tags/v6` advertises the same SHA, confirming `v6.1.0` is the newest release on the major line. The previous pin (`v4.2.2` @ `11bd71901bbe5b1630ceea73d27597364c9af683`) targets the deprecated Node.js 20 runtime and was forced onto Node.js 24 by runners; `v6.1.0` targets Node.js 24 natively.

### Verified Image Pins

The base image in `.agent/Dockerfile.aider` is pinned to tag + manifest-list digest.

| Image | Tag | Digest (manifest list) | Used in |
| :--- | :--- | :--- | :--- |
| `paulgauthier/aider-full` | `v0.86.2` | `sha256:ba4d51b3c846b89d0f261f88dd712b9ce62968d3844c73fe2b3353ae65b11ea4` | `.agent/Dockerfile.aider` `FROM` |

Verification record: the Docker Hub tags API for `paulgauthier/aider-full:v0.86.2` reported digest `sha256:ba4d51b3c846b89d0f261f88dd712b9ce62968d3844c73fe2b3353ae65b11ea4`, the manifest-list digest covering all architectures, matching the pinned value. (`docker buildx imagetools inspect <ref>` is the equivalent local command when the buildx plugin is installed.)
