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
- Python >=3.12 (host pin 3.12.12): runs the launcher (`.agent/ai_assistant.py`) and the direct `ai-assistant` install; the minimum version matches `requires-python` in `.agent/pyproject.toml`
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

#### One-command install

The quickest way to set the assistant up in another project is the
one-command installer. From inside the target project's repository,
run:

```bash
curl -fsSL https://raw.githubusercontent.com/daveonche/ai_assistant/v1.0.3/scripts/install.sh | bash
```

The installer needs only the documented host prerequisites: Bash and
git. It clones the pinned release reference into a temporary
directory, copies `.agent/` and `agent.sh` into the project root,
records both entry scripts as executable in the project's git index
(`git update-index --chmod=+x`), and removes the temporary directory
when it finishes, leaving no temporary artifacts behind. Afterwards,
configure the environment variables as described above and run
`./agent.sh` from the project root.

#### Updating an existing install

When `.agent/` or `agent.sh` already exist, the same command switches
to update mode:

```bash
curl -fsSL https://raw.githubusercontent.com/daveonche/ai_assistant/v1.0.3/scripts/install.sh | bash
```

The installer first warns that local customizations inside `.agent/`
(for example the `read:` list in `.agent/.aider.conf.yml`) will be
overwritten. It then shows the incoming changes and asks for
confirmation before touching anything; pass `--yes` to skip the prompt
in non-interactive runs. The refresh goes through the project's own
git: it fetches the pinned reference from the `ai-assistant` remote,
checks out `.agent` and `agent.sh`, and records the refresh as a
single commit. The update is therefore a normal, reviewable,
revertable project change — re-apply your local customizations after
the update completes.

#### Pinned-reference caveat

Installs and updates always retrieve the pinned release tag `v1.0.3`,
never `main`, so repeated runs are reproducible. To install from a
different reference, pass `--ref`:

```bash
curl -fsSL https://raw.githubusercontent.com/daveonche/ai_assistant/v1.0.3/scripts/install.sh | bash -s -- --ref v1.0.0
```

Three more options help before and during a run: `--dry-run` reports
the planned action without changing anything, `--yes` skips the update
confirmation prompt for non-interactive runs, and `--debug` enables
shell tracing for troubleshooting.

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
3. **Release tag guard** — on `v*` tag pushes, asserts the tag equals `DEFAULT_REF` in `scripts/install.sh`, so a tag cannot ship with a stale installer pin.

> **Important:** GitHub Actions only runs workflows from
> `.github/workflows/`. A `ci.yml` file inside `.agent/` will not be
> executed automatically. Keep the active workflow at
> `.github/workflows/ci.yml`.

## Releasing

Releases exist for changes that must reach consumers of the one-command
install: the tag's raw URL serves `scripts/install.sh`, and its
`DEFAULT_REF` decides which reference gets installed. Everyday pushes
to `main` need no release. `scripts/release.sh` cuts one in a single
command: it verifies the repository state, preflights the test suite on
the clean tree, bumps the pinned reference across the enforced files
(`scripts/install.sh`, `README.md`, and the S2.1 test suites), re-runs
the suite, records the bump as one commit, tags it, and pushes `main`
and the tag. The CI `release-tag-guard` job then asserts the tag equals
`DEFAULT_REF`, so a stale pin cannot ship.

### Release environment

The release script gates on the project's full test suite, so the host
needs the tools the suite uses:

- Bash and git (see [Prerequisites](#prerequisites))
- Python >=3.12 with `pytest` and `pyyaml` installed — the script uses
  the first pytest-capable interpreter among the `PYTHON_BIN` override,
  `.venv/bin/python3` (when present), and `python3` from the `PATH`
- `shellcheck` on the `PATH` (on Debian/Ubuntu:
  `sudo apt-get install shellcheck`; see
  [shellcheck.net](https://www.shellcheck.net) for other platforms)

Prepare the virtual environment the suite runs in:

```bash
python3 -m venv .venv
.venv/bin/pip install pytest pyyaml
```

### Cutting a release

Merge the changes to `main`, push, and run from a clean `main` that is
in sync with `origin/main` — the script aborts otherwise:

```bash
./scripts/release.sh --auto
```

`--auto` increments the current `DEFAULT_REF`'s patch segment
(`v1.0.3` -> `v1.0.4`). To choose the reference explicitly, pass it as
the only argument:

```bash
./scripts/release.sh v1.1.0
```

`--dry-run` previews the plan without changing anything, `-v/--verbose`
prints per-file bump detail, and `--debug` enables shell tracing.

After the push, wait for the `release-tag-guard` job to pass, then
verify the served installer carries the new pin:

```bash
curl -fsSL https://raw.githubusercontent.com/daveonche/ai_assistant/v1.0.3/scripts/install.sh | grep -E 'DEFAULT_REF=|no commits yet'
```

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
