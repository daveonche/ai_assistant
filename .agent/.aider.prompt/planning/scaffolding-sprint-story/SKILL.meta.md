# Metadata: Scaffolding Sprint Story Generation Prompt

## AI Assistant Compatibility

- Tested With:
  - Aider
  - Claude 3.5 Sonnet (October 22, 2024 release)
- Potential Compatible Assistants:
  - Other Claude models
  - GitHub Copilot — requires prompt reformatting
  - GPT-4 — requires command-handoff adaptation

## SDLC Phase

- Phase: Planning
- Sub-Phase: Sprint Scaffolding
- Workflow: Initial Project Setup

## Complexity Rating

- Complexity: High
- Cognitive Load: High
- Technical Depth: Requires comprehensive understanding of project initialization and technical dependencies

## Usage Guidelines

- Prerequisites:
  - Core requirements — can be generated using `$requirements-initial-project`
  - Technology stack — can be generated using `$architecture-tech-stack`
  - Architecture documentation — can be generated using `$architecture-design`
- Requires:
  - Technology stack documentation
  - Architecture documentation
  - Development environment needs
  - Technical dependencies
  - Project structure requirements
- Mode requirements:
  - `/ask` for story generation and review
  - `/code` only when saving the finalized story file

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes
- Requires Contextual Awareness: High
- Command Driven: Yes (`$planning-scaffolding-sprint-story`, `$planning-scaffolding-sprint-story-status`)
- Story Format: Standardized templates
- Dependency Tracking: Technical sequencing
- Output Format: Markdown sprint stories
- Review Checkpoints:
  - Foundation analysis review
  - Story set review before saving
- Saving Mode: `/code`

## Best Practices

- Focus on foundational setup
- Strict technical sequencing
- Clear story dependencies
- Version specification
- Environment setup inclusion
- Verification checkpoints
- Core architecture focus
- Development workflow establishment

## Challenges and Mitigations

| Challenge | Mitigation |
|---|---:|
| Technical dependency ordering | Clear dependency graphing |
| Environment setup completeness | Environment setup checklist |
| Version compatibility | Version specification guidance |
| Story scope control | Standard story categories |
| Infrastructure requirements | Verification checkpoints |
| Development workflow definition | Detailed acceptance criteria |
| Tool chain integration | Tool chain verification |
| Configuration management | Configuration documentation |

## Version

- Current Version: 1.1.0
- Last Updated: 2026-08-24
- Stability: Experimental

## Changelog

- 1.1.0: Added logging/config category, Definition of Done, version fallback, ASCII status indicators
- 1.0.1: Initial metadata version
