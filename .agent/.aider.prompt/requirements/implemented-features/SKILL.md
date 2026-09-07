# Implementation Status Analysis Prompt

## Commands

- `$requirements-implemented-features` — Start or resume implementation analysis.
- `$requirements-implemented-features-status` — Show current progress in the active conversation.

**Convention Check Reminder:** Before creating or editing any file, check the Conventions Reference Routing table in `.agent/AGENTS.md` and load the matching reference via `/read-only` before proceeding.

---

## Gotchas

- Do not invent or reuse technology stack values that are not present in the loaded `docs/tech_stack.md`.
- The `REQ-3` requirement-ID format in the report templates is illustrative only. Use the actual requirement IDs exactly as they appear in the loaded requirements files; if the requirements files do not define IDs, do not invent a format.
- Analysis runs in `/ask` mode, but saving the report requires a controlled transition to code mode (see Step 4).

---

## Workflow

### Step 0: Mode Verification

Ensure the user is in `/ask` mode. If they are not, or if you are unsure, say exactly:

"To proceed with implementation analysis:

1. Enter `/ask` mode.
2. Reply with `ready` when you are in ask mode."

[STOP — Do not proceed until the user replies with `ready`.]

---

### Step 1: Context Verification

Check that the actual contents of these files are loaded in the current conversation context:

1. Project requirements — `docs/requirements/core_requirements.md` when present; otherwise `docs/requirements.md`. At least one of the two must be loaded.
2. User stories — `docs/user_stories.md`
3. Core technology stack — `docs/tech_stack.md`

If any file contents are missing, list the exact missing files and ask the user to add them using the command: `/read-only <file>`. (`/add` also works if `/read-only` is unavailable.)

[STOP — If any required file contents are missing, do not begin analysis until they are loaded.]

Example response:

```text
Found in context:
✓ Requirements: docs/requirements/core_requirements.md
✓ User stories: docs/user_stories.md
✓ Tech stack: [values from docs/tech_stack.md]
```

---

### Step 2: Implementation Analysis

Once all required file contents are available, analyze the codebase and report in the following format.

If the current context is insufficient to determine implementation status, ask the user to add relevant source code directories such as `src/`, `tests/`, or specific feature directories.

---

## Implementation Status

### A. Completed Features

- **Feature name** — Supporting evidence from the codebase, citing specific files and implementations. Reference requirement IDs where possible, e.g. `REQ-3`.

### B. Partially Implemented Features

- **Feature name** — Current progress with specific file references and remaining work.

### C. Not Yet Implemented Features

Features listed in dependency and priority order, mapped to specific requirements:

- `[Requirement ID]` — Feature name — Requirement source file.

---

## Priority Order for Next Implementation Phase

### Priority 1 — Category Name

- `[Requirement ID]` — Specific feature/requirement from `docs/requirements.md` or `docs/requirements/core_requirements.md`
- `[Requirement ID]` — Specific feature/requirement from the requirements files
- Rationale: Why this category is first, based on dependencies and requirements

### Priority 2 — Category Name

- `[Requirement ID]` — Specific feature/requirement from the requirements files
- `[Requirement ID]` — Specific feature/requirement from the requirements files
- Rationale: Why this category follows the previous priority

Continue until all remaining features have been prioritized.

---

### Step 3: Validation

Before presenting the final report or saving it, validate the analysis:

1. Cross-check every cited requirement ID against the loaded requirements files and user stories.
2. Cross-check every technology stack value against the loaded `docs/tech_stack.md`.
3. Cross-check every cited file path against the files actually present in the codebase context.
4. Fix any mismatches and repeat the validation until all checks pass.

---

### Step 4: Save Report

After validation passes:

1. Offer to save the implementation status report.

Recommended default filename:

```text
docs/implementation_status.md
```

2. If the file already exists, ask the user whether to overwrite it or save as a timestamped file.

3. If the user agrees to save, request the mode transition before writing the file. Say exactly:

   "To save the report:

   1. Enter command: /code proceed
   2. Reply with 'done' once you have run the command."

   [STOP — Do not write the file until the user confirms the code-mode transition.]

4. After the user confirms, save the report and end the workflow immediately.

5. If the user declines to save, end the workflow immediately without writing any file.

[STOP — After the save decision, terminate the workflow. Do not offer further analysis, suggestions, or actions.]

---

## Status Command Response

When `$requirements-implemented-features-status` is seen, respond with:

```text
Implementation Analysis Progress:
✓ Completed: [list completed steps from the current conversation]
⧖ Current: [current step and what is needed to proceed]
☐ Remaining: [list uncompleted steps]
```

If no implementation analysis is currently active in the conversation, reply:

"No implementation analysis is currently active. Use `$requirements-implemented-features` to start one."

---

## Critical Rules

1. If user input at a `[STOP]` point is invalid or unexpected, re-prompt with the original question.

---

## Important Limitation

This analysis role is strictly limited to examining and reporting on implementation status only.

Do not:

- Modify code
- Make implementation suggestions
- Propose code changes
- Create new components
- Refactor existing code
- Generate code snippets
- Provide coding guidance
