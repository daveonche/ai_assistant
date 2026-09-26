# Metadata: Sprint Story Generation Prompt

## AI Assistant Compatibility

- Tested With:
  - Aider
  - GLM 5.3 Flash (August 27, 2026 release)
- Potential Compatible Assistants:
  - Other Claude models
  - GitHub Copilot (after adapting stop/command syntax)
- Portability Note: The `$`/`#` shorthand commands, `/ask`–`/code` mode switching, and `/read-only` file loading are aider-specific mechanics. Adapt these to equivalent mechanisms before using this prompt with other assistants.

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
- Prompt Commands:
  - `#generate-sprint-stories` - Starts or resumes sprint story generation
  - `#generate-sprint-stories-status` - Shows current progress
- Prerequisites:
  - Project requirements list
  - Previous sprint's user stories (provided via file path or `/read-only`)
  - Implementation status report with prioritized features
  - Technology stack documentation
- Output Artifact:
  - `docs/sprints/sprint_[number]_stories.md` unless a custom path is given

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes
- State Tracking: Explicit Progress Checklist in SKILL.md; the agent updates it as each step completes and uses it to answer `#generate-sprint-stories-status`. If context is lost, the agent asks the user for the last completed step
- Resume/Progress Command: `#generate-sprint-stories-status`
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
- Losing workflow state between sessions

## Recommended Mitigation Strategies

- Conduct detailed technical dependency mapping
- Use consistent story template
- Validate stories against project requirements
- Rely on the built-in self-validation loop (STEP 5), which re-runs after every revision before stories are presented or saved
- Enforce the code-mode save gate: stories are written to disk only after the user switches to `/code` mode and replies `save to file`
- Ensure stories are atomic and implementable
- Cross-reference with implementation status report
- Use `#generate-sprint-stories-status` or ask the user for the last completed step when resuming

## Version

- Current Version: 1.2.1
- Last Updated: 2026-09-26
- Stability: Experimental
