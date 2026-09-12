# Unit Test Generation Prompt Metadata

## AI Assistant Compatibility

- Tested With:
  - Aider
  - LLM: GLM 5.3 Flash (August 27, 2026 release)
- Last Validated Model: Claude 3.5 Sonnet
- Potential Compatible Assistants:
  - Other Claude models
  - GitHub Copilot (with modifications)

## SDLC Phase

- Phase: Development
- Sub-Phase: Testing
- Workflow: Step-by-Step Test Implementation

## Complexity Rating

- Complexity: High
- Cognitive Load: High
- Technical Depth: Requires detailed understanding of testing frameworks and project context

## Usage Guidelines

- Prerequisite: Story steps report
- Requires:
  - Implementation files for specific step
  - Existing test files (if any)
  - Project structure context
  - Testing environment details
- Uses progressive disclosure: core SKILL.md + references/gotchas.md, references/templates.md, references/rules.md

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes
- Requires Contextual Awareness: Critical
- Command Driven: Yes ($testing-unit-test, $testing-unit-test-status)

## Best Practices

- Analyze test environment before implementation
- Map tests directly to story requirements
- Verify test execution results
- Maintain strict scope adherence
- Follow project-specific testing patterns
- Handle dependencies systematically
- Use explicit checklists to track progress during major workflow steps
- Provide recommended defaults for decision menus while allowing overrides

## Potential Challenges

- Missing test environment setup
- Incorrect test framework assumptions
- Scope creep in test coverage
- Dependency management complexity
- Test execution verification
- Manual vs. automated test balance
- Reference files falling out of sync with core SKILL.md

## Recommended Mitigation Strategies

- Strict test-to-requirement mapping
- Explicit environment verification steps
- Clear dependency management process
- Step-by-step test implementation
- Regular test status checks
- Support for manual test execution
- Load references on demand and review them when core workflow changes

## Version

- Current Version: 1.1.0
- Last Updated: 2026-08-26
- Stability: Experimental
