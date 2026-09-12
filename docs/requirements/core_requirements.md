# Core Requirements for AIAssistant

## Functional Requirements

### Environment Setup

- REQ-1: The system shall provide a Dockerized environment for running aider.
- REQ-2: The system shall allow users to launch the environment via a single .sh script.
- REQ-3: The system shall support use within other projects to provide SDLC workflows by installing the core configuration files and root launcher into the project root via any documented method (manual copy or one-command installer), as defined in the README.md setup guide.
- REQ-4: The system shall mount the project root, including all files and subdirectories, into the Docker container to give the AI full access to that specific project.
- REQ-5: The system shall support standalone use by cloning the repository, changing into the cloned directory, and executing the agent.sh script to start the assistant.
- REQ-6: The system shall support refreshing an existing install in a consumer project from the pinned release reference through the project's own git, recording the refresh as a single reviewable, revertable project commit scoped to the assistant files, as defined in the README.md setup guide.

### Workflow Orchestration

- REQ-7: The system shall include a project-specific SDLC prompt library tailored to the project's goals.
- REQ-8: The system shall use an AGENT.md file to orchestrate aider through the prompt library.
- REQ-9: The system shall enforce SDLC best practices through the orchestrated workflow.

### Task Management

- REQ-10: The system shall break down complex development tasks into atomic, manageable steps.
- REQ-11: The system shall isolate context for each atomic step to minimize token usage.

## Non-Functional Requirements

### Performance

- REQ-12: The system shall minimize API token consumption during AI coding workflows.
- REQ-13: The system shall reduce API costs associated with AI coding.

### Usability

- REQ-14: The system shall provide a frictionless setup experience, eliminating local dependency conflicts.
