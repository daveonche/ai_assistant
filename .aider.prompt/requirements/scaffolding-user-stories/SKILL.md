# Project Scaffolding Story Generator

When asked to generate initial scaffolding stories:

1. Review provided context:
   - Project requirements (e.g., `docs/requirements.md`)
   - Architecture decisions (e.g., `docs/architecture/architecture.md`)
   - Technology stack (e.g., `docs/tech_stack.md`)
   - Component structure

   *If any of these are missing from the context, ask the user to add them using the `/read-only` command before proceeding.*

2. Summarize your understanding of the above context. If no context or clearly insufficient context is provided, give the user the option to proceed without providing more details but warn them that the scaffolding might be limited or could later require significant changes.

3. Generate 2-3 user stories that will result in:
   - Basic project structure
   - Core dependencies installed
   - Minimal running application
   - No data persistence
   - No security implementation
   - No business logic (strictly structural setup)

4. Format each story:

## Story [number]: [title]

**As a** developer
**I want to** [scaffolding goal]
**So that** [business value]

### Acceptance Criteria
- [ ] [Specific, testable criteria]
- [ ] [Include version numbers]
- [ ] [Reference component names]

### Technical Notes
- Technology choices: [list relevant tech]
- Component structure: [describe structure]
- Configuration details: [specific settings]
- Command examples: [setup/run commands]

### Definition of Done
- [ ] Project runs successfully
- [ ] Basic structure matches architecture
- [ ] Core dependencies installed
- [ ] Smoke test passes

5. Validate stories:
   - Ensure completeness for basic setup
   - Verify alignment with architecture
   - Confirm minimal scope
   - Check all technical details included

6. Save the generated stories:
   - Ask the user to switch to `/code` mode.
   - Save the generated stories to `docs/sprints/sprint_0_stories.md` (or a user-specified path).
