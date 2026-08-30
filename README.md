# AIAssistant

A CLI wrapper and pipeline orchestrator for the Aider AI coding assistant. It leverages Docker to run Aider in an isolated, containerized environment, integrating seamlessly with cloud-based LLM providers like OpenRouter, OpenAI, Google AI, and Hugging Face.

## Features

- **Isolated Environment:** Runs Aider inside a Docker container to keep your local system clean.
- **Multi-Model Support:** Configured to use OpenRouter, OpenAI, Gemini, and Hugging Face APIs.
- **Automated Testing:** Includes a GitHub Actions workflow (`ci.yml`) to automatically run tests for Rails, Elgg, or Odoo projects upon push.
- **Diagram Support:** Includes Mermaid CLI and Chromium for rendering diagrams.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (CLI & Compose Plugin)
- [Git](https://git-scm.com/)
- Bash (runs `agent.sh` and `.agent/ai-assistant.sh`)
- Python >=3.8 (host; runs the launcher and the direct `ai-assistant` install)
- API Keys for your chosen LLM providers (OpenRouter, OpenAI, Google AI, Hugging Face)

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
# Copy the specific convention file for your project (e.g., ELGG.md, RAILS.md, ODOO.md)
cp .agent/.aider.conventions/CONVENTIONS-FILENAME.md /path/to/your/project/
```

Make the launchers executable and update the git index so you don't have to run the execute command again in that repo:

```bash
cd /path/to/your/project/
chmod +x agent.sh .agent/ai-assistant.sh
git update-index --chmod=+x agent.sh .agent/ai-assistant.sh
```

Then run `./agent.sh` from that project's directory.

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

## Continuous Integration (CI)

This project includes a GitHub Actions workflow (`.github/workflows/ci.yml`) that automatically runs tests on push or pull request events.

**Supported Frameworks:**

- **Ruby on Rails:** Detected if `RAILS.md` exists in the project root. Runs `bundle exec rails test`.
- **Elgg:** Detected if `ELGG.md` exists in the project root. Runs `phpunit`.
- **Odoo:** Detected if `ODOO.md` exists in the project root. Runs `odoo --test-enable --stop-after-init`.

**Setup:**

1. Ensure the `ci.yml` file is located in `.github/workflows/` in your repository.
2. Add `DB_PASSWORD` to your repository's GitHub Actions Secrets.

To avoid running CI for changes that only affect the `.agent` directory,
add a `paths-ignore` entry for `.agent/**` in your workflow triggers:

```yaml
on:
  push:
    paths-ignore:
      - '.agent/**'
  pull_request:
    paths-ignore:
      - '.agent/**'
```

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
