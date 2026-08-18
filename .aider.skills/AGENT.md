# Elgg Multi-Agent System Core Settings

## 1. DUAL-MODE ARCHITECTURE

- Architect Mode (Nous Hermes 3 405B): System architecture, tool blue-printing, and logic reviews.
- Editor Mode (Poolside Laguna XS 2.1): File updates, clean syntax adjustments, and precise pathspec handling.

## 2. G-STACK CORE COMPLIANCE

- Enforce the 23-specialist G-Stack workflow loop across development sprints: Think -> Plan -> Build -> Review -> Test -> Ship -> Reflect.
- Trigger the "Confusion Protocol" immediately: If an architectural direction or structural variable is ambiguous, stop execution and ask the user a forcing question instead of guessing.

## 3. EXPLICIT AGENT PIPELINE

- [[/office-hours]] / [[/plan-ceo-review]]: Handled by Architect Mode. Rethink product choices, challenge scopes, and build detailed architectural designs before modifying code.
- [[/review]] / [[/cso]]: Handled by Editor Mode. Run automated code reviews, check for broken absolute pathspecs, and execute structural security audits against OWASP Top 10 paths.
- [[/ship]]: Release automation framework. Sync master branch dependencies, execute local test suites, and format a clean Git history.

## 4. SYSTEM SKILLS DIRECTORY

The following modular skills are permanently active in memory as read-only guardrails. Enforce them completely:

- [[php-conventions]]: Mapped via `.aider-conventions/php-conventions.md`
- [[elgg-conventions]]: Mapped via `.aider-conventions/elgg-conventions.md`
- [[phpunit-conventions]]: Mapped via `.aider-conventions/phpunit-conventions.md`

## 5. RELATIVE PATHING GUARDRAILS

- Git repository context tree root is evaluated at: `./`
- DO NOT pass absolute filesystem directory metrics (`/home/daveonche/...`) to execution layer binaries.
