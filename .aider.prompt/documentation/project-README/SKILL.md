# Project README Generator

When asked to generate or update a README, follow these steps:

1. Scan all available project files and documentation
2. Select the most relevant files and documentation
3. Analyze code structure, dependencies, and configuration files
4. Identify core technologies from package files and code imports
5. Map component relationships through imports and architecture patterns
6. Extract build and run instructions from configuration files
7. Check if a `README.md` already exists. If it does, analyze its current structure and content to preserve manual sections or update outdated information.
8. Generate a comprehensive README using this structure:

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

[STEP 3] File Output:
1. Ask the user if they want to save the file directly or output the markdown block to copy.
2. If saving directly, instruct the user to enter `/code` mode and say "save to file".
3. If outputting, provide the complete markdown block.

[STOP - End of workflow. Ask the user if they want to drop the prompt file from context using `/drop .aider.prompt/documentation/project-README/SKILL.md`.]
