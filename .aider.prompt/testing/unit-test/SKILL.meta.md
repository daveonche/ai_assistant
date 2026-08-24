# Metadata: # Unit Test Generation Prompt

## Description

Creates story-step-aware unit tests that map directly to `Must Support` requirements and stay inside step scope. Activated with `#generate-tests S<X.Y> [step-number]`; progress can be checked with `#test-status`.

## Usage

1. Have the story steps report for the target story step.
2. Provide implementation files for that step.
3. Provide any existing test files or confirm none exist.
4. Use: `#generate-tests S<X.Y> [step-number]`

## Best suited for

- Story-step unit testing driven by `Must Support` items
- New component testing
- Coverage improvement
- Test maintenance
- TDD workflows
- Quality assurance
- Regression prevention

## Output format

- Test scenario analysis
- Test suites
- Test cases
- Setup/teardown
- Assertions
- Manual verification mappings
- Exact test execution commands
- Test execution output and status
- Final test implementation summary

## AI Assistant Compatibility

- Tested With:
  - Aider
  - LLM: Claude 3.5 Sonnet (October 22, 2024 release)
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
- Mode switching: The workflow requires switching between `/ask` and `/code` modes for test generation and implementation.

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes
- Requires Contextual Awareness: Critical
- Command Driven: Yes (`#generate-tests`, `#test-status`)
- Mode Dependent: Yes (`/ask`, `/code`)

## Best Practices

- Check test applicability before generating tests
- Analyze test environment before implementation
- Map tests directly to story requirements
- Keep each test independent and side-effect-free
- Implement and verify one test at a time
- Verify test execution results
- Maintain strict scope adherence
- Follow project-specific testing patterns
- Handle dependencies systematically
- Allow skip-execution mode for external environments

## Potential Challenges

- Missing test environment setup
- Incorrect test framework assumptions
- Scope creep in test coverage
- Dependency management complexity
- Test execution verification
- Manual vs. automated test balance
- Mixed `/ask` and `/code` mode switching

## Recommended Mitigation Strategies

- Strict test-to-requirement mapping
- Explicit environment verification steps
- Clear dependency management process
- Step-by-step test implementation
- Regular test status checks
- Support for manual test execution
- Clear mode-switch instructions

## Version

- Current Version: 1.0.1
- Last Updated: 2026-08-24
- Stability: Experimental
