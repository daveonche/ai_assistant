# Sprint Story Generator Prompt

## Description

Guides the systematic generation of sprint user stories through a structured workflow that ensures proper context, technical dependencies, and implementation priorities are considered.

## Usage

1. Use command: "#generate-sprint-stories" to start or resume
2. Use command: "#generate-sprint-stories-status" to check progress

## Prerequisites

Ensure all required project context is available before starting:

- Project requirements list (e.g., `docs/requirements.md`)
- Previous sprint stories (e.g., `docs/sprints/sprint_X_stories.md`)
- Implementation status report (e.g., `docs/implementation_status.md`)
- Technology stack information (e.g., `package.json`, `requirements.txt`)

## Best suited for

- Sprint planning and backlog grooming sessions
- Sequencing feature implementation by technical dependencies
- Sprint backlog creation and story refinement
- Aligning implementation priorities across sprints

## Scope &amp; Limitations

- Focuses strictly on generating stories for the *next* sprint based on technical dependencies.
- Explicitly excludes testing from acceptance criteria, as testing is considered part of the standard "Definition of Done".
- Does not suggest additional stories or implementation details beyond the immediate sprint scope.

## Output format

- Input validation report
- Technical dependency analysis
- Sprint-specific user stories with:
  - Unique story IDs (S\[sprint\].\[number\])
  - User story descriptions
  - Acceptance criteria
  - Dependencies
  - Developer notes
  - Technical rationale
- Progress tracking checkpoints
- Option to save stories to `docs/sprints/sprint_[number]_stories.md`
