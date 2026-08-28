# Core Requirements for AIAssistant

## Functional Requirements

### Environment Setup

- REQ-FR-ENV-1: The system shall provide a Dockerized environment for running aider.
- REQ-FR-ENV-2: The system shall allow users to launch the environment via a single .sh script.
- REQ-FR-ENV-3: The system shall support use within other projects to provide SDLC workflows by copying the core configuration files into the project root as defined in the README.md setup guide.
- REQ-FR-ENV-4: The system shall mount the project root, including all files and subdirectories, into the Docker container to give the AI full access to that specific project.
- REQ-FR-ENV-5: The system shall support standalone use by cloning the repository, changing into the cloned directory, and executing the agent.sh script to start the assistant.

### Workflow Orchestration

- REQ-FR-WF-1: The system shall include a project-specific SDLC prompt library tailored to the project's goals.
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
