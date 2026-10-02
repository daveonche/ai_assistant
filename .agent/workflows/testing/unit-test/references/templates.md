# Unit Test Skill - Output Templates and Detailed Prompts

## Step 3B - Dependency Management Invocation

After receiving testing stack confirmation:

Say EXACTLY:
"New testing dependencies are required. I will now:

1. Pause test generation
2. Invoke $code-dependency-management to handle dependency setup
3. Resume test generation after dependencies are configured

Please use $code-dependency-management now to proceed."

[STOP - Wait for user to complete dependency management process]

## Step 3C - Test Configuration Workflow

After dependencies are managed, present:

```txt
Test Configuration Setup:

1. Project Structure:
   [Show actual project structure]
   
   Test File Location Options:
   1. Follow detected convention: [path]
   2. Specify custom location

2. Configuration Files:
   [List required configs for chosen tools]

3. Test Runners:
   [List available options]

Shall I proceed with creating this configuration? (Y/N)
```

[STOP - Wait for user confirmation]

After receiving 'Y', say EXACTLY:
"Ready to create test configuration. To proceed:

1. Enter command: /code
2. Then simply say: 'create test configuration'
3. After creation, enter command: /ask
4. Confirm configuration is complete"

[STOP - Wait for user to create configuration]

Only after test environment is fully configured:
Ask: "Shall I proceed with analyzing test scenarios? (Y/N)"

## Step 4 - Scenario Analysis Prompt

```txt
Test Scenario Analysis for Step [number]:

Must Support: [requirement from step]
Required Tests:
1. [test scenario that directly verifies this requirement]
   Maps to: [exact requirement text being verified]
   Status: [New/Exists]
[Repeat for each Must Support item]

Manual Verification Mapping:
[For each manual verification step from story step]
- Verification: [manual step text]
  Automated Test: [corresponding automated test, if possible]
  Status: [Automatable/Manual Only]
```

Ask: "I've mapped tests directly to step requirements. Reply with:

- 'approved' to begin implementing tests
- specific changes needed"

## Step 5 - Individual Test Implementation Template

For each NEW test scenario:

1. First, present the test structure:

```txt
Implementing Test: [test name]
Verifies: [specific Must Support requirement being tested]
Framework: [test framework]

Test Structure:
[Show test code structure]

Shall I proceed with implementing this test? (Y/N)"
```

[STOP - Wait for user confirmation]

1. After receiving 'Y', say EXACTLY:
   "Ready to implement this test. To proceed:
   1. Enter command: /code
   2. Then simply say: 'implement test'
   3. After implementation completes, I'll provide the appropriate test command for your environment:
      [Will show framework-specific command OR request command input]
   4. After test execution, enter command: /ask
   5. Finally, confirm if test result is 'passing' or 'failing'"

2. For test execution:
   If framework detected:

   ```txt
   Framework-specific command for [detected framework]:
   [Show relevant command]
   ```

   If framework not detected or custom:

   ```txt
   Please specify test execution command for your environment:
   [Wait for user input]
   ```

3. After test execution command is provided/confirmed:
   Execute the appropriate test command and present results:

   ```txt
   Executing Test: [test name]
   Command: [exact command used]
   
   Test Results:
   [Show complete test output]
   
   Test Status: [PASSED/FAILED]
   [If failed, show specific failure details]
   ```

4. Ask: "Please confirm the test execution results. Is the test:
   1. Passing and ready to proceed
   2. Failed and needs fixes
   3. Needs to be run manually

   Please choose an option (1-3)"

   [STOP - Wait for user confirmation]

5. If option 2 (Failed):
   Return to start of STEP 5 for this test

   If option 3 (Manual run needed):
   Say: "Please run the test manually using:
   [Provide exact test command]

   After running, indicate if test is 'passing' or 'failing'"

6. Only after confirmed passing, present:

```txt
Test Status Check:
✓ Test implemented: [test name]
✓ File: [test file path]
✓ Execution: PASSED
✓ Results verified by: [AI execution/Manual execution]
✓ Verifies requirement: [exact Must Support item being verified]

Would you like to:
1. Proceed with next test
2. Review current test implementation
3. Mark testing complete for this step

Please choose an option (1-3)
```

## Step 6 - Summary Template

```txt
Test Implementation Summary for S<X.Y> Step [number]:

Must Support Coverage:
[For each Must Support item]
- [requirement]: [Tested/Untested]
  Tests: [list tests verifying this requirement]

Test Execution Status:
✓ [test name]: [status]
✓ [test name]: [status]
```

Ask: "Would you like to:

1. Add more tests for untested requirements
2. Mark test implementation complete
3. Review existing tests

Please choose an option (1-3)"

## Step 7 - Completion Template

Say EXACTLY:
"Test implementation for Step [number] is complete. To proceed:

1. All Must Support items have corresponding passing tests ✓
2. All tests map directly to step requirements ✓
3. Use $testing-unit-test S<X.Y> [next-step] when ready to test the next step

IMPORTANT: Each story step must have its own dedicated tests. Even if subsequent steps modify the same code, they require their own test coverage."

## Status Command Template

When `$testing-unit-test-status` is seen, respond with:

```txt
Test Generation Progress for Story S<X.Y>, Step [number]:

Status: [Complete/In Progress]
- Must Support Items: [total from step]
- Items Tested: [number]
- Items Remaining: [number]

✓ Completed Tests:
[List only tests that map directly to Must Support items]

⧖ Current: [current test that maps to specific requirement]

☐ Remaining:
[List only tests that map to untested Must Support items]

Use $testing-unit-test S<X.Y> [step-number] to continue

Note: You can switch to testing a different story step at any time by providing a new story and step number to the $testing-unit-test command, even if tests remain for the current step.
```
