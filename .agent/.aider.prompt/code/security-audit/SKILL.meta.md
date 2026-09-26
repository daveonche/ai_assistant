# Metadata: # Security Audit Skill

## AI Assistant Compatibility

- Tested With:
  - Aider
  - GLM 5.3 Flash (August 27, 2026 release)
- Potential Compatible Assistants:
  - Other Claude models
  - GitHub Copilot (with modifications)
  - GPT-4

## SDLC Phase

- Phase: Code
- Sub-Phase: Security Audit
- Workflow: On-demand audit (standalone `$code-security-audit` command)

## Complexity Rating

- Complexity: High
- Cognitive Load: High
- Technical Depth: Requires exploit-chain tracing, framework-specific
  control analysis, and reproducible test writing

## Usage Guidelines

- Prerequisite: An audit target (branch diff, PR ref, file/directory
  path, or free-form description)
- Requires:
  - Repository access with `git` (and `gh` for PR targets)
  - Understanding of the app's authentication and tenant model
  - Location of the existing test suite for reproducer tests
  - Explicit user approval before any fix is applied

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes (target resolution depends on the invocation)
- Requires Contextual Awareness: High
- Command Driven: Yes (`$code-security-audit [target]`)
- Diagram Support: None

## Command Behavior

- `$code-security-audit [target]`: Resolves the target, audits it per
  the SKILL.md methodology, and delivers a findings report in the fixed
  output format. On local-branch audits it then offers per-finding
  fixes; fixes require explicit user approval and a passing reproducer
  test.

## Gotchas / Sync Notes

- A finding without a concrete exploit request is not a finding; the
  Calibration section in SKILL.md is authoritative.
- Reproducer tests are mandatory for local-branch audits and must fail
  against the vulnerable code before any fix is applied.
- Never start fixing without explicit per-finding user approval.
- Keep audit methodology, calibration, and output templates
  authoritative in SKILL.md. Do not duplicate them here.
- The sentinel line `<!-- sentinel: code/security-audit -->` must remain
  the final content line of SKILL.md; the orchestrator quotes it to
  detect truncated loads.

## Version

- Current Version: 1.0.0
- Last Updated: 2026-09-26
- Stability: Experimental

## Purpose

This metadata file describes the security audit skill. Audit scope,
methodology, calibration, and output format are defined in SKILL.md.

## Sync / Validation Checklist

Before considering this metadata file current, verify:

- [ ] Command description matches SKILL.md
- [ ] Gotchas / Sync Notes reflect the current SKILL.md gotchas
- [ ] Version and Last Updated are incremented after SKILL.md changes
- [ ] No audit methodology, calibration rules, or output templates are duplicated here
