# Agent-Flavored Markdown (AFM) Convention

Conventions for creating and reviewing `AGENTS.md` files: the agent-facing
documentation that tells coding agents how to work in this repository.
Derived from the AGENTS.md standard at https://agents.md/, with structure
and metadata guidance adapted from the Agent-Flavored Markdown
specification at
https://wso2.github.io/agent-flavored-markdown/specification/.

Use this file as the review criteria when creating or reviewing an
`AGENTS.md` file.

Note the distinction: `AGENTS.md` gives a coding agent context about this
repository; a WSO2 AFM `.afm.md` file defines a deployable AI agent (role,
model, tools, interfaces). This convention covers `AGENTS.md` only.

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

## Structure conventions

Adapted from the AFM specification; recommended, not required by the
AGENTS.md standard:

- Optionally start with a YAML front matter block (`---` delimited) for
  minimal metadata: `name`, `description`, `version`. The body is what
  agents read; keep front matter to a few fields.
- Open the body with a role-style section describing the agent's purpose
  and responsibilities in this repository (the AFM `# Role` pattern),
  followed by an instructions-style section with the directives that
  govern behavior (the AFM `# Instructions` pattern). The remaining
  recommended sections follow.
- Apply progressive disclosure: keep the root file concise and move detail
  into referenced files (e.g., `docs/`, conventions references) rather
  than growing it unbounded.

## Content rules

- Use standard Markdown. No required fields or headings.
- Keep the file concise and agent-focused.
- Prefer exact shell commands over prose descriptions.
- If tests are listed, agents should run them and fix failures before
  finishing.
- Add or update tests for code that changes.
- Markdown syntax itself follows the repository GFM rules in
  `references/github-flavored-markdown.md`.

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

## Review checklist

When reviewing an `AGENTS.md` file, verify:

- [ ] Located at the repository root (or nested per package in monorepos).
- [ ] Concise and agent-focused; no human-marketing prose.
- [ ] Commands are exact and runnable, not prose descriptions.
- [ ] Sections present where applicable (setup, build/test, style,
      testing, PR, security).
- [ ] Role/instructions-style opening context, per Structure conventions.
- [ ] Follows the GFM rules in
      `references/github-flavored-markdown.md`.
- [ ] Detail lives in referenced files, not duplicated inline.

## Gotchas

- The closest `AGENTS.md` wins: a nested file silently overrides the root
  file for paths in its subtree.
- An explicit user chat prompt overrides any `AGENTS.md` content; do not
  write instructions that assume they cannot be overridden.
- `AGENTS.md` is not the WSO2 AFM format: do not add `interfaces`,
  `tools`, or `model` front matter intended for `.afm.md` agent
  definitions.

## Validation

Before committing `AGENTS.md` changes: render-check against the GFM rules,
run every listed command once to confirm it works, and re-check the review
checklist above.
