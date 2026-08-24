# AI Code Tutor Prompt

## Description

Interactive tutorial system that guides developers through understanding a codebase while teaching core concepts and technologies used.

## Prerequisites

- Use `/ask` mode.
- Have the target code files or directories available to add to the chat via `/read-only`.
- Focus on key entry points rather than adding the entire repository.

## Usage

1. Ensure you are in `/ask` mode. If unsure, switch with `/ask`.
2. Activate the workflow with: `$learning-project-tutor`
3. When prompted, add files or directories using `/read-only <filepath>` and reply `continue`.
   - If a directory cannot be added, add its individual files instead.
   - After replying `continue`, the workflow verifies that the requested files are actually loaded.
4. Follow the interactive prompts:
   - Overview stage: reply `continue` to proceed or ask questions first.
   - Component deep dive stage: reply `next` to move to the next component, or ask a question about the current component.

## Best suited for

- Learning new codebases
- Onboarding team members
- Understanding inherited projects
- Technology stack education
- Architecture comprehension

## Workflow / Output format

1. Mode verification
2. Context verification
3. High-level overview
   - Core technologies and roles
   - 3-5 critical files/functions
   - Key architectural patterns
4. Component deep dives
   - Purpose and functionality
   - Brief code examples
   - Integration with other components
5. Improvement analysis and learning path recommendations
6. Final check for revisit or tutorial end

## Important notes

- The high-level overview is based only on files added to the chat, not the entire repository.
- The workflow waits for explicit user input at each stop point.
