# Metadata: Story Analysis Prompt

## AI Assistant Compatibility

- Tested With:
  - Aider
  - LLM: GLM 5.3 Flash (August 27, 2026 release)
  - Skill version tested: 1.1.0
- Potential Compatible Assistants:
  - Other GLM models
  - GitHub Copilot (with modifications)

## SDLC Phase

- Phase: Planning
- Sub-Phase: Story Decomposition
- Workflow: Post-Scaffolding Sprint Workflow

## Complexity Rating

- Complexity: Medium
- Cognitive Load: Moderate
- Technical Depth: Requires comprehensive story understanding

## Usage Guidelines

- Prerequisite: Sprint stories generated
- Requires:
  - User story details
  - Project requirements
  - Project context (may include a technology stack; it must NOT influence step wording)
- Progressive Disclosure:
  - Core workflow lives in `SKILL.md`
  - The implementation-steps template lives in `references/story-template.md` and is loaded on demand in Step 4

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes
- Requires Contextual Awareness: High

## Best Practices

- Follow the rules defined in `SKILL.md` (see its "Each step MUST", "Developer Notes MUST", and "CRITICAL Rules" sections); this file intentionally does not duplicate them

## Potential Challenges

- Overly complex or vague story decomposition
- Misinterpreting user requirements
- Creating non-implementable steps
- Losing sight of original story objectives

## Recommended Mitigation Strategies

- Use consistent step decomposition template
- Validate steps against original story
- Ensure steps are incremental and testable
- Cross-reference with project requirements
- Maintain clear acceptance criteria
- Run the Step 4a validation checklist in `SKILL.md` before presenting steps; it directly addresses vague decomposition and non-implementable steps

## Version

- Current Version: 1.1.0
- Last Updated: 2026-08-27
- Stability: Experimental

## Version History

- 1.1.0 (2026-08-27): Added Gotchas section and Step 4a validation loop to `SKILL.md`; extracted the implementation-steps template to `references/story-template.md`; clarified technology neutrality and `#analysis-status` stage definitions.
- 1.0.0 (2024-11-09): Initial release.
