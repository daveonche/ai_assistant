# Metadata: Scaffolding Sprint Story Generation Prompt

## AI Assistant Compatibility

- Tested With:
  - Aider
  - LLM: GLM 5.3 Flash (August 27, 2026 release)
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

- Prerequisites (files that must exist, ideally loaded in context):
  - Core requirements — can be generated using `$requirements-initial-project`
  - Technology stack — can be generated using `$architecture-tech-stack`
  - Architecture documentation — can be generated using `$architecture-design`
- Required information (extracted from the prerequisite files):
  - Development environment needs
  - Technical dependencies with exact versions
  - Project structure requirements
- Mode requirements:
  - `/ask` for story generation and review
  - `/code` only when saving the finalized story file

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes
- Requires Contextual Awareness: High
- Command Driven: Yes (`$planning-scaffolding-sprint-story`, `$planning-scaffolding-sprint-story-status`)
- Story Format: Standardized template in `references/story-template.md`, loaded on demand (progressive disclosure)
- Dependency Tracking: Technical sequencing
- Output Format: Markdown sprint stories
- Review Checkpoints:
  - Foundation analysis review
  - Self-validation checklist before presenting the story set
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
| Environment setup completeness | Story MUST-rule for environment setup inclusion |
| Version compatibility | Exact-version pinning with "latest stable" flagging |
| Story scope control | Standard story categories |
| Infrastructure requirements | Verification checkpoints |
| Development workflow definition | Detailed acceptance criteria |
| Tool chain integration | Dedicated developer workflow and build pipeline story categories |
| Configuration management | Configuration documentation |

## Version

- Current Version: 1.2.0
- Last Updated: 2026-08-27
- Stability: Experimental

## Changelog

- 1.2.0: Aligned metadata with SKILL.md refactor (c8c97d0): documented external story template and self-validation checkpoint, clarified prerequisites vs. required information, aligned mitigations with actual skill mechanisms
- 1.1.0: Added logging/config category, Definition of Done, version fallback, ASCII status indicators
- 1.0.1: Initial metadata version
