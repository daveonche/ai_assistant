# Unit Test Skill - Consolidated Rules

## Scope and Mapping

1. Generate tests only for the current step’s Must Support items.
2. Map every test directly to a specific requirement.
3. Reject and flag out-of-scope test suggestions.
4. Check for existing test coverage before writing new tests.

## Environment and Dependencies

1. Never assume testing tools, configuration, or runner are available.
2. Always set up proper test environment before writing tests.
3. Use `$code-dependency-management` for new testing dependencies.
4. Pause and resume test generation around dependency and configuration tasks.

## Implementation and Verification

1. Implement only one test at a time.
2. Always wait for explicit user confirmation before proceeding.
3. Always execute each test after implementation.
4. Require explicit confirmation of test pass/fail before moving on.
5. Do not assume test success; wait for user confirmation.
6. Never modify existing tests without explicit approval.

## Workflow and Documentation

1. Follow existing project test patterns and language-specific practices.
2. Document all test assumptions.
3. Maintain clear separation between test scenarios.
4. Keep test implementations atomic and focused.

## Non-Testable Steps

1. Never force unit tests for non-testable steps.
2. Identify steps better served by manual verification.
3. When no testable items exist, exit test generation and provide manual verification steps.
