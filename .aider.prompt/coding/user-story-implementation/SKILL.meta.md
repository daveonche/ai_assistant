# User Story Implementation Role Prompt

## Description

Guides the systematic implementation of user stories through a structured workflow that ensures stable, incremental development with proper dependency management, version control, and acceptance criteria validation.

## Usage

1. Ensure the following context is available:
   - User story to be implemented
   - Project technology stack information
   - Current dependencies and versions
2. Use command: "#implement-story S<X.Y>" to start or resume implementation
   - Replace X.Y with specific story number (e.g., S2.1)
3. Use command: "#implement-story-status" to check progress
4. After completion, use the /drop command to remove the prompt from context and free up tokens.

## Best suited for

- Feature implementation
- Dependency management
- Version control enforcement
- Incremental development
- Acceptance criteria validation
- Technical debt prevention
- Project stability maintenance
- Systematic testing workflows
- Development process standardization
- Implementation verification
- Compatibility assurance
- Package version management

## Output format

- Story validation report
- Technical requirements analysis:
  - Ecosystem detection
  - Core tool verification
  - Dependency analysis matrix
  - Version lock enforcement
- Implementation plan:
  - Incremental breakdown
  - Functionality mapping
  - Criteria coverage
- Implementation tracking:
  - Increment progress
  - Test proposals
  - Revision handling
  - Verification checkpoints
  - Stability confirmations
- Completion verification:
  - Acceptance criteria validation
  - Dependency confirmation
  - Implementation verification
