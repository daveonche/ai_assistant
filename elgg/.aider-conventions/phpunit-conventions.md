# SKILL: phpunit-conventions (Elgg Testing Guardrails)

## 1. STRUCTURE & LIFECYCLE

- Prefix all test case methods strictly with `test` (e.g., `testMethodReturnsExpectedPayload`).
- Use the native `setUp()` method to initialize mock environments and `tearDown()` to cleanly destroy instantiated Elgg entities.
- Keep one distinct assertion layout per test method block to maintain clear test boundaries.

## 2. ELGG ENTITY FACTORIES & INTEGRATION

- DO NOT save raw database entities using direct SQL. Mock entity data schemas or leverage Elgg's built-in creation wrappers.
- When evaluating plugin hooks or system actions, dispatch your triggers through `elgg_trigger_event()` or `elgg_trigger_plugin_hook()` to test authentic propagation behaviors.

## 3. MOCKING & STUBBING BOUNDARIES

- NEVER stub native global Elgg core components unless testing highly isolated third-party integrations.
- Use PHPUnit's internal `$this->createMock(ClassName::class)` syntax engine cleanly. 
- Avoid testing private or protected plugin helper methods directly; target assertions strictly against your public plugin API controllers and action endpoints.
