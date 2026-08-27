# Metadata: Initial Project Requirements Management Prompt

## Description

Generates structured core requirements for a new software project, focusing on aspects that influence architecture and technology choices.

## Usage

1. Activate the workflow using: `$requirements-initial-project`
2. Follow the assistant's mode and context setup instructions.
3. For a new project, enter: `#generate-requirements`
4. To update existing requirements, enter: `#modify-requirements`
5. To check progress, enter: `#requirements-status`

Note: `$requirements-initial-project` activates the workflow through the orchestrator; the `#`-prefixed commands are in-workflow commands used after activation.

## Best suited for

- New project initialization
- Project scope definition
- Architecture planning phase
- Technology stack selection
- Informing later architecture and technology choices

## Output format

- Categorized functional and additional requirements
- Unique reference numbers
- Markdown formatted document
- `[Assumed]` markers on assumption-based requirements
- Focus on explicit user needs rather than implementation or architecture details

## AI Assistant Compatibility

- Tested With:
  - Aider
  - LLM: GLM 5.3 Flash (August 27, 2026 release)
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
- Command Driven: Yes (`#generate-requirements`, `#modify-requirements`, `#requirements-status`)

## Best Practices

- Focus on explicit project needs
- Support iterative refinement

Note: Detailed rules (atomicity, `[Assumed]` marking, ID uniqueness, showing the complete list after each change) are enforced by SKILL.md's Critical Rules and Gotchas and are not repeated here.

## Potential Challenges

- Ambiguous project ideas
- Scope creep in requirements
- Maintaining requirement atomicity
- Managing requirement dependencies
- Balancing detail vs. clarity
- Tendency to drift into implementation or technical details

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
- Last Updated: 2026-08-27
- Stability: Beta
- Changelog:
  - 1.2.0: Added validation loops, checklist-based status reporting, `[CAT]` abbreviation rules, and a worked example; documented the command-prefix mismatch in Gotchas (commands intentionally not renamed); applied Markdown formatting fixes
  - 1.1.0: Initial interactive requirements workflow
