# Metadata: # Project Scaffolding Sprint Workflow Chain Prompt

## AI Assistant Compatibility

- Tested With:
  - Aider
  - Implementation Prompt: GLM 5.3 Flash (August 27, 2026 release)
  - Other Workflow Prompts: GLM 5.3 Flash (August 27, 2026 release)
- Potential Compatible Assistants:
  - Other Claude models
  - GitHub Copilot (with modifications)
  - GPT-4 (with workflow adaptation)

## SDLC Phase

- Phase: Planning & Implementation
- Sub-Phase: Project Scaffolding
- Workflow: Chained AI-assisted scaffolding (activated via `$workflows-project-scaffolding-chain`)

## Complexity Rating

- Complexity: High
- Cognitive Load: High
- Technical Depth: Requires coordination across vision, requirements, architecture, planning, coding, and testing prompts

## Usage Guidelines

- Prerequisite: Project idea or problem statement; no prior project structure, dependencies, or core technologies
- Requires:
  - Understanding of chained workflow dependencies
  - Ability to load and run phase-specific prompts on demand
- Assumptions: the AI can handle file operations; the developer verifies all outputs; each phase completes fully before the chain proceeds
- Modes: orchestration runs in the current mode; phase prompts manage their own `/ask`/`/code` transitions

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes (fresh-start vs. resume branching)
- Requires Contextual Awareness: High
- Command Driven: Yes ($workflows-project-scaffolding-chain plus per-phase commands)
- Diagram Support: None
- Chained Workflow: Yes

## Command Behavior

- `$workflows-project-scaffolding-chain`: Starts or resumes the chain — fresh/resume check, presentation of the phase command table, phase selection, on-demand loading of the selected phase's SKILL.md, then a [STOP] waiting for the user to run a phase command.
- Phase commands (`$planning-vision-statement`, `$requirements-initial-project`, `$architecture-tech-stack`, `$architecture-design`, `$planning-scaffolding-sprint-story`, `$planning-story-analysis S<X.Y>`, `$code-implementation S<X.Y> [step-number]`, `$testing-unit-test S<X.Y> [step-number]`, `$code-dependency-management`): activate the corresponding phase. The authoritative command table lives in SKILL.md.

## Gotchas / Sync Notes

- Chain integrity requires each phase's output to be available or approved before proceeding to the next phase; never auto-progress — always wait for the user to select a phase.
- Load phase prompts on demand via their phase commands to avoid context overload.
- Scope stays within initial scaffolding; later features are out of chain scope.
- The phase sequence, Input/Output Chain, Chain Dependencies, and verification points are authoritative in SKILL.md. Do not duplicate them here.
- The sentinel line `<!-- sentinel: workflows/project-scaffolding-chain -->` must remain the final content line of SKILL.md; the orchestrator quotes it to detect truncated loads.

## Version

- Current Version: 1.1.0
- Last Updated: 2026-09-26
- Stability: Experimental

## Purpose

This metadata file describes the project scaffolding workflow chain. The phase sequence, Input/Output Chain, chain dependencies, and verification points are defined in SKILL.md.

## Sync / Validation Checklist

Before considering this metadata file current, verify:

- [ ] Command Behavior matches the phase commands in SKILL.md
- [ ] Gotchas / Sync Notes reflect the current SKILL.md gotchas
- [ ] Version and Last Updated are incremented after SKILL.md changes
- [ ] No phase details, chain dependencies, or verification points are duplicated here
