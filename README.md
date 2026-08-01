
# Local Development AI Assistant

This documentation details the complete, low-cost, high-performance AI integration setup for an HP EliteBook x360 1040 G8 (32GB RAM, 1TB SSD) running Windows 11 with WSL2 (Ubuntu-24.04.1 LTS).
The architecture leverages [OpenRouter](https://openrouter.ai) to process heavy model computation in the cloud for a fraction of the cost, keeping local laptop CPU load at 0% while utilizing Aider for structured code modifications and VS Code Continue for inline autocompletions.

------------------------------

## 1. The Aider Global Aliased Container (Full Version Installation)

download the image once globally and use a bash alias to dynamically spin up a lightweight, ephemeral container that maps to whatever project folder you are currently sitting in.

- Create a *Dockerfile.aider* file from VSCode WSL: Ubuntu terminal:
  `code ~/Dockerfile.aider`

  - Copy and paste the code below in the file:

    ```Dockerfile
    FROM paulgauthier/aider-full:latest

    # Switch to root to install system requirements
    USER root

    # Install Docker CLI and the compose plugin so Aider can run docker commands
    RUN apt-get update && \
    apt-get install -y ca-certificates curl gnupg libpulse0 alsa-utils && \
        install -m 0755 -d /etc/apt/keyrings && \
        curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
        chmod a+r /etc/apt/keyrings/docker.gpg && \
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian bookworm stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
        apt-get update && \
        apt-get install -y docker-ce-cli docker-compose-plugin

    # Grant the non-root user (1000:1000) ownership of /root so it can write cache files     
    RUN chown -R 1000:1000 /root 
    USER 1000:1000
    ```

- Open your WSL2 Ubuntu configuration file (~/.bashrc or ~/.zshrc):
  `nano ~/.bashrc`

- Paste the following smart global alias at the bottom of the file:

  ```bash
  ai_assistant() {
      local TOOL_NAME="ai-assistant"
      local DIR_NAME=$(basename "$(pwd)")
      local WORKSPACE_HASH=$(pwd | md5sum | awk '{print $1}')
      # Use VSCODE_PID as a session ID to group containers; fallback to 0 if not in VS Code
      local SESSION_ID="${VSCODE_PID:-0}"
      # Include SESSION_ID and shell PID ($$) to allow multiple concurrent containers per session
      local CONTAINER_NAME="${TOOL_NAME}-${DIR_NAME}-${WORKSPACE_HASH:0:8}-${SESSION_ID}-${$}"
      local DOCKER_GID=$(getent group docker | cut -d: -f3 2>/dev/null || echo 0)
      local AIDER_IMAGE="aider-agent:latest"
      local DOCKERFILE_PATH="$HOME/Dockerfile.aider"

      # Clean up orphaned containers from previous sessions (e.g., after a VS Code window reload)
      # This allows multiple concurrent containers in the current session, but clears old ones on reload
      local ALL_DIR_CONTAINERS=$(docker ps --filter "label=aider.dir=${WORKSPACE_HASH}" --format "{{.ID}}\t{{.Label \"aider.session\"}}")
      while IFS=$'\t' read -r id session; do
          if [ "$session" != "$SESSION_ID" ]; then
              docker rm -f "$id" > /dev/null 2>&1
          fi
      done <<< "$ALL_DIR_CONTAINERS"

      if [ -f "$DOCKERFILE_PATH" ]; then
          # Relying on Docker's layer cache, this is instant if nothing changed
          # Suppress build output completely unless an error occurs
          if ! docker build -t "$AIDER_IMAGE" -f "$DOCKERFILE_PATH" "$HOME" > /dev/null 2>&1; then
              echo "Failed to build Aider image. Exiting."
              return 1
          fi
      else
          echo "Dockerfile.aider not found at $DOCKERFILE_PATH. Exiting."
          return 1
      fi

      # Ensure the cache directory exists on the host to avoid permission issues
      mkdir -p "$HOME/.cache/aider"

      docker run -it --rm \
          --name "$CONTAINER_NAME" \
          --label "aider.dir=${WORKSPACE_HASH}" \
          --label "aider.session=${SESSION_ID}" \
          --user "$(id -u):$(id -g)" \
          --group-add "$DOCKER_GID" \
          --group-add audio \
          --device /dev/snd \
          -e HOME=/home \
          -v "/var/run/docker.sock:/var/run/docker.sock" \
          -v "$HOME/.docker:/home/.docker:ro" \
          -v "$(pwd):$(pwd)" \
          -w "$(pwd)" \
          -v "$HOME/.bashrc:/home/.bashrc:ro" \
          -v "$HOME/Dockerfile.aider:/home/Dockerfile.aider" \
          -v "$HOME/.gitconfig:/home/.gitconfig:ro" \
          -v "$HOME/.cache/aider:/home/.cache" \
          -v "/run/user/$(id -u)/pulse/native:/run/user/1000/pulse/native" \
          -v "/dev/shm:/dev/shm" \
          -e PULSE_SERVER=unix:/run/user/1000/pulse/native \
          ${RFILE:---env-file .env} \
          "$AIDER_IMAGE" "$@"
  }
  ```

- Save the file (*CTRL + X*, and hit *Enter* or if if using vi, type *:wq*) and reload your shell:
  `source ~/.bashrc`

------------------------------

## 2. Project Environment Variables

Make sure your local project **.env** file contains all your preferences formatted like this:

- [Generate Your Free OpenRouter API Key](https://openrouter.ai/)
- [Generate Your Free Google AI Studio API Key](https://aistudio.google.com/)

```env
# AIDER (AI Assistant)
OPENAI_API_KEY=sk-proj-...
OPENROUTER_API_KEY=sk-or-v1-...
AIDER_OPENROUTER_API_KEY='sk-or-v1-...
HF_TOKEN=hf_...
AIDER_HF_TOKEN=hf_...
GEMINI_API_KEY=AIzaSy...
AIDER_GEMINI_API_KEY=AIzaSy...

LITELLM_NUM_RETRIES=5
```

- Launch aider from any project directory that contains this variables in a **.env** file
  `ai_assistant`

  *NOTE:** *Docker will pull down the single global aider-full image layer, inject all the variables, spin up the multi-model OpenRouter setup, parse the defined conventions instantly, and vanish from your system resources the second you exit the chat*

------------------------------

## 3. Automation Scripts (~/.local/bin/)

### Script A: Configuration Auto-Rewriter & Logger (ai-update-models)

This script queries OpenRouter's live API to fetch active free-tier Qwen model tags. It then automatically updates your global and local configuration profiles, preventing 404 Not Found model deprecation crashes.

`cp ./bin/ai-update-models ~/.local/bin`

### Script B: Workspace Prompt Cleaner (ai-clean)

Removes temporary prompt engineering documentation blocks from your directory after a successful feature commit.

`cp ./bin/ai-clean ~/.local/bin`

Make both script files executable:

`chmod +x ~/.local/bin/ai-update-models ~/.local/bin/ai-clean`

------------------------------

## 4. Global Configuration Layers

### Global Aider Profile & Custom Metadata Overrides (~/.aider/aider.conf.yml and ~/.aider/.aider.model.metadata.json)

Configures a silent dual-model architecture: Gemma 4 31B serves as the system Architect (handling project mapping), while Qwen 3.6 Plus writes edits via OpenRouter. Qwen 3 Coder handles concise Git commit formatting.

`cp ./global-configs/.aider.conf.yml ~/`

Advanced model adjustments for fine-tuning how OpenRouter models function, ensuring stability while keeping context clear.

`cp ./global-configs/.aider.model.settings.yml ~/`

Forces Aider to bypass internal parameter checks, manually setting the input limits and free metrics for OpenRouter's Gemma model layers.

`cp ./global-configs/.aider.model.metadata.json ~/`

------------------------------

## 5. Project-Specific Configuration Profiles ([project-root]/.aider.conf.yml and [project-root]/.aider.rules.md)

Drop these file into project specific root directories to configure isolated testing behaviors. Uncomment the *test-cmd* line and use the right command for your specific project.

`cp ./.aider.conf.yml ~/path/to/project-root`

Use Aider's built-in Project Rules feature to automatically look for a file named *.aider.rules.md* in the project folder, load it into every single prompt, and handle it perfectly across all models without breaking the CLI

`cp ./.aider.rules.md ~/path/to/project-root`

- Trigger automated loop manually inside an active Aider session

  `/test`

- Test a specific file you are currently modifying (ruby on rails docker example)

  `/test docker compose exec -T web bundle exec rspec spec/controllers/api/v1/users_controller_spec.rb`

*If a test fails, Aider grabs the error traceback from the terminal, adds it to the chat history, and asks the Architect model to analyze it. The Editor model then rewrites the file, and Aider automatically reruns the test. It repeats this process until the tests pass or it hits your max reflection limit set in .bashrc.*

- To quickly override the max reflection limit threshold for a one-off massive task, boot Aider with:

  `ai --max-reflections 12 Gemfile`

------------------------------

## 6. Repository Global Context Filter (.aiderignore)

Place this file in your project roots to prevent Aider from uploading log files or build artifacts to the cloud.

`cp ./.aiderignore ~/path/to/project-root`

------------------------------

## 7. VS Code Host Integration (config.yaml)

This configuration registers your keys with the VS Code Continue extension, routing sidebar chats through Gemma 4 and mapping autocomplete suggestions through an optimized OpenAI connection proxy to eliminate connection time-outs. To update this file, edit your ~/.config/Continue/config.yaml file (or open it via the gear icon in the Continue extension sidebar):

```yaml
name: Main Config
version: 1.0.0
schema: v1

models:
  # 1. Flagship Chat Panels
  - name: Free AI Models (Cloud Chat)
    provider: openrouter
    model: openrouter/free
    apiKey: sk-or-your-actual-api-key-here
    contextLength: 32000
    roles:
      - chat
    modelTypes:
      - intent
      - chat
    defaultCompletionOptions:
      contextLength: 32000
      maxTokens: 4096
    capabilities:
      - tool_use

  # 2. Refactoring Engine
  - name: Free AI Models (Refactoring)
    provider: openrouter
    model: openrouter/free
    apiKey: sk-or-your-actual-api-key-here
    roles:
      - edit
      - apply
    modelTypes:
      - edit
    defaultCompletionOptions:
      contextLength: 64000
      maxTokens: 8192

# 3. Fast Inline Ghost-Text Autocomplete Engine (Truncation Warning Patched)
tabAutocompleteModel:
  name: Free AI Models (Free Autocomplete)
  provider: openai
  apiBase: https://openrouter.ai
  model: openrouter/free
  apiKey: sk-or-your-actual-api-key-here
  roles:
    - autocomplete
  defaultCompletionOptions:
    contextLength: 2048
    maxTokens: 128

tabAutocompleteOptions:
  debounceDelay: 600
  maxPromptTokens: 1024
```

------------------------------

## 8. Windows Host VS Code Global Keybindings (keybindings.json)

Maps a keyboard shortcut to instantly trigger the ai-clean workspace cleanup script inside your integrated terminal.

1. Press Ctrl + Shift + P in VS Code.
2. Select Preferences: Open Keyboard Shortcuts (JSON).
3. Paste the following macro block inside the main array:

```json
{
    "key": "ctrl+alt+c",
    "command": "workbench.action.terminal.sendSequence",
    "args": {
        "text": "ai-clean\u000D"
    },
    "when": "terminalFocus"
}
```

------------------------------

## 9. Automated Git Pre-Commit Security Layer (.git/hooks/pre-commit)

This hook catches errors before code changes are committed. It compiles updated code files and executes your specific Docker-wrapped testing suites (Rails/Elgg). If a test fails, the commit is blocked, preventing broken code from entering your repository.

`cp ./bin/pre-commit ~/path/to/project-root/.git/hooks`

------------------------------

## 10. Secure Cloud Continuous Integration & Variables

*For someone who has never used Cloud Continuous Integration (CI), think of GitHub Actions as a free, automated computer in the cloud that wakes up every time you push code to GitHub. It clones your project from scratch, builds your Docker containers, and runs your Rails or Elgg test suites to make sure your AI assistant (Aider) didn't accidentally break anything. This prevents broken code from ever reaching production.*

*To get your automated cloud tester running, you only need to do two things:*
*1. **Create the Folder Structure:** GitHub Actions specifically looks inside a hidden directory named .github/workflows/ at the root of your project. If you name the folders or files anything else, the cloud runner will ignore them.
*2. **Commit and Push:** Once you add the ci.yml file to that folder and run git push origin main, GitHub will automatically detect the file, read your build instructions, and start your automated test suite under the Actions tab of your online GitHub repository.*

### Project Environment Blueprint (.env.example)

Place this template file in your project roots. It acts as an anchor for Docker Compose and your team, detailing which keys must exist without committing real passwords to source control.

`cp ./.env.example ~/path/to/project-root`

### Step 1: Register Secrets on GitHub

To safely feed the DATABASE_PASSWORD and environment arrays into your remote runner without revealing them publicly:

   1. Go to your repository on [GitHub](https://github.com/).
   2. Navigate to *Settings -> Secrets* and *variables -> Actions* in the sidebar.
   3. Click *New repository secret*.
   4. Set the Name to *DB_PASSWORD* and fill the Value field with your secure password.

### Step 2: Cloud Continuous Integration (.github/workflows/ci.yml)

This workflow file acts as your automated pipeline infrastructure. Whenever you type git push, GitHub spins up a clean computer, mounts your Docker containers, and validates the build automatically

`cp ./ci.yml ~/path/to/project-root/.github/workflows`

------------------------------

## Touchless Automated Installation Script

Execute the script by making it executable and running it directly in the WSL terminal to completely build, organize, and assign executable permissions for every single one of your global tool files automatically:

`chmod +x install-ai-stack.sh`

`./install-ai-stack.sh`

------------------------------

## OPTIONAL: Cleanup WSL

- Check WSL system storage capacity
  `df -h /`

- Install and Run NCDU to provide terminal-based visual interface that lists every folder sorted by file weight
  `sudo apt update && sudo apt install -y ncdu`

- Run the interactive disk map starting from your home space:
  `ncdu ~`

- Scans the internal Linux subsystem root
  `sudo ncdu -x /`

  *If the ncdu total disk usage output is not upto the amount of disk space shown under install apps for Ubuntu, quit docker and VSCode and any other program using wsl. Open powershell in administrator mode and run the commands below:*

  - Shut down the virtualization environment completely
    `wsl --shutdown`

  - Check the list of active systems:
    `wsl --list --verbose`

  - Strip the sparse setting tag from the distribution using the exact name string from the output of `wsl --list --verbose:
    `wsl --manage Ubuntu-24.04 --set-sparse false`

  - Execute the Optimize-VHD utility directly on the path replacing username with your actual username:
    `Optimize-VHD -Path "C:\Users\username\AppData\Local\Packages\CanonicalGroupLimited.Ubuntu24.04LTS_79rhkp1fndgsc\LocalState\ext4.vhdx" -Mode Full`

- Enable Sparse Mode to automatically shrink the virtual disk footprint in real-time
  `wsl --manage Ubuntu-24.04 --set-sparse true --allow-unsafe`

------------------------------

## Developer Production Routine

Follow this step-by-step workflow when building a new feature or fixing a bug:

Step 1: Open google gemini from chrome browser
        -> give it a clear description of your AI architectural setup
        -> describe the project
        -> For example:
          -> I have just setup a local AI Agent with Aider in my windows 11 WSL Ubuntu-24.04.1 LTS Distribution running docker desktop.
            -> I have configured aider's dual mode to use openrouter's mistralai/codestral-2501:free as architect and qwen/qwen3.6-plus:free as editor and weak model.
            -> I just took over a ruby on rails app built using Rootstrap's rails_api_base boilerplate which has not been updated since 2020.
            -> My task is to execute a seamless, zero-downtime migration of the app backend to a containerized Rootstrap's rails_api_base Rails 8 pipeline while maintaining the core custom features added by the old maintainer, fix all errors and ensure all the tests is passed. Also, add any missing test to the test suite.
            -> The app is on digitalocean and provides API end points for a native Andriod App built with kotlin and a native IOS App built with swift.
            -> Given that the current Rootstrap's rails_api_base boilerplate has docker configured for rails 8 deployment, I want to also setup my development to use all the added features for easy deployment to production.
            -> Provide me with detailed prompts I can use to achieve this task in a markdown format. This should include:
              -> Progressive grouping technique to limit context bloating when mapping aider workspace files.
              -> Rspec strict schema matching to protect production apps from crashing due to unexpected changes in JSON structures.
              -> Strategy for processing API Controllers safely.
              -> Automated Schema Rules Enforced via .aider.rules.md
        -> Copy the prompts from gemini and structure it into a *.aider.playbook.md* file in your project directory. Implement the prompts iteratively using a *.aider.coder-prompt.md* file.

Step 2: Open a terminal inside your project root.
        -> Create a safe feature branch:
           `git checkout -b feat/your-feature-name`

Step 3: Initialize your prompt instructions file inside VS Code:
           `code .coder-prompt.md`
        -> Detail your feature requirements, active files, and edge cases using this lean pattern.
            -> # Objective: Add user profile avatars to accounts
            -> # Target Files: app/models/user.rb, app/controllers/profiles_controller.rb
            -> # Requirements: Must use ActiveStorage, maximum file size 5MB, resize to square.

Step 4: Launch your quiet, cloud-accelerated AI environment:
           `ai`

Step 5: Load your context files and execute the task:
           `/add app/models/user.rb .coder-prompt.md`
        -> (type `/multiline-o` in the prompt for multiline input, press *'Enter'* to move to the nextline or *'Alt+Enter'* to submit prompt)
        -> To integrate a third-party API that has updated documentation online:
           `/web https://example.com`
        -> Tell the model to execute the change:
            `Read .coder-prompt.md and the scraped documentation to implement the feature.`

Step 6: Run tests manually inside the AI chat container session:
           `/test`
        -> (If anything breaks, the agent auto-corrects the code via *'auto-test'*)

Step 7: Exit the AI interface once the auto-commit succeeds:
           `/exit`

Step 8: Press *'Ctrl + Alt + C'* inside the VS Code terminal or type `ai-clean`.
        -> This triggers *'ai-clean'*, leaving your workspace completely spotless.
