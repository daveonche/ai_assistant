# Metadata: Dependency Management Prompt

## AI Assistant Compatibility

- Tested With:
  - Aider
  - LLM: Claude 3.5 Sonnet (October 22, 2024 release)
- Potential Compatible Assistants:
  - Other Claude models
  - GitHub Copilot (with modifications)

## SDLC Phase

- Phase: Implementation
- Sub-Phase: Dependency Management
- Workflow: Pre-Implementation Dependency Resolution

## Complexity Rating

- Complexity: High
- Cognitive Load: Significant
- Technical Depth: Deep dependency analysis and compatibility understanding required

## Usage Guidelines

- Prerequisite: Story Analysis Complete
- Requires:
  - Sprint Stories
  - Project Dependency Definition File (package manifests, lock files, etc.)
  - Current Technology Stack Information

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes
- Requires Contextual Awareness: Critical
- Mode Sensitive: Yes (switches between /ask and /code modes)

## Best Practices

- Always verify compatibility with existing dependencies
- Use exact versions, never ranges
- Treat existing dependencies as immutable
- Document all dependency decisions
- Maintain clean separation between analysis and implementation phases
- Update both documentation and dependency files

## Potential Challenges

- Missing or incomplete dependency information
- Version compatibility conflicts
- Circular dependencies
- Peer dependency resolution
- Breaking changes in dependency updates
- Mode switching complexity
- Maintaining consistency across dependency files

## Recommended Mitigation Strategies

- Strict version control (no ranges)
- Comprehensive compatibility testing
- Clear documentation of decisions
- Explicit mode switching instructions
- Verification steps for dependency updates
- Return path validation to implementation

## Version

- Current Version: 1.0.1
- Last Updated: 2026-08-23
- Stability: Experimental

## Integration Points

- Implementation Prompt
- Story Analysis Prompt
- Project Setup Workflow
- Build/Deploy Pipeline Configuration

## Success Metrics

- Clean dependency resolution
- No version conflicts
- Successful return to implementation
- Minimal dependency-related implementation blocks
- Clear documentation trail

## Failure Modes

- Circular dependency requests
- Incompatible version selections
- Incomplete dependency updates
- Lost context during mode switching
- Implementation blocking due to missing dependencies
