# Scaffolding Sprint Stories

## Story S1.1: Initial Project Creation and Configuration

As a developer, I want to set up the basic project structure with core dependencies so that we have a working development environment.

Acceptance Criteria:

- Project directory is created with standard structure (e.g., `src/`, `docs/`, `scripts/`)
- Git repository is initialized
- `.gitignore` is configured for standard development files
- Basic `README.md` is created

Dependencies: None

Developer Notes:

- Use standard git initialization tools
- Follow team's agreed-upon project structure

## Story S1.2: Docker Environment Setup

As a developer, I want to create a Dockerfile and docker-compose configuration so that Aider can run in an isolated, containerized environment.

Acceptance Criteria:

- `Dockerfile.aider` is created using `paulgauthier/aider-full:latest` as the base image
- `docker-compose.yml` is configured to build and run the container
- Volume mappings are configured to map local repositories into the container
- Container builds and runs successfully

Dependencies: S1.1

Developer Notes:

- Ensure Docker Compose plugin is utilized
- Map local repository to a standard path inside the container (e.g., `/app`)

## Story S1.3: Bash Launch Script Implementation

As a developer, I want to create a Bash script to launch the Dockerized environment so that I can start the AI assistant with a single command.

Acceptance Criteria:

- `ai-assistant.sh` is created and made executable
- Script accepts local repository paths and configuration flags
- Script handles Docker container lifecycle (build, run, stop)
- Script successfully launches the Aider environment inside the container

Dependencies: S1.2

Developer Notes:

- Use standard Bash scripting practices
- Ensure error handling via exit codes

## Story S1.4: Aider Configuration and AGENT.md Setup

As a developer, I want to configure Aider and create an AGENT.md file so that the workflow is orchestrated according to SDLC best practices.

Acceptance Criteria:

- `.aider.conf.yml` is created with necessary Aider settings
- `.aider.model.settings.yml` is configured for model usage
- `.aiderignore` is set up to exclude unnecessary files from Aider's context
- `AGENT.md` is created with context management rules (`/read-only`, `/drop`) and workflow instructions

Dependencies: S1.2, S1.3

Developer Notes:

- Reference Aider documentation for configuration options
- Ensure AGENT.md enforces atomic, context-isolated steps

## Story S1.5: Prompt Library Integration

As a developer, I want to integrate the software-dev-prompt-library into the project so that structured workflows are available to Aider.

Acceptance Criteria:

- `.aider.prompt/` directory is created
- Core prompt categories (planning, coding, architecture, etc.) are added as `SKILL.md` files
- Prompts are accessible via Aider shorthand commands (`$<category>-<promptname>`)
- Aider successfully loads and drops prompts based on AGENT.md instructions

Dependencies: S1.4

Developer Notes:

- Ensure prompt files follow the standard `SKILL.md` format
- Verify shorthand command mapping in AGENT.md

## Technical Dependencies Graph

S1.1 -> S1.2 -> S1.3 -> S1.4 -> S1.5

## Verification Checkpoints

- After S1.1: Verify git repository and basic files exist.
- After S1.2: Verify `docker-compose up` builds and runs the container.
- After S1.3: Verify `./ai-assistant.sh` launches the container and Aider.
- After S1.4: Verify Aider reads `AGENT.md` and applies configuration.
- After S1.5: Verify Aider can load a prompt using `$planning-vision-statement`.
