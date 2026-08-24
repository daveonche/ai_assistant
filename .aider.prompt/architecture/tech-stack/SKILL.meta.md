# Metadata: # Technology Stack Generation Prompt

## AI Assistant Compatibility

- Tested With:
  - Aider
  - Claude 3.5 Sonnet (October 22, 2024 release)
- Potential Compatible Assistants:
  - Other Claude models
  - GitHub Copilot (with modifications)
  - GPT-4 (with adaptations)

## SDLC Phase

- Phase: Planning
- Sub-Phase: Technology Selection
- Workflow: Initial Project Setup

## Complexity Rating

- Complexity: High
- Cognitive Load: High
- Technical Depth: Requires extensive knowledge of technology ecosystems and version compatibility

## Usage Guidelines

- Prerequisite: Project requirements list
- Requires:
  - Existing dependency files (if any)
  - Application type understanding
  - Core technology preferences
  - Capability requirements
  - Version compatibility constraints

## Purpose
This prompt guides the user through defining a compatible, version-locked technology stack based on project requirements and user preferences. It also supports modifying an existing stack.

## Usage
Use this prompt when starting a new project to select the core technology, frameworks, and dependencies, or when you need to modify an existing technology stack.

### Commands
- `#generate-stack`: Starts new technology stack generation.
- `#modify-stack`: Allows modification of an existing tech stack.
- `#stack-status`: Shows current progress in stack generation workflow.

### Workflow
1. **Mode Verification**: Ensure you are in `/ask` mode.
2. **Requirements Verification**: Check for project requirements and existing dependency files.
3. **Application Type Assessment**: Determine the type of application being built.
4. **Core Technology Selection**: Select the core technology and version.
5. **Dependency Analysis**: Identify required capabilities and recommend or select dependencies.
6. **Compatibility Verification**: Verify compatibility between core technology and dependencies.
7. **Generate Documentation and Dependency Files**: Create the tech stack documentation and appropriate dependency files.
8. **Save Files**: Switch to `/code` mode to save the generated files.

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes
- Requires Contextual Awareness: High
- Command Driven: Yes (#generate-stack, #modify-stack, #stack-status)
- Multi-File Generation: Yes (documentation and dependency files)

## Best Practices

- Use exact version numbers
- Verify all compatibility
- Document selection rationale
- Generate appropriate dependency files
- Maintain version consistency
- Support multiple technology ecosystems
- Enable user preference consideration
- Conduct thorough impact analysis

## Potential Challenges

- Version compatibility conflicts
- Dependency chain resolution
- Cross-platform compatibility
- Technology ecosystem constraints
- Maintaining version consistency
- Managing user preferences vs technical fit
- Handling multiple dependency file formats

## Recommended Mitigation Strategies

- Strict version locking
- Comprehensive compatibility checks
- Clear documentation requirements
- Structured modification process
- Impact analysis before changes
- Explicit user confirmation steps
- Technology-specific file generation
- Consistent version formatting

## Version

- Current Version: 1.0.0
- Last Updated: 2024-12-02
- Stability: Experimental
