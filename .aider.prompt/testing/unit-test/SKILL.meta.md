# Metadata: # Unit Test Generation Prompt

## AI Assistant Compatibility
- Tested With: 
  * Aider
  * LLM: Claude 3.5 Sonnet (October 22, 2024 release)
- Potential Compatible Assistants: 
  * Other Claude models
  * GitHub Copilot (with modifications)

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
  * Implementation files for specific step
  * Existing test files (if any)
  * Project structure context
  * Testing environment details

## Prompt Characteristics
- Input Driven: Yes
- State Dependent: Yes
- Requires Contextual Awareness: Critical
- Command Driven: Yes (#generate-tests, #test-status)

## Best Practices
- Analyze test environment before implementation
- Map tests directly to story requirements
- Verify test execution results
- Maintain strict scope adherence
- Follow project-specific testing patterns
- Handle dependencies systematically

## Potential Challenges
- Missing test environment setup
- Incorrect test framework assumptions
- Scope creep in test coverage
- Dependency management complexity
- Test execution verification
- Manual vs. automated test balance

## Recommended Mitigation Strategies
- Strict test-to-requirement mapping
- Explicit environment verification steps
- Clear dependency management process
- Step-by-step test implementation
- Regular test status checks
- Support for manual test execution

## Version
- Current Version: 1.0.0
- Last Updated: 2024-12-02
- Stability: Experimental
