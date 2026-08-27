# AGENTS.md Convention

This is an Aider convention file derived from the AGENTS.md standard at
https://agents.md/.

## What AGENTS.md is

`AGENTS.md` is a README for coding agents: a predictable, project-specific file
containing the context and instructions an agent needs to work effectively in
the repository. It complements the human-focused `README.md` rather than
replacing it.

## Placement and precedence

- Put the main project file at the repository root: `AGENTS.md`.
- In monorepos, put nested `AGENTS.md` files in each package or subproject.
- The closest `AGENTS.md` to the file being edited takes precedence.
- An explicit user chat prompt always overrides any `AGENTS.md` content.

## Recommended sections

Create or update `AGENTS.md` with the sections that apply:

- Project overview
- Setup commands
- Build and test commands
- Code style guidelines
- Testing instructions
- Commit and PR instructions
- Security considerations
- Deployment steps
- Large datasets or reproducibility notes

## Content rules

- Use standard Markdown. No required fields or headings.
- Keep the file concise and agent-focused.
- Prefer exact shell commands over prose descriptions.
- If tests are listed, agents should run them and fix failures before finishing.
- Add or update tests for code that changes.

## Reference skeleton

```markdown
# AGENTS.md

## Setup commands
- Install deps: <command>
- Start dev server: <command>
- Run tests: <command>

## Code style
- <style rule>
- <style rule>

## Testing instructions
- <test workflow>

## PR instructions
- Title format: <format>
```

## Aider configuration

Load this convention by adding this to `.aider.conf.yml`:

```yaml
read: .agent/.aider.conventions/AGENTS.md
```

If there is also a repository-root `AGENTS.md`, add:

```yaml
read: AGENTS.md
```
