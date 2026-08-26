# Unit Test Skill - Consolidated Rules

## Scope and Mapping

1. Generate tests only for the current step’s Must Support items.
2. Map every test directly to a specific requirement.
3. Reject and flag out-of-scope test suggestions.
4. Check for existing test coverage before writing new tests.

## Environment and Dependencies

5. Never assume testing tools, configuration, or runner are available.
6. Always set up proper test environment before writing tests.
7. Use `$coding-dependency-management` for new testing dependencies.
8. Pause and resume test generation around dependency and configuration tasks.

## Implementation and Verification

9. Implement only one test at a time.
10. Always wait for explicit user confirmation before proceeding.
11. Always execute each test after implementation.
12. Require explicit confirmation of test pass/fail before moving on.
13. Do not assume test success; wait for user confirmation.
14. Never modify existing tests without explicit approval.

## Workflow and Documentation

15. Follow existing project test patterns and language-specific practices.
16. Document all test assumptions.
17. Maintain clear separation between test scenarios.
18. Keep test implementations atomic and focused.

## Non-Testable Steps

19. Never force unit tests for non-testable steps.
20. Identify steps better served by manual verification.
21. When no testable items exist, exit test generation and provide manual verification steps.
