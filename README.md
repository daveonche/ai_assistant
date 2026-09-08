# AIAssistant

A CLI wrapper and pipeline orchestrator for the Aider AI coding assistant. It leverages Docker to run Aider in an isolated, containerized environment, integrating seamlessly with cloud-based LLM providers like OpenRouter, OpenAI, Google AI, and Hugging Face.

## Features

- **Isolated Environment:** Runs Aider inside a Docker container to keep your local system clean.
- **Multi-Model Support:** Configured to use OpenRouter, OpenAI, Gemini, and Hugging Face APIs.
- **CI Validation:** Includes a GitHub Actions workflow (`.github/workflows/ci.yml`) that validates the launcher, shell scripts, and the Docker image build on every push and pull request.
- **Diagram Support:** Includes Mermaid CLI and Chromium for rendering diagrams.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (CLI & Compose Plugin): provides the isolated container that runs Aider, and the Compose Plugin backs the container lifecycle commands used by the launcher
- [Git](https://git-scm.com/): needed to clone this repository and to copy the configuration into other projects; the launcher itself does not require Git to start the assistant
- Bash: runs the `agent.sh` and `.agent/ai-assistant.sh` entry scripts
- Python >=3.8 (host): runs the launcher (`.agent/ai_assistant.py`) and the direct `ai-assistant` install; the minimum version matches `requires-python` in `.agent/pyproject.toml`
- API Keys for your chosen LLM providers (OpenRouter, OpenAI, Google AI, Hugging Face): authenticate the model calls Aider makes at launch

## Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Configure Environment Variables:**

   Copy the example environment file and update it with your API keys.

   ```bash
   cp .agent/.env.example .env
   ```

   Edit `.env` and fill in your `OPENAI_API_KEY`, `OPENROUTER_API_KEY`, `GEMINI_API_KEY`, and `HF_TOKEN`.

3. **Make the launch scripts executable (if not already):**

   ```bash
   chmod +x agent.sh .agent/ai-assistant.sh
   ```

## Usage

To start the AI assistant, run the root convenience launcher from the root of your project:

```bash
./agent.sh
```

This launcher calls `.agent/ai-assistant.sh`. That script delegates to `.agent/ai_assistant.py`, which automatically builds the Docker image when needed and starts the container with the necessary volume mappings and environment variables.

If you prefer a direct console command, install the `.agent` package in editable mode inside a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .agent
ai-assistant
```

> **Note:** Using a virtual environment avoids the PEP 668
> “externally-managed-environment” error that occurs when trying to
> install packages directly into a system-managed Python. If you prefer
> an isolated application install, you can also use
> `pipx install -e .agent`.

### Using in Other Projects

You can use this assistant in other projects by copying the `.agent` directory and the root launcher to that project's root:

```bash
cp -r .agent /path/to/your/project/
cp agent.sh /path/to/your/project/
```

The `.agent` copy already includes `.aider.conventions/`, so all
convention files stay in that directory. Framework conventions are
enabled per project via the `read:` setting in
`.agent/.aider.conf.yml` — they are read on launch, never copied to
the project root.

Make the launchers executable and update the git index so you don't have to run the execute command again in that repo:

```bash
cd /path/to/your/project/
chmod +x agent.sh .agent/ai-assistant.sh
git update-index --chmod=+x agent.sh .agent/ai-assistant.sh
```

Configure the environment variables for the target project. The
launcher reads `.env` from the project root, falling back to
`.agent/.env`:

```bash
cp .agent/.env.example .env
```

Edit `.env` and fill in your `OPENAI_API_KEY`, `OPENROUTER_API_KEY`,
`GEMINI_API_KEY`, and `HF_TOKEN`.

Then run `./agent.sh` from that project's directory. The entry chain
resolves its own paths at runtime, so it behaves exactly as it does in
a standalone clone.

If you prefer a direct `ai-assistant` command instead, install the `.agent` package in editable mode inside a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .agent
ai-assistant
```

> **Note:** Using a virtual environment avoids the PEP 668
> “externally-managed-environment” error that occurs when trying to
> install packages directly into a system-managed Python. If you prefer
> an isolated application install, you can also use
> `pipx install -e .agent`.

### Project Structure for Docker Compose Projects

If using with other projects that are built with Docker Compose, all the Docker files and configurations should be placed in the root directory, and the project's main source code should be placed in the `src/` folder.

## Logging and Debug Mode

Every Docker command the launcher runs is appended to a per-session command log in the system temporary directory. The log file is named `ai-assistant-<workspace-hash>-<session-id>.log` (for example, `/tmp/ai-assistant-1a2b3c4d-12345.log`), and the exact path is printed when debug mode is enabled. The log is appended to across runs of the same session and never contains secret values: credentials are forwarded to the container by variable name only.

### Enabling Debug Mode

Run the launcher with the `--debug` flag (short form `-x`):

```bash
./agent.sh --debug
```

In debug mode the launcher additionally prints to stderr:

- Each Docker command just before it runs
- The command log path at startup
- The image cache tag used for the build-or-skip decision
- The last 10 command-log entries when the assistant fails to start

Spinner progress output is suppressed in debug mode so the traced commands print cleanly.

### Normal Mode

Without the flag, the launcher shows spinner progress feedback only while long operations run; Docker commands are still recorded to the command log file.

## Agent Workflow Sessions

The `.agent` orchestration configuration supports long-running workflow sessions that survive chat resets. Session position is kept in `docs/workflow_state.md`.

1. **Checkpoint anytime:** run `$session-checkpoint` to save the current workflow position (workflow command, current step, last completed step, next action, files in context) to `docs/workflow_state.md`.
2. **Clear the context:** run `/clear` to start a fresh chat without losing your position.
3. **Resume:** in the fresh session, add the state file to the chat with `/read-only docs/workflow_state.md`; the orchestrator announces where you stopped and asks you to reply `continue` to resume from the checkpoint, or `discard` to clear the recorded state.

## Continuous Integration (CI)

This project includes a GitHub Actions workflow (`.github/workflows/ci.yml`) that validates the assistant's own tooling on every push or pull request touching `.agent/**`, `agent.sh`, or `.github/workflows/**`, and on manual `workflow_dispatch`:

1. **Validate launcher and scripts** — Python syntax check of `.agent/ai_assistant.py`, then `shellcheck` over all tracked `*.sh` scripts.
2. **Docker image build smoke test** — builds the image from `.agent/Dockerfile.aider`.

> **Important:** GitHub Actions only runs workflows from
> `.github/workflows/`. A `ci.yml` file inside `.agent/` will not be
> executed automatically. Keep the active workflow at
> `.github/workflows/ci.yml`.

## Project Structure

```txt
.
├── agent.sh                 # Root convenience launcher
├── .agent/
│   ├── AGENTS.md            # Agent workflow & context orchestrator
│   ├── ai-assistant.sh      # Thin Bash launcher that invokes ai_assistant.py
│   ├── ai_assistant.py      # Python CLI implementation
│   ├── Dockerfile.aider     # Dockerfile for the Aider environment
│   ├── .env.example         # Template for environment variables
│   ├── .aider.conf.yml      # Aider configuration
│   ├── .aider.model.settings.yml
│   ├── .aiderignore         # Context exclusion rules for aider
│   ├── .aider.prompt/       # Aider prompt library
│   ├── .aider.conventions/  # Project-specific coding conventions
│   └── pyproject.toml       # Optional packaging for the `ai-assistant` command
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI workflow
├── docs/                    # Project documentation and analysis
├── scripts/                 # Utility scripts
└── src/                     # Source code
```
