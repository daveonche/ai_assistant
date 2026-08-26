# Metadata: Vision Statement Generation Prompt (v1.1.0)

## AI Assistant Compatibility

- Tested With:
  - Aider
  - Claude 3.5 Sonnet (October 22, 2024 release)
  - GPT-4o mini
- Potential Compatible Assistants:
  - Claude models
  - Other GPT-4o models
  - GitHub Copilot (with modifications: requires explicit mode management equivalent to `/ask` and `/code`)

## SDLC Phase

- Phase: Planning
- Sub-Phase: Vision Definition
- Workflow: Initial Project Vision

## Complexity Rating

- Complexity: Medium
- Cognitive Load: Moderate
- Technical Depth: Focuses on business/user value over technical details

## Usage Guidelines

- Prerequisite: Project concept or idea
- Required User Inputs:
  - Problem statement / purpose
  - Target audience
  - Value proposition
  - Key feature concepts
  - Future growth vision
- Mode Requirements:
  - `/ask` for generation/modification
  - `/code` for saving
- File Dependency:
  - Existing vision file (`docs/vision/project_vision.md`) must be loaded for `#modify-vision`

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes (conversation-scoped only)
- Persistence: None
- Requires Contextual Awareness: Moderate
- Command Driven: Yes (#generate-vision, #modify-vision, #vision-status)
- Modification Workflow: Yes (Interactive loop for updating specific sections)
- Example Based: Provides clear examples for each section
- Interactive Guidance: Multi-option input approach

## Best Practices

- Focus on business/user value
- Clear section separation
- Example-driven guidance
- Value-oriented content
- Future vision inclusion
- Technical neutrality
- Structured documentation
- Interactive refinement
- Require explicit user approval of full draft before saving
- Verify `/ask` mode before beginning workflows
- Confirm existing file is loaded before modifying
- Keep modifications section-scoped

## Challenges & Mitigations

| Challenge | Mitigation |
| --- | --- |
| Maintaining non-technical focus | Example-based guidance |
| Balancing detail level | Structured section format |
| Future vision clarity | Clear technical boundaries |
| Value proposition definition | Interactive refinement process |
| Feature abstraction level | Multiple input options |
| Audience specificity | Value-focused questions |
| Vision scope control | Consistent structure |
| Technical detail avoidance | Regular alignment checks |
| Losing generated draft when switching from `/ask` to `/code` | Output full markdown content at save time to avoid context loss |
| Saving when the target file already exists | Require explicit overwrite or rename confirmation before writing |
| Modifying a vision file that is not loaded in context | Require `/read-only` + user confirmation before modification |
| Accidentally changing more than one section during `#modify-vision` | Restrict `#modify-vision` edits to the selected section only |

## Outputs

- Default File: `docs/vision/project_vision.md`
- Format: Markdown
- Structure: Purpose, Target Users, Value Proposition, Key Features, Future Vision

## Related Skills

- Parent workflow: `workflows/project-scaffolding-chain`
- `requirements/initial-project`
- `architecture/design`
- `planning/story-analysis`

## Version

- Current Version: 1.1.0
- Last Updated: 2026-08-26
- Stability: Beta
