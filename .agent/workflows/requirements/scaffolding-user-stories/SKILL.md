# Project Scaffolding Story Generator

**Convention Check Reminder:** Before creating or editing any file, check the Conventions Reference Routing table in `.agent/AGENTS.md` and load the matching reference via `/read-only` before proceeding.

When asked to generate initial scaffolding stories:

1. Review provided context:
   - Project requirements (e.g., `docs/requirements/core_requirements.md`)
   - Architecture decisions (e.g., `docs/architecture/architecture.md`)
   - Technology stack (e.g., `docs/tech_stack.md`)
   - Component structure (e.g., the component section of `docs/architecture/architecture.md`)

   Ask the user: "Are these files currently loaded in your context? If yes, name them. (Y/N)" — do not assess context contents yourself (Critical Rule 3). For any file the user did not name, output the exact command inline (e.g., `/read-only docs/requirements/core_requirements.md`), ask the user to add the missing file, and wait for confirmation. If the user declines, continue with what is available and apply the warning rule in step 2.

2. Summarize your understanding of the above context. If context is missing (declined in step 1) or clearly insufficient, warn the user that the scaffolding might be limited or could later require significant changes, and let them choose to proceed anyway or provide more details before continuing.

3. Generate 2-3 user stories that will result in:
   - Basic project structure
   - Core dependencies installed
   - Minimal running application
   - No data persistence
   - No security implementation
   - No business logic (strictly structural setup)

4. Format each story using this template:

   ```markdown
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
   ```

5. Validate stories (validation loop):
   - Re-check each story against the scope list in step 3 and the template in step 4.
   - Fix any failures (missing template sections, scope violations, unpinned versions).
   - Re-validate after each fix; repeat until every story passes.
   - Report the validation results to the user before saving.

6. Save the generated stories:
   - Instruct the user to run `/code proceed` and wait for explicit confirmation that code mode is active.
   - Save the generated stories to `docs/sprints/sprint_0_stories.md` (or a user-specified path).

## Gotchas

- Never include data persistence, security, or business logic in scaffolding stories, even if the technology stack lists a database or an auth provider; those belong to later stories.
- Pin exact dependency versions in acceptance criteria and technical notes (e.g., `flask==3.0.3`), not version ranges.
- Keep stories strictly structural: a story that requires data migration or production secrets is out of scope.

## Worked example

For format and level of detail, follow the real stories in `docs/sprints/sprint_1_stories.md`. Ask the user: "Is `docs/sprints/sprint_1_stories.md` currently loaded in your context? (Y/N)" — do not assess context contents yourself (Critical Rule 3). If the user answers N, ask them to add it with `/read-only docs/sprints/sprint_1_stories.md`.

<!-- sentinel: requirements/scaffolding-user-stories -->
