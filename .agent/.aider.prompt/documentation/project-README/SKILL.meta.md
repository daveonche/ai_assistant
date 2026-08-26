# Project README Generator/Updater

## Description

Generates a new project README or updates an existing one by analyzing codebase files, documentation, and configuration, then validates the generated README against project files. When updating, it preserves manual sections and updates only outdated or inaccurate information.

## Usage

1. Activate the prompt with:
   `$documentation-project-README`
   - Or say: "Generate or update a README for this project using the README generator prompt"
2. When prompted, add relevant project files. Preferred files:
   - package/config files
   - existing `README.md`
   - `docs/requirements.md`
   - `docs/tech_stack.md`
   - `docs/architecture/architecture.md`
   - `docs/user_stories.md`
   - `src/` entry points
3. The workflow includes context management commands:
   - Load: `/read-only .agent/.aider.prompt/documentation/project-README/SKILL.md`
   - Drop: `/drop .agent/.aider.prompt/documentation/project-README/SKILL.md`
4. After generation, validate the README against project files and present it for user approval.
5. Once approved, choose to save the README directly (requires `/code` mode) or copy it as a markdown block.

> **Note:** See the main `SKILL.md` **Gotchas** section for important handling of manual content and context-management path conventions.

## Best suited for

- New projects needing initial documentation
- Projects with outdated or missing READMEs
- Updating an existing README without overwriting manually maintained content
- Documenting project structure after major refactoring

## Works best with

- Projects with standard package/config files
- Codebases with clear import/dependency structures
- Repositories with existing docs such as requirements, architecture, and user stories
- Projects using common build, test, and run commands
