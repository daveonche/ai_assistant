# Metadata: Initial Project Requirements Management Prompt

## Description

Generates structured core requirements for a new software project, focusing on aspects that influence architecture and technology choices.

## Usage

1. Activate the workflow using: `$requirements-initial-project`
2. Follow the assistant's mode and context setup instructions.
3. For a new project, enter: `#generate-requirements`
4. To update existing requirements, enter: `#modify-requirements`
5. To check progress, enter: `#requirements-status`

## Best suited for

- New project initialization
- Project scope definition
- Architecture planning phase
- Technology stack selection

## Output format

- Categorized functional and additional requirements
- Unique reference numbers
- Markdown formatted document
- `[Assumed]` markers on assumption-based requirements
- Focus on explicit user needs rather than implementation or architecture details
- Provides input that helps later architecture and technology choices

## AI Assistant Compatibility

- Tested With:
  - Aider
  - Current Claude models available as of the last test date
- Potentially Compatible:
  - Other modern LLMs, but the interactive workflow may require minor prompt adaptations

## SDLC Phase

- Phase: Planning
- Sub-Phase: Requirements Analysis
- Workflow: Initial Requirements Definition

## Complexity Rating

- Complexity: Medium
- Cognitive Load: Moderate
- Technical Depth: Requires understanding of requirements engineering principles

## Usage Guidelines

- Prerequisite: project idea or problem statement
- Helpful inputs:
  - Clear project vision
  - Basic project context
  - Understanding of target users
  - Desired feature set outline
- Note: The workflow can also start from a minimal or ambiguous idea and ask clarifying questions.
- Note: This prompt requires interactive, step-by-step execution and involves switching between `/ask` and `/code` modes as directed by the workflow.

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes
- Requires Contextual Awareness: Moderate
- Command Driven: Yes (#generate-requirements, #modify-requirements, #requirements-status)

## Best Practices

- Focus on explicit project needs
- Maintain clear requirement categorization
- Use consistent ID formatting
- Keep requirements atomic
- Avoid technical implementation details
- Mark assumptions clearly with the `[Assumed]` prefix
- Only mark assumptions when the user explicitly chooses the assumption option
- Support iterative refinement

## Potential Challenges

- Ambiguous project ideas
- Scope creep in requirements
- Maintaining requirement atomicity
- Managing requirement dependencies
- Balancing detail vs. clarity
- Tendency to drift into implementation or technical details

## Recommended Mitigation Strategies

- Structured requirement ID system
- Clear assumption marking
- Interactive refinement process
- Explicit user confirmation steps
- Show the complete updated requirements list after every modification
- Separate functional/additional requirements

## Inputs

- Project idea or problem statement
- Optional: existing requirements file for modification
- Optional: category names and requirement descriptions
- Optional: custom output path

## Outputs

- Markdown requirements document
- Requirement IDs
- Optional custom save location

## Version

- Current Version: 1.2.0
- Last Updated: 2026-08-24
- Stability: Beta
- Changelog:
  - 1.2.0: Aligned commands, clarified assumptions, improved modification loop
  - 1.1.0: Initial interactive requirements workflow
