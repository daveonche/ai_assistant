# Requirements Revision Guide

When asked to revise requirements:
1. Review Current Requirements
- If not provided, request project requirements

2. Present Current Requirements
- Display all requirements with reference numbers
- Ask which numbers need revision or if new ones should be added
[STOP - Wait for user input]

3. For Each Selected Requirement:
   Present options:
   1. Revise requirement
   2. Remove requirement
   3. Add new requirement (if selected)
[STOP - Wait for user selection]

4. For Revision/Removal Choice:
- Show current requirement text
- Check for dependencies/impact
- Collect new requirement details (if revising/adding)
- Validate clarity and testability
- Confirm revision
[STOP - Wait for user confirmation]

5. After All Revisions:
- Renumber requirements sequentially
- Group by category
- Update requirement relationships
- Generate clean requirements list

Format output as:

# Revised Core Requirements

## Functional Requirements

### [Category]
- REQ-1: [Requirement]
- REQ-2: [Requirement]

## Non-Functional Requirements
- REQ-3: [Requirement]
- REQ-4: [Requirement]
