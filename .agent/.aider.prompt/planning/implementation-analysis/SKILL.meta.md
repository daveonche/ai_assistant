# Metadata: Implementation Status Analysis Prompt

## Description

Analyzes the current codebase to determine the implementation status of features, comparing what has been built against project requirements and user stories. It generates a prioritized list of remaining features for the next implementation phase.

## Prompt File

- Path: `.agent/.aider.prompt/planning/implementation-analysis/SKILL.md`

## Trigger Commands

- `$planning-implementation-analysis`: Starts or resumes the implementation analysis.
- `$planning-implementation-analysis status`: Shows the current progress in the analysis workflow.

## AI Assistant Compatibility

- Tested With:
  - Aider
  - LLM: GLM 5.3 Flash (August 27, 2026 release)

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
  - Project requirements list (e.g., `docs/requirements/core_requirements.md`)
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
- Output Template: The report structure (status classifications, feature entries, source-file citations) is defined in `SKILL.md`; treat it as the single source of truth for output format.

## Workflow Chain

- Current Prompt: `$planning-implementation-analysis`
- Next Workflow Step: `$planning-sprint-story`
- Previous Workflow Step: `$planning-scaffolding-sprint-story`

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes
- Requires Contextual Awareness: High

## Best Practices

- Conduct thorough review of existing project state
- Identify both completed and pending features
- Prioritize features based on technical dependencies
- Maintain clear, structured output
- Validate findings with the development team before acting on them

## Gotchas

- Never classify a feature as Complete or Partially Implemented without at least one source-file citation; features with no source evidence must be classified Not Yet Implemented.
- Documentation can drift: `docs/requirements/core_requirements.md` and `docs/user_stories.md` may describe features that no longer match the code. Verify claims against source files, not documentation alone.
- Features are often split across multiple files (models, handlers/views, templates). Search broadly before marking something Partially Implemented.
- Re-running the analysis must preserve historical records in `docs/implementation_status.md` unless the user explicitly asks to overwrite them.

## Version

- Current Version: 1.2.0
- Last Updated: 2026-08-27
- Stability: Experimental
