# Metadata: Vision Statement Generation Prompt (v1.1.0)

## AI Assistant Compatibility

- Tested With:
  - Aider
  - Claude 3.5 Sonnet (October 22, 2024 release)
  - GPT-4o mini
- Potential Compatible Assistants:
  - Claude models
  - Other GPT-4o models
  - GitHub Copilot (with modifications: may require manual handling of /ask and /code commands)

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
- Default Output Location: `docs/vision/project_vision.md` (unless custom path is specified)

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

## Potential Challenges

- Maintaining non-technical focus
- Balancing detail level
- Future vision clarity
- Value proposition definition
- Feature abstraction level
- Audience specificity
- Vision scope control
- Technical detail avoidance
- Losing generated draft when switching from `/ask` to `/code`
- Saving when the target file already exists
- Modifying a vision file that is not loaded in context
- Accidentally changing more than one section during `#modify-vision`

## Recommended Mitigation Strategies

- Example-based guidance
- Structured section format
- Clear technical boundaries
- Interactive refinement process
- Multiple input options
- Value-focused questions
- Consistent structure
- Regular alignment checks
- Output full markdown content at save time to avoid context loss
- Require explicit overwrite or rename confirmation before writing
- Require `/read-only` + user confirmation before modification
- Restrict `#modify-vision` edits to the selected section only

## Outputs

- Default File: `docs/vision/project_vision.md`
- Format: Markdown
- Structure: Purpose, Target Users, Value Proposition, Key Features, Future Vision

## Related Skills

- `requirements/initial-project`
- `architecture/design`
- `planning/story-analysis`

## Version

- Current Version: 1.1.0
- Last Updated: 2026-08-24
- Stability: Beta
