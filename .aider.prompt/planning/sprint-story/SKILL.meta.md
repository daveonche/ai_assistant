# Metadata: # Sprint Story Generation Prompt

## AI Assistant Compatibility

- Tested With:
  - Aider
  - LLM: Claude 3.5 Haiku or newer
- Potential Compatible Assistants:
  - Other Claude models
  - GitHub Copilot (with modifications)

## SDLC Phase

- Phase: Planning
- Sub-Phase: Sprint Preparation
- Workflow: Post-Scaffolding Sprint Workflow (typically follows the Scaffolding Sprint Workflow)

## Complexity Rating

- Complexity: Medium
- Cognitive Load: Moderate
- Technical Depth: Requires comprehensive project understanding

## Usage Guidelines

- Shorthand Command: `$planning-sprint-story`
- Prerequisite: Implementation status report
- Requires:
  - Project requirements list
  - Previous sprint's user stories (must be provided via `/read-only`)
  - Technology stack documentation
  - Implementation priority mapping

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes
- Requires Contextual Awareness: Critical

## Best Practices

- Analyze technical dependencies thoroughly
- Map features to minimal implementable units
- Ensure stories align with project requirements
- Maintain clear, actionable story descriptions
- Prioritize features based on technical dependencies

## Potential Challenges

- Misinterpreting technical dependencies
- Creating overly complex or vague stories
- Overlooking critical implementation constraints
- Inconsistent story granularity

## Recommended Mitigation Strategies

- Conduct detailed technical dependency mapping
- Use consistent story template
- Validate stories against project requirements
- Ensure stories are atomic and implementable
- Cross-reference with implementation status report

## Version

- Current Version: 1.0.0
- Last Updated: 2026-08-24
- Stability: Experimental
