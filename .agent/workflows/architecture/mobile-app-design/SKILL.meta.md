# Metadata: # Mobile App Design & Implementation Prompt

## Description

Guides the design and implementation of production-grade cross-platform mobile applications that consume the project's API backend, grounded in the mobile framework identified by Project Framework Detection and the tech stack document, enforcing strict planning/implementation phase separation and user-provided branding placeholders.

## AI Assistant Compatibility

- Tested With:
  - Aider
- Potential Compatible Assistants:
  - Should be compatible with most advanced LLMs capable of following complex, multi-step instructions.

## SDLC Phase

- Phase: Design
- Sub-Phase: Mobile App Design & Implementation
- Workflow: Project Scaffolding Sprint Workflow Chain (Phase 4C, conditional); Post-Scaffolding Sprint Workflow Chain (conditional)

## Complexity Rating

- Complexity: High
- Cognitive Load: High
- Technical Depth: Requires understanding of mobile platform design languages, offline/sync architecture, framework detection, and spec-driven design conformance

## Usage Guidelines

- Prerequisite: Project Framework Detection (`.agent/workflows/core/framework-detection/SKILL.md`) and a tech stack document that names a mobile app client consuming the API backend; when a framework is detected, its matching `.agent/specs/<FRAMEWORK>.md`
- Requires:
  - Tech stack document identifying the mobile framework and target platforms
  - Architecture design document (the API backend the app consumes)
  - User-provided mobile requirements (screens, flows, device features, offline needs)
  - Branding values confirmed by the user: `[BRAND_NAME]` and `[BRAND_URL]`
  - Convention references loaded per the routing table in `.agent/AGENTS.md`
- Assumptions: the developer verifies all outputs and approves every change; store publishing happens via `$deployment-release`, never from this skill
- Modes: the prompt manages its own `/ask`/`/code` transitions

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes
- Requires Contextual Awareness: Critical
- Command Driven: Yes (#generate-mobile-app-design, #mobile-app-design-status)
- Phase Separation: Strict planning (/ask) vs. implementation (/code) phases
- Framework-Grounded: Design and output requirements derive from the detected framework spec and tech stack, never hard-coded
- Branding Placeholders: User-provided values substituted everywhere; never hard-coded
- Validation Loop: Explicit checklist before final status
- Status Reporting: #mobile-app-design-status shows progress without activating the workflow

## Command Behavior

- `#generate-mobile-app-design`: Starts or resumes the mobile app design workflow.
- `#mobile-app-design-status`: Shows current progress only and does NOT activate the full workflow. To resume after viewing status, use `#generate-mobile-app-design`.

## Gotchas / Sync Notes

- Conditional phase, mirroring `$architecture-frontend-design`: in the scaffolding chain it is Phase 4C (run only when the tech stack includes a mobile app client); in the post-scaffolding chain it runs only when Phase 2 generated a mobile app story, before that story's analysis.
- In both chains it runs its planning steps only ([STEP 1]-[STEP 3A], including the design-artifact save); implementation flows through the chain's implementation phase following the approved plan.
- The framework decision gate (Flutter / React Native / native) belongs to Phase 3 (tech stack); this skill adapts to the chosen framework and stops if the tech stack names no mobile client.
- Store listing inputs are design outputs; store submission stays in `$deployment-release`.
- Keep workflow instructions authoritative in SKILL.md. Do not duplicate full workflow steps or implementation details here.

## Version

- Current Version: 1.0.0
- Last Updated: 2026-10-05
- Stability: Experimental
- Keep metadata synchronized with changes to SKILL.md; update version and date when SKILL.md changes

## Purpose

This metadata file describes the mobile app design & implementation skill. Workflow instructions, command behavior, and stop points are defined in SKILL.md.

## Sync / Validation Checklist

Before considering this metadata file current, verify:

- [ ] `#mobile-app-design-status` description matches SKILL.md
- [ ] Gotchas / Sync Notes reflect the current SKILL.md gotchas
- [ ] Version and Last Updated are incremented after SKILL.md changes
- [ ] No full workflow steps, command highlights, or implementation details are duplicated here
