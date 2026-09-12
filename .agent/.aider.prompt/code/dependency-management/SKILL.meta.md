# Metadata: Dependency Management Prompt

## AI Assistant Compatibility

- Tested With:
  - Aider
  - LLM: GLM 5.3 Flash (August 27, 2026 release)
- Potential Compatible Assistants:
  - Other Claude models
  - GitHub Copilot (with modifications)

  Note: The current `SKILL.md` includes updated verification commands and eco-system-specific dependency handling. Compatibility should be re-verified on the assistants used in practice.

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
- Document all dependency decisions with concrete evidence sources (e.g., `npm view`, `pip index versions`)
- Maintain clean separation between analysis and implementation phases
- Update both documentation and dependency files
- Use `$code-dependency-management S<X.Y>` and `$code-dependency-status` command aliases consistently
- Run post-change verification using the project’s dependency manager (lockfile, dependency resolution, etc.)
- Handle the “no new dependencies required” path as an explicit no-op, not an empty update

## Potential Challenges

- Missing or incomplete dependency information
- Version compatibility conflicts
- Circular dependencies
- Peer dependency resolution
- Breaking changes in dependency updates
- Mode switching complexity
- Maintaining consistency across dependency files
- Unsupported or project-specific dependency file formats
- Failed post-update dependency-manager verification
- Command syntax drift between `#` aliases and `$` shorthand
- Metadata drift from workflow updates

## Recommended Mitigation Strategies

- Strict version control (no ranges)
- Comprehensive compatibility testing
- Clear documentation of decisions with evidence output recorded
- Explicit mode switching instructions
- Mandatory post-change verification commands (`npm install --package-lock-only`, `pip install -r`, `bundle lock --update`, `mvn dependency:resolve`, `gradle dependencies`)
- Define both `#` and `$code` aliases consistently in prompts
- Add an explicit no-op branch for “no new dependencies required”
- Keep metadata version and notes synchronized with the prompt workflow

## Version

- Current Version: 1.2.0
- Last Updated: 2026-08-26
- Stability: Experimental
- Changes: Synced with `SKILL.md` v1.2 enhancements (workflow progress checklist, `Gotchas` section, clarified step 6 save instruction, updated resume command to `$code-implementation`)

## Integration Points

- Implementation Prompt
- Story Analysis Prompt
- Project Setup Workflow
- Build/Deploy Pipeline Configuration
- AGENTS.md shorthand command mapping (`$code-dependency-management`, `$code-dependency-status`)
- Code Review Workflow (`.agent/.aider.prompt/code/review/SKILL.md`)

## Success Metrics

- Dependency analysis successfully uses documented ecosystem commands and cites evidence
- No unresolved peer dependency conflicts with existing locked versions
- Dependency files and lockfiles are updated/committed where required
- Post-change dependency manager verification command succeeds
- No-op path is selected for “no new dependencies required” when applicable
- Successful return to implementation with `$code-implementation S<X.Y>` command

## Failure Modes

- Circular dependency requests
- Incompatible version selections
- Incomplete dependency updates
- Lost context during mode switching
- Implementation blocking due to missing dependencies
- Post-update verification fails or is skipped
- Unsupported dependency file format not handled
- Metadata drift after SKILL.md enhancements
- Empty dependency-file changes when no new dependencies are required
