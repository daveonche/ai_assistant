# Metadata: Implementation Status Analysis Prompt

## Description
Analyzes the current codebase to determine the implementation status of features, comparing what has been built against project requirements and user stories. It generates a prioritized list of remaining features for the next implementation phase.

## Prompt File

- Path: `.aider.prompt/planning/implementation-analysis/SKILL.md`

## Trigger Commands
- `#analyze-impl`: Starts or resumes the implementation analysis.
- `#analyze-impl-status`: Shows the current progress in the analysis workflow.

## AI Assistant Compatibility

- Tested With:
  - Aider
  - LLM: Claude 3.5 Haiku (October 22, 2024 release)
- Potential Compatible Assistants:
  - Other Claude models
  - GitHub Copilot (with modifications)

## SDLC Phase

- Phase: Planning
- Sub-Phase: Sprint Preparation
- Workflow: Post-Scaffolding Sprint Workflow

## Complexity Rating

- Complexity: Medium
- Cognitive Load: Moderate
- Technical Depth: Comprehensive project understanding required

## Usage Guidelines

- Prerequisite: Project requirements and current user stories available in context
- Previous implementation status report may be used for comparison
- Requires:
  - Project requirements list (e.g., `docs/requirements.md`)
  - Current set of user stories (e.g., `docs/user_stories.md`)
  - Technology stack documentation (e.g., `docs/tech_stack.md`)
  - Previous implementation artifacts

## Modes

- Analysis Mode: `/ask`
- Save Mode: `/code`

## Outputs

- Default Output File: `docs/implementation_status.md`
- Output Behavior:
  - Compare with existing status file
  - Update only changed sections
  - Preserve historical records unless explicitly overwritten

## Workflow Chain

- Current Prompt: `#analyze-impl`
- Next Workflow Step: `#generate-sprint-stories`
- Previous Workflow Step: `#scaffolding-sprint-story` (verify for this repository)

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes
- Requires Contextual Awareness: High

## Best Practices

- Conduct thorough review of existing project state
- Identify both completed and pending features
- Prioritize features based on technical dependencies
- Require at least one source-file citation per feature before classifying it as Complete or Partially Implemented
- Classify features with no source evidence as Not Yet Implemented
- Maintain clear, structured output

## Potential Challenges

- Incomplete project documentation
- Misinterpreting existing implementation status
- Overlooking subtle technical dependencies
- Inconsistent feature tracking

## Recommended Mitigation Strategies

- Maintain comprehensive project documentation
- Regularly update implementation status
- Cross-reference multiple sources of project information
- Validate findings with development team

## Version

- Current Version: 1.1.1
- Last Updated: 2026-08-24
- Stability: Experimental
