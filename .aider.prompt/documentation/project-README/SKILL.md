# Project README Generator

## Workflow

### Step 0: Context setup
1. Ensure this prompt file is loaded in context. If not, ask the user to run:
   `/read-only .aider.prompt/documentation/project-README/SKILL.md`
2. Ask the user to add relevant project files to the chat if they are not already present. Prefer:
   - package/config files
   - `README.md` if present
   - `docs/requirements.md`
   - `docs/tech_stack.md`
   - `docs/architecture/architecture.md`
   - `docs/user_stories.md`
   - `src/` entry points

[STOP - Wait until the user confirms the relevant files are added.]

### Step 1: Analyze
1. Scan all available project files and documentation.
2. Select the most relevant files and documentation.
3. Analyze code structure, dependencies, and configuration files.
4. Identify core technologies from package files and code imports.
5. Map component relationships through imports and architecture patterns.
6. Extract build, run, and test instructions from configuration files.
7. If a `README.md` already exists:
   - Preserve manual sections such as custom badges, team documentation, or manually maintained content.
   - Identify only outdated sections.
   - Update inaccurate information without overwriting manually maintained content.
   - If unsure whether a section is manual or generated, ask the user before changing it.

### Step 2: Generate
Generate a comprehensive README using this structure:

# [Project Name]

## Overview
[Analysis of project purpose and capabilities based on codebase]

## Core Technologies
- [Technology Name]: [Role/Purpose derived from usage]
[List each major technology identified]

## Architecture
[Component relationship diagram or list based on code structure]
- [Component Name]: [Purpose and relationships]
[List each core component]

## Getting Started
### Prerequisites
[List dependencies found in package files]

### Installation
```bash
[Commands extracted from package files]
```

### Usage
[Instructions on how to run and use the project]

### Testing
[Instructions on how to run tests]

## Contributing
[Guidelines for contributing to the project]

## License
[Project license information]

[STOP - Present the generated README to the user for review. Wait for user confirmation before proceeding.]

### Step 3: Output
1. Ask the user whether they want to save the file directly or output the markdown block to copy.
2. If saving directly:
   - Ask the user to enter `/code` mode.
   - Wait for the user to say “save to file”.
3. If outputting:
   - Provide the complete markdown block.

[STOP - End of workflow. Ask the user if they want to drop the prompt file from context using `/drop .aider.prompt/documentation/project-README/SKILL.md`.]
