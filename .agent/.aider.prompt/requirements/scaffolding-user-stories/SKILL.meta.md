# Project Scaffolding Story Generator

## Description

Generates a minimal set of user stories needed to create a basic working shell of an application based on defined architecture and tech stack.

## Usage

1. Have requirements, architecture, tech stack, and component structure defined
2. Activate using the shorthand command: `$requirements-scaffolding-user-stories`
   (Or manually load: `/read-only .agent/.aider.prompt/requirements/scaffolding-user-stories/SKILL.md`)

## Best suited for

- Project initialization
- Basic app structure setup
- Framework installation
- Minimal running application shell
- Development environment setup

## Output format

- 2-3 user stories
- Detailed acceptance criteria
- Technical implementation notes
- Clear definition of done
- Strictly structural scope: no persistence, security, or business logic; pinned dependency versions
- Saved to `docs/sprints/sprint_0_stories.md` (or user-specified path)
