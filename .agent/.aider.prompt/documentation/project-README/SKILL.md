# Project README Generator

**Convention Check Reminder:** Before creating or editing any file, check the Conventions Reference Routing table in `.agent/AGENTS.md` and load the matching reference via `/read-only` before proceeding.

## Gotchas
- Preserve manually maintained README content (badges, team documentation, custom sections) when updating an existing README.
- The `/read-only` and `/drop` commands must use the full path including `.agent/`:
  - `/read-only .agent/.aider.prompt/documentation/project-README/SKILL.md`
  - `/drop .agent/.aider.prompt/documentation/project-README/SKILL.md`
- When generating commands, use actual commands from package/config files rather than placeholders.

## Progress Checklist
- [ ] Step 0: Context setup
- [ ] Step 1: Analyze
- [ ] Step 2: Generate
- [ ] Step 2.5: Validate
- [ ] Step 3: Output

## Workflow

### Step 0: Context setup
1. Ask the user: "Is this prompt file currently loaded in your context? (Y/N)" — do not assess context contents yourself (Critical Rule 3). If the user answers N, ask them to run:
   `/read-only .agent/.aider.prompt/documentation/project-README/SKILL.md`
   and wait until they confirm it is added.
2. Ask the user: "Are the relevant project files currently loaded in your context? If yes, name them. (Y/N)" — do not assess context contents yourself (Critical Rule 3). If the user answers N, ask them to add the relevant project files. Prefer:
   - package/config files
   - `README.md` if present
   - `docs/requirements.md`
   - `docs/tech_stack.md`
   - `docs/architecture/architecture.md`
   - `docs/user_stories.md`
   - `src/` entry points

[STOP - Wait until the user replies with "relevant files added" before proceeding.]

### Step 1: Analyze
1. Scan all available project files and documentation.
2. Select the most relevant files and documentation.
3. Analyze code structure, dependencies, and configuration files.
4. Identify core technologies from package files and code imports.
5. Map component relationships through imports and architecture patterns.
6. Extract build, run, and test instructions from configuration files.
7. If a `README.md` already exists, refer to the **Gotchas** section and preserve manual content as described there.

### Step 2: Generate
Generate a comprehensive README using this structure. Use the guidance below for concrete content:

- For each placeholder like `[Analysis of project purpose and capabilities based on codebase]`, write a short, specific sentence rather than leaving the placeholder.
- Core Technologies entries should use the format `Technology — role/purpose` (e.g., `FastAPI — REST API framework`).
- For `Installation`, `Usage`, and `Testing` commands, extract the actual commands from `pyproject.toml`, `package.json`, `Makefile`, or other config files.

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

### Step 2.5: Validate
1. Cross-check the generated README against the project files and documentation.
   - Ensure all installation, usage, and testing commands exist in package or config files.
   - Verify that each technology in `Core Technologies` appears in package files or imports.
   - Confirm architecture components match code structure and imports.
2. Correct any mismatches found.
3. Repeat validation until the generated content aligns with the project.

[STOP - Present the generated README. Wait for the user to reply with "README approved" before proceeding.]

### Step 3: Output
1. Ask the user whether they want to save the file directly or output the markdown block to copy.
2. If saving directly:
   - Ask the user to enter `/code` mode.
   - Wait for the user to say “save to file”.
3. If outputting:
   - Provide the complete markdown block.

[STOP - End of workflow. Ask the user if they want to drop the prompt file from context. If yes, tell them to run `/drop .agent/.aider.prompt/documentation/project-README/SKILL.md`. Wait for the user’s response.]

<!-- sentinel: documentation/project-README -->
