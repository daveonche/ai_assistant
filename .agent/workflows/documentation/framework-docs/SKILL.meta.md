# Metadata: # Framework Documentation Generator Prompt

## AI Assistant Compatibility

- Tested With:
  - Aider
  - GLM 5.3 Flash (August 27, 2026 release)
- Potential Compatible Assistants:
  - Other Claude models
  - GitHub Copilot (with modifications)
  - GPT-4 (with modifications)

## SDLC Phase

- Phase: Documentation
- Sub-Phase: Framework Documentation Distillation
- Workflow: Post-Scaffolding

## Complexity Rating

- Complexity: High
- Cognitive Load: High
- Technical Depth: Requires understanding of documentation source structures,
  raw-source fetching, sha-based diffing, and multi-file organization

## Usage Guidelines

- Prerequisite: Framework detection via
  `.agent/workflows/core/framework-detection/SKILL.md` (generation);
  an existing distilled tree (update workflow)
- Requires:
  - Network access to `raw.githubusercontent.com` and `api.github.com`
  - A confirmed documentation ref (branch or release tag)
  - The framework's `upgrading.md` and `upgrade-notes/` files on ref bumps

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes
- Requires Contextual Awareness: High
- Command Driven: Yes (#generate-framework-docs, #update-framework-docs,
  #framework-docs-status)
- Diagram Support: None

## Command Behavior

- `#generate-framework-docs`: Starts or resumes the framework documentation
  generation workflow.
- `#update-framework-docs`: Starts or resumes the update workflow (same-ref
  content changes or ref bumps, diffed from the baseline source listing).
- `#framework-docs-status`: Shows current progress only and does NOT activate
  either workflow. To resume after viewing status, use
  `#generate-framework-docs` or `#update-framework-docs`.

## Gotchas / Sync Notes

- Fetch only from raw endpoints (`raw.githubusercontent.com`,
  `api.github.com`); rendered docs pages sit behind Cloudflare bot
  challenges.
- Never guess paths or refs; resolve via the contents API or the saved
  baseline listing.
- Diff updates by `sha`, not `size`.
- Keep workflow instructions authoritative in SKILL.md. Do not duplicate full
  workflow steps or implementation details here.

## Version

- Current Version: 1.0.0
- Last Updated: 2026-09-30
- Stability: Experimental

## Purpose

This metadata file describes the framework documentation generator skill.
Workflow instructions, command behavior, and stop points are defined in
SKILL.md.

## Sync / Validation Checklist

Before considering this metadata file current, verify:

- [ ] `#framework-docs-status` description matches SKILL.md
- [ ] `#update-framework-docs` description matches SKILL.md
- [ ] Gotchas / Sync Notes reflect the current SKILL.md gotchas
- [ ] Version and Last Updated are incremented after SKILL.md changes
- [ ] No full workflow steps, command highlights, or implementation details are duplicated here
