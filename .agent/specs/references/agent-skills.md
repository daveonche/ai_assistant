# Agent Skills Best Practices

Summarized from [Agent Skills](https://agentskills.io/skill-creation/best-practices)

## Start from real expertise

- Ground skills in specific project knowledge, not generic training data.
- Extract reusable patterns from actual hands-on tasks, recording successful steps, corrections, input/output formats, and provided context.
- Synthesize from real artifacts: internal docs, runbooks, API specs, schemas, configs, code review comments, version control history, and real failure cases.

## Refine with real execution

- Run the skill against real tasks and feed results back into creation.
- Include all results, not only failures, to tune false positives and missed items.
- Read execution traces to identify vague instructions, irrelevant guidance, or too many options without a default.
- Use structured evaluation with test cases, assertions, and grading for systematic iteration.

## Spending context wisely

- Add what the agent lacks; omit what it already knows (e.g., don't explain what a PDF is).
- Keep each skill a coherent unit, not too narrow (many skills needed) or too broad (hard to activate precisely).
- Aim for moderate detail: concise, stepwise guidance with a working example beats exhaustive documentation.
- For large skills, use progressive disclosure: keep core SKILL.md under ~500 lines and ~5,000 tokens; move details to `references/` and tell agent when to load them.

## Calibrating control

- Match specificity to fragility. Give freedom where multiple approaches are valid; be prescriptive when operations are fragile or exact sequence matters.
- **Flexible** example: describe what to check in a review. **Prescriptive** example: exact migration command sequence.
- Provide a clear default and mention alternatives briefly, not a menu of equal options.
- Favor procedures over declarations: teach a reusable method rather than a single answer, while still allowing specific details like output templates or prohibited PII.

## Patterns for effective instructions

### Gotchas sections

- List environment-specific facts that defy reasonable assumptions.
- Keep in SKILL.md where the agent can read them before encountering the problem.
- Add corrections when the agent makes mistakes; this iteratively improves the skill.

### Templates for output format

- Provide concrete templates rather than prose descriptions for required output formats.
- Short templates inline; longer or conditional templates in `assets/` and reference from SKILL.md.

### Placeholder conventions

- Treat bracketed text in quoted templates (e.g., `[filename]`, `[file path]`) as placeholders to resolve from context, never as literal output.
- State the substitution rule explicitly in the skill (e.g., a "Placeholder Convention" section) so any model follows it.
- When a template requires a file list, reference the exact paths tracked earlier in the workflow instead of generic placeholders.

### Checklists for multi-step workflows

- Use explicit checkboxes to track progress, especially with dependencies or validation gates.

### Validation loops

- Instruct the agent to validate its own work before moving on.
- Pattern: do the work, run a validator, fix issues, repeat until validation passes.
- A reference document can serve as the validator.

### Plan-validate-execute

- For batch or destructive operations, create an intermediate structured plan.
- Validate plan against source of truth, then execute only after validation passes.
- Use a validation script that produces actionable error messages.

### Bundling reusable scripts

- If execution traces show the agent reinventing the same logic, write and bundle a tested script in `scripts/`.
- See the skill-creation using-scripts guide for details.
