# Technology Stack Documentation

## Core Technology

- Aider (via `paulgauthier/aider-full:latest`)

## Required Dependencies

### Environment Containerization

- Docker (CLI & Compose Plugin)
  - Purpose: Providing the Dockerized environment for running Aider and allowing Aider to run docker commands.
  - Chosen because: Standard containerization tool required to fulfill REQ-FR-ENV-1 and REQ-FR-ENV-3.

### Launch Scripting

- Bash
  - Purpose: Providing the single `.sh` script to launch the environment, manage container lifecycle, and map local repositories.
  - Chosen because: Standard shell scripting required to fulfill REQ-FR-ENV-2 and REQ-NFR-USAB-1.

### Workflow Orchestration

- AGENT.md (Configuration)
  - Purpose: Orchestrating Aider through the prompt library and enforcing SDLC best practices.
  - Chosen because: Native markdown format supported by Aider to fulfill REQ-FR-WF-2, REQ-FR-WF-3, REQ-FR-TM-1, and REQ-FR-TM-2.

## Compatibility Matrix

| Dependency        | Version | Aider (latest) | Docker | Bash | AGENT.md |
|-------------------|---------|----------------|--------|------|----------|
| Docker            | N/A     | ✓              | -      | ✓    | ✓        |
| Bash              | N/A     | ✓              | ✓      | -    | ✓        |
| AGENT.md          | N/A     | ✓              | ✓      | ✓    | -        |

## Version Lock Rationale

The base image `paulgauthier/aider-full:latest` is used to ensure all Aider dependencies are correctly configured. Docker and Bash versions are provided by the host system and base image respectively.
