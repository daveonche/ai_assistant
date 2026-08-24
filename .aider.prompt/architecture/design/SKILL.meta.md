# Metadata: # Architecture Design Generator Prompt

## AI Assistant Compatibility

- Tested With:
  - Aider
  - LLM: Claude 3.5 Sonnet (October 22, 2024 release)
- Potential Compatible Assistants:
  - Other Claude models
  - GitHub Copilot (with modifications)
  - GPT-4 (with architectural diagram adaptations)

## SDLC Phase

- Phase: Design
- Sub-Phase: Initial Architecture
- Workflow: Project Scaffolding

## Complexity Rating

- Complexity: High
- Cognitive Load: High
- Technical Depth: Requires comprehensive understanding of architectural patterns and principles

## Usage Guidelines

- Prerequisite: Project requirements documentation
- Requires:
  - Technology stack documentation
  - Core dependency definitions
  - Project scope understanding
  - Basic technical constraints

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes
- Requires Contextual Awareness: High
- Command Driven: Yes (#generate-architecture, #architecture-status)
- Diagram Support: Mermaid.js integration

## Best Practices

- Focus on core structural decisions
- Minimize initial component count
- Document decision rationale
- Maintain clear component boundaries
- Use visual representations
- Keep documentation concise
- Limit scope to scaffolding needs

## Potential Challenges

- Scope creep beyond core architecture
- Over-engineering initial design
- Balancing flexibility vs. structure
- Managing technical constraints
- Maintaining documentation clarity
- Avoiding premature optimization

## Recommended Mitigation Strategies

- Strict scaffolding scope limits
- Core component focus
- Clear architectural boundaries
- Explicit decision documentation
- Visual diagram support
- Regular scope verification
- Minimal project structure depth

## Version

- Current Version: 1.0.0
- Last Updated: 2024-12-02
- Stability: Experimental

## Purpose
This prompt guides the user through defining the core architectural components for a project. It focuses on fundamental structures, cross-cutting concerns, and integration patterns that are difficult to change later in the development lifecycle.

## Usage
Use this prompt when starting a new project or when a major architectural pivot is required.

### Commands
- `#generate-architecture`: Starts or resumes the architecture design workflow.
- `#architecture-status`: Shows the current progress in the architecture workflow.

### Workflow
1. **Mode Verification**: Ensure you are in `/ask` mode.
2. **Context Verification**: The prompt will check for core requirements and technology stack documents.
3. **Scope Confirmation**: Defines the boundaries of the scaffolding design (what is and isn't included).
4. **Core Architecture Generation**: Defines layers, cross-cutting concerns, and integration patterns.
5. **Documentation Planning**: Outlines the architecture document and Mermaid diagram.
6. **Implementation**: Switches to `/code` mode to generate the documentation files and diagrams.
