# Metadata: # Post-Scaffolding Sprint Workflow Chain Prompt

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
- Sub-Phase: Post-Scaffolding / Feature Development
- Workflow: Chained AI-assisted feature planning and implementation (activated via `$workflows-post-scaffolding-chain`)

## Complexity Rating

- Complexity: High
- Cognitive Load: High
- Technical Depth: Requires coordination across implementation analysis, story generation, story analysis, coding, and testing prompts

## Usage Guidelines

- Prerequisite: Completed initial project scaffolding (Sprint 1)
- Requires:
  - Existing project structure, dependencies, and core technologies
  - Previous sprint user stories and project requirements
- Assumptions: the AI can handle file operations; the developer verifies all outputs; each phase completes fully before the chain proceeds
- Modes: orchestration runs in the current mode; phase prompts manage their own `/ask`/`/code` transitions

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes
- Requires Contextual Awareness: High
- Command Driven: Yes ($workflows-post-scaffolding-chain plus per-phase commands)
- Diagram Support: None
- Chained Workflow: Yes

## Command Behavior

- `$workflows-post-scaffolding-chain`: Starts or resumes the chain — presentation of the phase command table, phase selection, on-demand loading of the selected phase's SKILL.md, then a [STOP] waiting for the user to run a phase command.
- Phase commands (`$planning-implementation-analysis`, `$planning-sprint-story`, `$planning-story-analysis S<X.Y>`, `$code-implementation S<X.Y> [step-number]`, `$testing-unit-test S<X.Y> [step-number]`, `$code-dependency-management`): activate the corresponding phase. The authoritative command table lives in SKILL.md.

## Gotchas / Sync Notes

- Chain integrity requires each phase's output to be available or approved before proceeding to the next phase; never auto-progress — always wait for the user to select a phase.
- `S<X.Y>` story IDs must come from Phase 2; do not guess them.
- `$code-dependency-management` is conditional: activate it only when a new dependency is identified during Phase 4A.
- Load phase prompts on demand via their phase commands to avoid context overload.
- Scope stays within the current sprint; later features are out of chain scope.
- The phase sequence, Input/Output Chain, verification points, and chain best practices are authoritative in SKILL.md. Do not duplicate them here.
- The sentinel line `<!-- sentinel: workflows/post-scaffolding-chain -->` must remain the final content line of SKILL.md; the orchestrator quotes it to detect truncated loads.

## Version

- Current Version: 1.2.0
- Last Updated: 2026-09-26
- Stability: Experimental

## Purpose

This metadata file describes the post-scaffolding workflow chain. The phase sequence, Input/Output Chain, chain dependencies, and verification points are defined in SKILL.md.

## Sync / Validation Checklist

Before considering this metadata file current, verify:

- [ ] Command Behavior matches the phase commands in SKILL.md
- [ ] Gotchas / Sync Notes reflect the current SKILL.md gotchas
- [ ] Version and Last Updated are incremented after SKILL.md changes
- [ ] No phase details, chain dependencies, or verification points are duplicated here
