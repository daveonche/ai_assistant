# Metadata: # Implementation Prompt

## Description

Guides the implementation of a specific step from a story analysis report, enforcing strict planning and implementation phase separation.

## AI Assistant Compatibility

- Tested With:
  - Aider
  - Claude 3.5 Sonnet (October 22, 2024 release)
- Potential Compatible Assistants:
  - Should be compatible with most advanced LLMs capable of following complex, multi-step instructions.

## SDLC Phase

- Phase: Development
- Sub-Phase: Implementation
- Workflow: Story Step Execution

## Complexity Rating

- Complexity: High
- Cognitive Load: High
- Technical Depth: Requires comprehensive understanding of development practices and dependency management

## Usage Guidelines

- Prerequisite: Story steps report file (e.g., `docs/analysis/S<X.Y>-story-steps.md`)
- Requires:
  - Sprint story documentation
  - Story step requirements
  - Implementation context
  - Approved dependencies or dependency context

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes
- Requires Contextual Awareness: Critical
- Command Driven: Yes (#implement-step S<X.Y> [step-number], #implementation-status S<X.Y> [step-number])
- Phase Separation: Strict planning vs. implementation phases
- Sequential Execution: Enforced step order with validation (step-number presence, range, and order)
- Gotchas: Dedicated section covering new-dependency stop, sequential-order enforcement, and prerequisite verification
- Progress Tracking: Workflow Progress Checklist provided
- Validation Loop: Explicit validate-fix-repeat loop before final status
- User Response Handling: Defined N response path for step requirement confirmation
- Status Reporting: Clarifies omitted step-number behavior before reporting status

## Best Practices

- Strict phase separation
- Step-by-step implementation
- Focused requirement coverage
- Clear implementation planning
- Dependency verification
- Manual verification steps
- Validation loop after implementation (review, test, fix, repeat)
- Sequential progress tracking
- Scope control per step

## Potential Challenges

- Maintaining step boundaries
- Managing implementation scope
- Dependency requirements
- Cross-step dependencies
- Phase separation enforcement
- Requirement verification
- Implementation sequence control

## Recommended Mitigation Strategies

- Clear phase distinction
- Explicit plan approval process
- Strong scope boundaries
- Dependency management integration
- Regular progress verification
- Manual verification steps
- Validation loop before final status
- Sequential implementation enforcement
- Clear completion criteria

## Version

- Current Version: 1.1.0
- Last Updated: 2026-08-26
- Stability: Beta
- Keep metadata synchronized with changes to SKILL.md; update version and date when SKILL.md changes
