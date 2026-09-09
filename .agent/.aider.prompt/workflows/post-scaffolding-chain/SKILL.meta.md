# Metadata: Post-Scaffolding Sprint Workflow Chain Prompt

## AI Assistant Compatibility

- Tested With: Aider

## SDLC Phase

- Phase: Planning & Implementation
- Sub-Phase: Post-Scaffolding / Feature Development
- Workflow: Chained AI-assisted feature planning and implementation

## Complexity Rating

- Complexity: High
- Cognitive Load: High
- Technical Depth: Requires coordination across implementation analysis, story generation, story analysis, coding, and testing prompts

## Usage Guidelines

- Prerequisite: Completed initial project scaffolding (Sprint 1)
- Requires:
  - Existing project structure, dependencies, and core technologies
  - Previous sprint user stories and project requirements
- Command Driven: Yes

## Prompt Characteristics

- Input Driven: Yes
- State Dependent: Yes
- Requires Contextual Awareness: High
- Command Driven: Yes
- Chained Workflow: Yes

## Best Practices

- Keep phase outputs in accessible locations
- Verify all outputs before proceeding to the next phase
- Version control all artifacts
- Document modifications, assumptions, and decisions
- Never skip phases or assume outputs

## Potential Challenges

- Missing or incomplete previous sprint artifacts
- Skipping verification points
- Dependency drift between phases
- Context overload when loading multiple prompts
- Scope creep beyond the sprint

## Recommended Mitigation Strategies

- Input completeness checks
- Explicit phase verification points
- Dependency documentation and tracking
- Use phase commands to load prompts on demand
- Strict sprint scope limits

## Version

- Current Version: 1.1.0
- Last Updated: 2026-08-26
- Stability: Experimental

## Purpose

This workflow chain guides a project from implementation status analysis through sprint story generation, story analysis, implementation, and unit testing after initial scaffolding. It ensures each phase’s outputs become required inputs for the next phase.

## Usage

Use this workflow chain after initial project scaffolding has been completed, when planning and implementing the next sprint or new features.

### Commands

- `$workflows-post-scaffolding-chain` - Starts or resumes the post-scaffolding workflow chain
- `$planning-implementation-analysis` - Activates Phase 1: Implementation Status Analysis
- `$planning-sprint-story` - Activates Phase 2: Sprint Story Generation
- `$planning-story-analysis S<X.Y>` - Activates Phase 3: Story Analysis
- `$code-implementation S<X.Y> [step-number]` - Activates Phase 4A: Implementation
- `$testing-unit-test S<X.Y> [step-number]` - Activates Phase 4B: Unit Testing
- `$code-dependency-management` - Activates conditional dependency management during implementation

### Workflow

```txt
Phase 1: Implementation Status Analysis
↓ [Outputs feed Phase 2]
Phase 2: Sprint Story Generation
↓ [Outputs feed Phase 3]
Phase 3: Story Analysis
↓ [Outputs feed Phase 4A]
Phase 4A: Implementation
↓ [Outputs feed Phase 4B]
Phase 4B: Unit Testing
```

## Overview

This workflow is designed for projects that have already completed their initial scaffolding. It assumes basic project structure, initial dependencies, and core technologies are already in place.

The workflow operates through the sequential phases shown in the `Workflow` section above.

## Input/Output Chain

### Phase 1: Implementation Status Analysis (`$planning-implementation-analysis`)

[Implementation Analysis Prompt](../../planning/implementation-analysis/SKILL.md)

#### Phase 1 Purpose

Assess current project state, identify implemented and pending features.

**Initial Inputs Required:**

- Existing project code and status files

**Key Outputs → [Feed into Phase 2]:**

- Implementation Status Report (`implementation_status.md`)

### Phase 2: Sprint Story Generation (`$planning-sprint-story`)

[Sprint Story Generation Prompt](../../planning/sprint-story/SKILL.md)

#### Phase 2 Purpose

Create focused user stories for the next sprint based on technical dependencies.

**Required Inputs (including Phase 1 outputs):**

- Implementation Status Report
- Previous sprint's user stories

**Key Outputs → [Feed into Phase 3]:**

- Sprint Stories (`sprint_X_stories.md`)

### Phase 3: Story Analysis (`$planning-story-analysis S<X.Y>`)

[Story Analysis Prompt](../../planning/story-analysis/SKILL.md)

#### Phase 3 Purpose

Break down user stories into atomic, implementable functional steps.

**Required Inputs:**

- Sprint story for `S<X.Y>`

**Key Outputs → [Feed into Phase 4A]:**

- Story Steps Report (`S<X.Y>-story-steps.md`)

### Phase 4A: Implementation (`$code-implementation S<X.Y> [step-number]`)

[Implementation Prompt](../../code/implementation/SKILL.md)

#### Phase 4A Purpose

Systematically implement one specific step from the story analysis, ensuring all requirements are met using only approved dependencies.

**Required Inputs (including Phase 3 outputs):**

- Story Steps Report (`S<X.Y>-story-steps.md`)
- Sprint story
- Project's dependency definition file (e.g., `package.json`)

**Key Outputs → [Feed into Phase 4B]:**

- Code changes implementing the specified step

**Iteration Note:**

Phases 4A and 4B iterate until all steps for a user story have been implemented and unit tested.

### Phase 4B: Unit Testing (`$testing-unit-test S<X.Y> [step-number]`)

[Unit Test Generation Prompt](../../testing/unit-test/SKILL.md)

#### Phase 4B Purpose

Generate and verify unit tests for the implemented story step, ensuring comprehensive test coverage.

**Required Inputs (including Phase 4A outputs):**

- Code changes implementing the specified step
- Story Steps Report (`S<X.Y>-story-steps.md`)
- Sprint story
- Project's dependency definition file (e.g., `package.json`)

**Key Outputs:**

- Unit tests for the implemented step
- Test results indicating pass/fail status

**Conditional Prompt:**

During the implementation phase, if the Implementation Prompt determines that new dependencies may be required to implement a user story step, it will prompt the user to execute the Dependency Management Prompt. This ensures that all necessary dependencies are evaluated and approved before proceeding with the implementation.

[Reference: Dependency Management Prompt](../../code/dependency-management/SKILL.md)

## Workflow Chain Execution

### Starting the Chain

1. **Initiate Implementation Status Analysis:**

   ```cmd
   $planning-implementation-analysis
   ```

   - Ensure all Phase 1 inputs are available
   - Wait for complete analysis before proceeding

2. **Generate Sprint Stories:**

   ```cmd
   $planning-sprint-story
   ```

   - Must have all Phase 1 outputs available
   - Proceeds only when analysis outputs are complete

3. **Analyze Story:**

   ```cmd
   $planning-story-analysis S<X.Y>
   ```

   - Ensure the specific user story is available in the context
   - Wait for story analysis to complete before proceeding

4. **Implement Stories, step by step:**

   ```cmd
   $code-implementation S<X.Y> [step-number]
   ```

   - Requires complete story analysis outputs
   - Execute for each story and step, in sequence

5. **Generate Unit Tests:**

   ```cmd
   $testing-unit-test S<X.Y> [step-number]
   ```

   - Requires implemented code changes for the step
   - Run after each implementation step, or as needed

## Chain Dependencies

See `Input/Output Chain` for the single source of phase dependencies and outputs.

## Maintaining Chain Integrity

### Verification Points

1. **Analysis → Story Generation**
   - Verify implementation status report is complete
   - Confirm previous sprint stories are available

2. **Story Generation → Story Analysis**
   - Verify all sprint stories have required components

3. **Story Analysis → Implementation**
   - Verify story steps report is complete
   - Confirm dependency definition file is available

4. **Implementation → Unit Testing**
   - Verify implemented code changes are complete
   - Confirm story steps report and sprint story are available

### Chain Break Prevention

To maintain workflow integrity:

1. Keep all documentation updated as you progress
2. Use phase commands to confirm current state
3. Don't proceed if required inputs are missing

## Best Practices for Chain Execution

1. **Document Management**
   - Keep all phase outputs in accessible locations
   - Document any modifications to outputs
   - Version control all artifacts

2. **Phase Transitions**
   - Explicitly verify all required outputs exist
   - Validate output quality before proceeding
   - Document any assumptions or decisions

3. **Dependency Handling**
   - Track both technical and workflow dependencies
   - Verify dependency satisfaction at each step
   - Document any dependency changes

## Using the Workflow Chain

1. **Preparation**
   - Gather all initial inputs
   - Verify input completeness
   - Set up documentation structure

2. **Execution**
   - Follow the chain sequence strictly
   - Verify outputs at each step
   - Maintain documentation of progress

3. **Verification**
   - Use phase commands frequently
   - Verify chain integrity at each phase
   - Document completion of each phase

## AI Integration Notes

This workflow chain has been tested with different LLMs:

- AI Assistant: aider
- Implementation Prompt: Claude 3.5 Sonnet (October 22, 2024 release)
- Other Workflow Prompts: Claude 3.5 Haiku (October 22, 2024 release)

The chain assumes:

- AI can handle file operations
- Developer verifies all outputs
- Each phase completes fully before the chain proceeds

## Chain Verification

Before starting each phase, verify:

1. All required inputs are available
2. Previous phase outputs are complete
3. All dependencies are satisfied
4. Documentation is current

Remember: The strength of this workflow lies in its chained nature. Each phase builds upon the outputs of the previous phase, creating a comprehensive and connected development process.
