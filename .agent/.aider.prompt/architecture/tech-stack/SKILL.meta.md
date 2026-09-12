# Metadata: # Technology Stack Generation Prompt

## AI Assistant Compatibility

- Tested With:
  - Aider
  - GLM 5.3 Flash (August 27, 2026 release)
- Untested / Not verified:
  - Other Claude models
  - GitHub Copilot
  - GPT-4

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
- Reference file: `references/dependency-file-templates.md` — load this file when generating dependency files.

## Purpose

This prompt guides the user through defining a compatible, version-locked technology stack based on project requirements and user preferences. It also supports modifying an existing stack.

## Usage

Use this prompt when starting a new project to select the core technology, frameworks, and dependencies, or when you need to modify an existing technology stack.

### Commands

- `#generate-stack`: Starts new technology stack generation.
- `#modify-stack`: Allows modification of an existing tech stack.
- `#stack-status`: Shows current progress in stack generation workflow.

### Workflow for `#generate-stack`

1. **Mode Verification**: Ensure you are in `/ask` mode.
2. **Requirements Verification**: Check for project requirements and existing dependency files.
3. **Application Type Assessment**: Determine the type of application being built.
4. **Core Technology Selection**: Select the core technology and version.
5. **Dependency Analysis**: Identify required capabilities and recommend or select dependencies.
6. **Compatibility Verification**: Verify compatibility between core technology and dependencies.
7. **Generate Documentation and Dependency Files**: Create the tech stack documentation and appropriate dependency files.
8. **Save Files**: Switch to `/code` mode to save the generated files.

### Workflow for `#modify-stack`

1. **Mode Verification**: Ensure correct context and mode.
2. **Context Verification**: Confirm that the existing tech-stack documentation and dependency files are present.
3. **File Content Verification**: Read and display current stack and dependency contents.
4. **Modification Selection**: Choose core version update, add dependency, update dependency version, remove dependency, or other.
5. **Impact Analysis**: Present exact proposed changes, files to modify, compatibility verification, and cascading changes.
6. **Save Modified Files**: Exercise the same `/code` mode saving workflow.

### Workflow for `#stack-status`

- Report completed steps, current step, and remaining steps for tech stack generation.
- If persistence across sessions is needed, use a small state file such as `tech_stack_progress.md`.

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

## Key Risks and Mitigations

- Core risks and mitigations are documented in `SKILL.md`; the main constraints are:
  - Version compatibility conflicts → strict version locking and comprehensive compatibility checks.
  - Dependency chain resolution and cross-platform compatibility → technology-specific validation and structured modification process.
  - Maintaining version consistency → consistent dependency-file generation and explicit user confirmation steps.
  - User preference vs technical fit → clear documentation of AI recommendations and user choices.

## Validation & Execution Notes

- Validation loop: Run the generated dependency-file templates through the checklist in `SKILL.md` before saving.
- Execution evidence: Update this section after each real run with tested scenarios and any issues found.
- Current status: Not yet recorded.

## Version

- Current Version: 1.1.0
- Last Updated: 2026-08-26
- Stability: Experimental
