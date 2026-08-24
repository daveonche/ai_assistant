# Code Review Workflow

[STEP 0] Ask the user:
"Do you have a coding convention you want me to apply to this review? If yes, provide it or point me to a convention file."

[STOP] Wait for the user’s response.

- If they provide a convention, follow it as review criteria.
- If they point to a file, read that file and use it as review criteria.
- If they answer no, proceed with general best practices.

[STEP 1] Read the target file: `{file}`.

[STEP 2] Review the file against the agreed conventions and best practices.
Provide concise issues, risks, and suggested improvements.

[STOP] Present the improvements as numbered options and ask the user to select which ones to implement.

Example:
"Which improvements would you like me to implement?

1. <Improvement 1>
2. <Improvement 2>
3. <Improvement 3>

Reply with the number(s) to implement, or 'all'."

[STEP 3] Ask the user to run: `/code proceed`

[STOP] Wait for confirmation that the user has run the command.

[STEP 4] Implement the confirmed improvements in `{file}`.
