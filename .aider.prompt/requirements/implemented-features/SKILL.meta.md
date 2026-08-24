# Implementation Status Analysis Prompt

## Description

Systematically analyzes a codebase to determine the current state of feature implementation, mapping completed, partial, and pending features against project requirements and user stories while establishing implementation priorities.

## Prerequisites

- `docs/requirements.md` (or similar project requirements list)
- `docs/user_stories.md` (or similar user stories list)
- `docs/tech_stack.md` (or similar technology stack information)

## Usage

1. Ensure required project context is available (see Prerequisites)
2. Use command: "$requirements-implemented-features" to start or resume analysis
3. Use command: "$requirements-implemented-features-status" to check progress

## Best suited for

- Implementation progress tracking
- Sprint planning preparation
- Feature completion verification
- Technical dependency mapping
- Project status reporting
- Sprint retrospectives
- Resource allocation planning
- Milestone tracking
- Requirements validation
- Gap analysis

## Output format

- Context validation report
- Structured implementation status:
  - Completed features with evidence
  - Partially implemented features
  - Not yet implemented features
- Prioritized implementation roadmap:
  - Priority categories
  - Feature requirements mapping
  - Implementation rationale
- Progress tracking checkpoints
- Offer to save the generated report to a markdown file
