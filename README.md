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

You can use this assistant in other projects by copying the `.agent` directory, the root launcher, and `.githooks/` to that project's root:

```bash
cp -r .agent /path/to/your/project/
cp agent.sh /path/to/your/project/
cp -r .githooks /path/to/your/project/
```

The `.agent` copy already includes `.aider.conventions/`, so all
convention files stay in that directory. Framework conventions are
enabled per project via the `read:` setting in
`.agent/.aider.conf.yml` — they are read on launch, never copied to
the project root.

Make the launchers and the commit-msg hook executable and update the git index so you don't have to run the execute command again in that repo:

```bash
cd /path/to/your/project/
chmod +x agent.sh .agent/ai-assistant.sh .githooks/commit-msg
git update-index --chmod=+x agent.sh .agent/ai-assistant.sh .githooks/commit-msg
git config core.hooksPath .githooks
```

The last command enables the commit message gate in that project right
away; every assistant launch sets it too when it is still unset (see
[Commit Message Gate](#commit-message-gate)). Remove it anytime with
`git config --unset core.hooksPath`.

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

#### Mergeable configuration with your project root

At launch — whether via `./agent.sh` or the `ai-assistant` command — the
launcher checks your project root for same-named counterparts of its four
configuration files and combines them with the `.agent/` defaults:

| File | Format | Combination rule |
| :--- | :--- | :--- |
| `.aider.conf.yml` | YAML | Deep-merged: your root value wins each conflict, agent defaults are kept for keys you do not set |
| `.aider.model.settings.yml` | YAML | Entries merged per model `name`: your entry overrides the matching default, untouched defaults are kept |
| `.aider.model.metadata.json` | JSON | Deep-merged: your root value wins each conflict, agent defaults are kept |
| `.aiderignore` | gitignore patterns | Union of both files' patterns, duplicates counted once |

To override or extend the defaults, create a file with the same name in
your project root. For example, a root `.aider.conf.yml` containing
`auto_commits: true` flips that one setting while every other
`.agent/.aider.conf.yml` default still applies:

```yaml
auto_commits: true
```

If your project root has no counterpart for a file, the `.agent/` copy is
used unchanged — nothing changes until you add one. If a counterpart
cannot be parsed (for example unsupported YAML syntax), the launcher falls
back to the `.agent/` copy instead of failing the launch, and reports it
in `--debug` output.

The combined files are written under `.agent/.merged/` — never to either
source file — rewritten deterministically on every launch, and removed
when the session ends.

#### SSH access for git remotes

Git push/pull over SSH remotes works inside the container without manual
setup. The launcher mounts your host `~/.ssh` directory read-only at the
identical path, so keys, config, and `known_hosts` travel together and the
container can never modify the host's SSH state. When an ssh-agent is
reachable, its socket is forwarded at the identical path and
passphrase-protected keys work without copying them; the entry script
starts or reuses a persistent per-user agent on the first interactive
launch.

GitHub's published SSH host keys are pinned automatically for `github.com`:
the ed25519 and ecdsa keys are embedded in the entry script, and the rsa
key is fetched from `api.github.com` once (a one-time fetch, up to ten
seconds, on the first interactive launch) and appended only after its
SHA256 fingerprint matches GitHub's published value. First-use connections
therefore never stall on a host-key prompt. Pinning is idempotent, runs
only in interactive launches, and never fails the launch. Projects using
HTTPS remotes are unaffected.

> **Note:** if GitHub ever rotates a host key, connections fail with a
> host-key-changed error. Remove the stale entry with
> `ssh-keygen -R github.com`, update to a release whose entry script
> carries the new key, and relaunch — pinning re-runs and re-verifies each
> key. The rsa key needs no script update: it is re-fetched and
> fingerprint-verified whenever no rsa key is pinned.

#### One-command install

The quickest way to set the assistant up in another project is the
one-command installer. From inside the target project's repository,
run:

```bash
curl -fsSL https://raw.githubusercontent.com/daveonche/ai_assistant/v1.0.17/scripts/install.sh | bash
```

The installer needs only the documented host prerequisites: Bash and
git. It clones the pinned release reference into a temporary
directory, copies `.agent/`, `agent.sh`, and `.githooks/` into the
project root, records the entry scripts and the commit-msg hook as
executable in the project's git index (`git update-index --chmod=+x`),
enables the commit message gate by default (`git config core.hooksPath
.githooks` — an existing `core.hooksPath` value is left untouched with
a warning), and removes the temporary directory when it finishes,
leaving no temporary artifacts behind. No manual step follows: the
hook is left executable and active, so git runs it on the project's
next commit. Afterwards, configure the environment variables as
described above and run `./agent.sh` from the project root.

#### Updating an existing install

When `.agent/` or `agent.sh` already exist, the same command switches
to update mode:

```bash
curl -fsSL https://raw.githubusercontent.com/daveonche/ai_assistant/v1.0.17/scripts/install.sh | bash
```

The installer first warns that local customizations inside `.agent/`
(for example the `read:` list in `.agent/.aider.conf.yml`) will be
overwritten. It then shows the incoming changes and asks for
confirmation before touching anything; pass `--yes` to skip the prompt
in non-interactive runs. The refresh goes through the project's own
git: it fetches the pinned reference from the `ai-assistant` remote,
checks out `.agent`, `agent.sh`, and — when the release ships the
commit-msg hook — `.githooks`, enables the commit message gate after
confirmation (unless `core.hooksPath` is already set), and records the
refresh as a single commit whose subject conforms to that gate. The
update is therefore a normal, reviewable, revertable project change —
re-apply your local customizations after the update completes.

When `raw.githubusercontent.com` is unreachable — for example a broken
local resolver, or a network that blocks or filters the raw domain —
the installer can be retrieved from the same repository over
`github.com` with plain git and piped to `bash` the same way:

```bash
git fetch --depth 1 https://github.com/daveonche/ai_assistant.git v1.0.17 && git show FETCH_HEAD:scripts/install.sh | bash
```

The git-served installer behaves identically to the curl variant:
same warning, preview, and confirmation prompt, and the same options
after `bash -s --` (for example `bash -s -- --dry-run`).

#### Pinned-reference caveat

Installs and updates always retrieve the pinned release tag `v1.0.17`,
never `main`, so repeated runs are reproducible. To install from a
different reference, pass `--ref`:

```bash
curl -fsSL https://raw.githubusercontent.com/daveonche/ai_assistant/v1.0.17/scripts/install.sh | bash -s -- --ref v1.0.0
```

Three more options help before and during a run: `--dry-run` reports
the planned action without changing anything, `--yes` skips the update
confirmation prompt for non-interactive runs, and `--debug` enables
shell tracing for troubleshooting.

### Project Structure for Docker Compose Projects

If using with other projects that are built with Docker Compose, all the Docker files and configurations should be placed in the root directory, and the project's main source code should be placed in the `src/` folder.

## Logging and Debug Mode

Every Docker and git command the launcher runs is appended to a per-session command log in the user's cache directory. The log file is named `ai-assistant-<workspace-hash>-<session-id>.log` (for example, `~/.cache/aider-agent/ai-assistant-1a2b3c4d-12345.log`), and the exact path is printed when debug mode is enabled. The log is appended to across runs of the same session and never contains secret values: credentials are forwarded to the container by variable name only.

### Enabling Debug Mode

Run the launcher with the `--debug` flag (short form `-x`):

```bash
./agent.sh --debug
```

In debug mode the launcher additionally prints to stderr:

- Each Docker and git command just before it runs
- The command log path at startup
- The image cache tag used for the build-or-skip decision
- The last 10 command-log entries when the assistant fails to start

Spinner progress output is suppressed in debug mode so the traced commands print cleanly.

### Normal Mode

Without the flag, the launcher shows spinner progress feedback only while long operations run; Docker and git commands are still recorded to the command log file.

## Agent Workflow Sessions

The `.agent` orchestration configuration supports long-running workflow sessions that survive chat resets. Session position is kept in `docs/workflow_state.md`.

1. **Checkpoint anytime:** run `$session-checkpoint` to save the current workflow position (workflow command, current step, last completed step, next action, files in context) to `docs/workflow_state.md`.
2. **Clear the context:** run `/clear` to start a fresh chat without losing your position.
3. **Resume:** in the fresh session, add the state file to the chat with `/read-only docs/workflow_state.md`; the orchestrator announces where you stopped and asks you to reply `continue` to resume from the checkpoint, or `discard` to clear the recorded state.

## Continuous Integration (CI)

This project includes a GitHub Actions workflow (`.github/workflows/ci.yml`) that validates the assistant's own tooling on every push or pull request touching `.agent/**`, `agent.sh`, or `.github/workflows/**`, and on manual `workflow_dispatch`:

1. **Validate launcher and scripts** — Python syntax check of `.agent/ai_assistant.py`, then `shellcheck` over all tracked `*.sh` scripts, then the commit-msg gate (`.githooks/commit-msg`) validating every commit the push introduces (tip-only checks on pull requests and new-branch pushes).
2. **Docker image build smoke test** — builds the image from `.agent/Dockerfile.aider`.
3. **Release tag guard** — on `v*` tag pushes, asserts the tag equals `DEFAULT_REF` in `scripts/install.sh`, so a tag cannot ship with a stale installer pin.

> **Important:** GitHub Actions only runs workflows from
> `.github/workflows/`. A `ci.yml` file inside `.agent/` will not be
> executed automatically. Keep the active workflow at
> `.github/workflows/ci.yml`.

## Commit Message Gate

A tracked `commit-msg` hook (`.githooks/commit-msg`) mechanically
enforces the subject format the assistant's `commit-prompt` asks for:
`type(scope): summary`, max 72 characters, plain text — no quotes or
backticks. The launcher activates it automatically: every launch sets
`core.hooksPath` to `.githooks` when the project is a git worktree that
ships the gate and the setting is still unset, so the gate is live from
the first `./agent.sh` run with no manual step. To enable it without
launching the assistant, run:

```bash
git config core.hooksPath .githooks
```

A non-conforming subject (stray chat prose, missing type, over-length
line) is rejected before the commit is created, so a misfiring LLM
commit is stopped at the gate instead of landing in history. The hook
also rejects any message that embeds an aider SEARCH/REPLACE edit block
(the `<<<<<<< SEARCH` / `>>>>>>> REPLACE` anchor lines), in the subject
or the body — the failure mode seen when the LLM echoes an edit block
into the commit message instead of prose. Git's auto-generated subjects
(`Merge …`, `fixup! …`, `squash! …`, `Revert "…"`) are exempt. The CI
`validate` job runs the same script on every commit a push introduces,
so the gate also holds on machines without the hook enabled and catches
a non-conforming subject even when it was committed with `--no-verify`
and buried under later commits.

The gate is default-on in consumer projects: the one-command installer,
the manual copy instructions, and every assistant launch set
`core.hooksPath` to `.githooks` — each only when the setting is unset,
so an existing value (pre-commit, husky, …) is never overwritten. The
installer warns when it leaves an existing value untouched, and its own
update commit conforms to the enforced format so the freshly enabled
gate accepts it. Remove the gate from a project with `git config
--unset core.hooksPath`; the next launch re-enables it unless the
`.githooks/` directory is removed as well.

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
(`v1.0.2` -> `v1.0.3`). To choose the reference explicitly, pass it as
the only argument:

```bash
./scripts/release.sh v1.1.0
```

`--dry-run` previews the plan without changing anything, `-v/--verbose`
prints per-file bump detail, and `--debug` enables shell tracing.

After the push, wait for the `release-tag-guard` job to pass, then
verify the served installer carries the new pin:

```bash
curl -fsSL https://raw.githubusercontent.com/daveonche/ai_assistant/v1.0.17/scripts/install.sh | grep -E 'DEFAULT_REF=|no commits yet'
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
├── .githooks/
│   └── commit-msg           # Git commit-msg hook (subject format gate)
├── docs/                    # Project documentation and analysis
├── scripts/                 # Utility scripts
└── src/                     # Source code
```
