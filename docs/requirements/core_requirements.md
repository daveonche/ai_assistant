# Core Requirements for AIAssistant

## Functional Requirements

### Environment Setup

- REQ-FR-ENV-1: The system shall provide a Dockerized environment for running aider.
- REQ-FR-ENV-2: The system shall allow users to launch the environment via a single `.sh` script.
- REQ-FR-ENV-3: The system shall map the Dockerized environment to any local project repository.

### Workflow Orchestration

- REQ-FR-WF-1: The system shall integrate the software-dev-prompt-library.
- REQ-FR-WF-2: The system shall use an AGENT.md file to orchestrate aider through the prompt library.
- REQ-FR-WF-3: The system shall enforce SDLC best practices through the orchestrated workflow.

### Task Management

- REQ-FR-TM-1: The system shall break down complex development tasks into atomic, manageable steps.
- REQ-FR-TM-2: The system shall isolate context for each atomic step to minimize token usage.

## Non-Functional Requirements

### Performance

- REQ-NFR-PERF-1: The system shall minimize API token consumption during AI coding workflows.
- REQ-NFR-PERF-2: The system shall reduce API costs associated with AI coding.

### Usability

- REQ-NFR-USAB-1: The system shall provide a frictionless setup experience, eliminating local dependency conflicts.
