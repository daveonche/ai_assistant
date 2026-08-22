
# Local Development AI Assistant

This documentation details the complete, low-cost, high-performance AI integration setup for an HP EliteBook x360 1040 G8 (32GB RAM, 1TB SSD) running Windows 11 with WSL2 (Ubuntu-24.04.1 LTS).
The architecture leverages [OpenRouter](https://openrouter.ai) to process heavy model computation in the cloud for a fraction of the cost, keeping local laptop CPU load at 0% while utilizing Aider for structured code modifications and VS Code Continue for inline autocompletions.

------------------------------

## The Aider Docker Container (Full Version Installation)

1. Clone the repo
   `git clone git@github.com:daveonche/ai_architecture.git`

2. Copy *.env.example* to *.env*
   `cp .env.example .env`

3. Generate API Keys and update the *.env* variables
    - [Generate Your Free OpenRouter API Key](https://openrouter.ai/)
    - [Generate Your Free Google AI Studio API Key](https://aistudio.google.com/)
    - [Generate Your Free Hugging Face (HF_TOKEN) Token Key](https://huggingface.co/)
    - [Generate Your Free OpenAI API Key](https://platform.openai.com/)

4. Launch aider
   `./ai_assistant`

  *NOTE:** *Docker will pull down the single global aider-full image layer, inject all the variables, spin up the multi-model OpenRouter setup, parse the defined conventions instantly, and vanish from your system resources the second you exit the chat*

------------------------------

## Use The AI Assistant in your Projects

- Copy *.env.example* to *.env* in your project root or merge the values with the project's **.env** variables
  `cp .env.example path/to/project/root`

- Copy the following files to the project root
  `cp ./aider.conf.yml ./.aider.model.settings.yml ./ai-assistant.sh ./Dockerfile.aider path/to/project/root`

- Make *ai-assistant.sh* executable and add the command to git repo so you don't have to run the execute command again in the repo
  `git init`
  `chmod +x ai-assistant.sh`
  `git add .`
  `git update-index --chmod=+x ai-assistant.sh`

  See [Aider docs](https://aider.chat/docs/) for more info

------------------------------

## 7. VS Code Host Integration (config.yaml)

This configuration registers your keys with the VS Code Continue extension, routing sidebar chats through Gemma 4 and mapping autocomplete suggestions through an optimized OpenAI connection proxy to eliminate connection time-outs. To update this file, edit your ~/.config/Continue/config.yaml file (or open it via the gear icon in the Continue extension sidebar):

```yaml
name: Main Config
version: 1.0.0
schema: v1

models:
  # 1. Flagship Chat Panels
  - name: Model Name (Cloud Chat)
    provider: openrouter
    model: openrouter/z-ai/glm-5.2
    apiKey: sk-or-v1-...
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
  - name: Model Name (Refactoring)
    provider: openrouter
    model: openrouter/poolside/laguna-xs-2.1
    apiKey: sk-or-v1-...
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
  name: Model Name (Autocomplete)
  provider: openai
  apiBase: https://openrouter.ai
  model: openrouter/gemini-3.1-flash-lite
  apiKey: sk-or-v1-...
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
# AIAssistant

A CLI wrapper and pipeline orchestrator for the Aider AI coding assistant.

## Getting Started

(Instructions to be added)
