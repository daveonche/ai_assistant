# Implementation Status Analysis Prompt

## Description

Read-only analysis prompt that compares the current codebase against project requirements and user stories, reports completed, partially implemented, and not-yet-implemented features with evidence, and produces a prioritized implementation roadmap.

## Prerequisites

The following files must be loaded in the conversation context:

- `docs/requirements.md` and/or `docs/requirements/core_requirements.md`
- `docs/user_stories.md`
- `docs/tech_stack.md`

## Mode

Requires `/ask` mode before activation.

## Usage

1. Ensure mode and required project context are available (see Prerequisites).
2. Use command `$requirements-implemented-features` to start or resume analysis.
3. Use command `$requirements-implemented-features-status` to check progress.

## Output format

- Context validation report:
  - Confirms loaded requirements, user stories, and tech stack files
- Structured implementation status:
  - Completed features with code evidence
  - Partially implemented features
  - Not yet implemented features
- Prioritized implementation roadmap:
  - Priority categories
  - Requirement ID to feature mapping
  - Implementation rationale
- Progress tracking checkpoints
- Optional report save:
  - Default: `docs/implementation_status.md`
  - Existing file handling: overwrite or timestamped copy

## Important Limitation

Strictly read-only analysis. This prompt does not modify code, propose code changes, generate code snippets, or provide coding guidance.

## Best suited for

- Implementation progress tracking
- Sprint planning and backlog preparation
- Dependency and gap analysis
- Release readiness review
- Requirements validation

## Related file

Workflow details are defined in `SKILL.md`.
