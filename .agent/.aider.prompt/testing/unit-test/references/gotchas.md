# Unit Test Skill - Gotchas

- Never assume a testing environment is configured.
- Never assume test framework or patterns; verify project conventions first.
- Each story step must have its own dedicated tests, even if later steps modify the same code.
- Some steps are not unit-testable; manual verification may be more appropriate.
- Do not introduce new dependencies or edit files outside the target step's scope.
- Always require explicit user confirmation after test execution before proceeding.
- Test environment setup and dependency changes require pausing test generation and returning to it after configuration is complete.
- Existing tests should always be checked for coverage before writing new tests.
- Scope tests strictly to the current step's Must Support items; reject out-of-scope test suggestions.
