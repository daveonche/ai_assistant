# Requirements Revision Guide

**Convention Check Reminder:** Before creating or editing any file, check the Conventions Reference Routing table in `.agent/AGENTS.md` and load the matching reference via `/read-only` before proceeding.

When asked to revise requirements:

1. Review Current Requirements
   - Ask the user: "Are the project requirements currently loaded in your context? If yes, name the file. (Y/N)" — do not assess context contents yourself (Critical Rule 3). If the user answers N, ask them to provide the requirements file and wait.

2. Present Current Requirements
   - Display all requirements with reference numbers
   - Ask which numbers need revision or if new ones should be added

   [STOP - Wait for user input]

3. For Each Selected Requirement:
   Present options:

   1. Revise requirement
   2. Remove requirement

   Adding a new requirement is a separate case: it is chosen from the step 2 prompt and is not tied to a selected requirement, so collect its details directly instead of presenting these options.

   [STOP - Wait for user selection]

4. For Revision/Removal Choice:
   - Show current requirement text
   - Check for dependencies/impact
   - Collect new requirement details (if revising/adding)
   - Validate clarity and testability
   - If validation fails, propose a reworded requirement and re-confirm with the user before applying it
   - Confirm revision

   [STOP - Wait for user confirmation]

5. After All Revisions:
   - Renumber requirements sequentially
   - Group by category
   - Update requirement relationships
   - Generate clean requirements list

Format output as:

```markdown
# Revised Core Requirements

## Functional Requirements

### [Category]
- REQ-1: [Requirement]
- REQ-2: [Requirement]

## Non-Functional Requirements
- REQ-3: [Requirement]
- REQ-4: [Requirement]
```

<!-- sentinel: requirements/revised-project -->
