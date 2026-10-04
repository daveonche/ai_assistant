# Metadata: # Frontend Design & Implementation Prompt

## Description

Guides the design and implementation of distinctive, production-grade frontend interfaces grounded in the repo's detected framework and the referenced specs loaded during the session, enforcing strict planning/implementation phase separation and user-provided branding placeholders.

## AI Assistant Compatibility

- Tested With:
  - Aider
- Potential Compatible Assistants:
  - Should be compatible with most advanced LLMs capable of following complex, multi-step instructions.

## SDLC Phase

- Phase: Design
- Sub-Phase: Frontend Design & Implementation
- Workflow: Post-Scaffolding Sprint Workflow Chain

## Complexity Rating

- Complexity: High
- Cognitive Load: High
- Technical Depth: Requires comprehensive understanding of frontend aesthetics, framework detection, and spec-driven design conformance

## Usage Guidelines

- Prerequisite: Project Framework Detection (`.agent/workflows/core/framework-detection/SKILL.md`) and, when a framework is detected, its matching `.agent/specs/<FRAMEWORK>.md`
- Requires:
  - User-provided frontend requirements (component, page, dashboard, or application)
  - Branding values confirmed by the user: `[BRAND_NAME]` and `[BRAND_URL]` (plus `[BRAND_INITIALS]` when a monogram pattern is chosen)
  - Convention references loaded per the routing table in `.agent/AGENTS.md`
  - Technical constraints (framework, performance, accessibility)

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes
- Requires Contextual Awareness: Critical
- Command Driven: Yes (#generate-frontend-design, #frontend-design-status)
- Phase Separation: Strict planning (/ask) vs. implementation (/code) phases
- Framework-Grounded: Design and output requirements derive from the detected framework spec, never hard-coded
- Branding Placeholders: User-provided values substituted everywhere; never hard-coded
- Validation Loop: Explicit checklist before final status
- Status Reporting: #frontend-design-status shows progress without activating the workflow

## Command Behavior

- `#generate-frontend-design`: Starts or resumes the frontend design workflow.
- `#frontend-design-status`: Shows current progress only and does NOT activate the full workflow. To resume after viewing status, use `#generate-frontend-design`.

## Gotchas / Sync Notes

- Framework detection is read-only: it informs guidance only and never modifies or generates project files.
- Never assume the repo's framework or UI stack; confirm it with the user before design decisions.
- Output requirements (entry file name, project layout) come from the detected framework spec, never from hard-coded assumptions.
- Branding is built from user-provided placeholders; never ship a literal placeholder or a hard-coded brand.
- Keep workflow instructions authoritative in SKILL.md. Do not duplicate full workflow steps or implementation details here.

## Version

- Current Version: 1.0.0
- Last Updated: 2026-10-04
- Stability: Experimental
- Keep metadata synchronized with changes to SKILL.md; update version and date when SKILL.md changes

## Purpose

This metadata file describes the frontend design & implementation skill. Workflow instructions, command behavior, and stop points are defined in SKILL.md.

## Sync / Validation Checklist

Before considering this metadata file current, verify:

- [ ] `#frontend-design-status` description matches SKILL.md
- [ ] Gotchas / Sync Notes reflect the current SKILL.md gotchas
- [ ] Version and Last Updated are incremented after SKILL.md changes
- [ ] No full workflow steps, command highlights, or implementation details are duplicated here
