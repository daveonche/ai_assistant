# Sprint 5 Stories

## Story S5.1: Host-Side Per-Project Configuration (Replaces Root-Config Merging)

As a developer, I want per-project assistant customization through a trusted host-side args file so that project-specific settings (for example a different `test-cmd`) survive assistant updates and repository content can never configure the assistant.

Acceptance Criteria:

- The launcher no longer detects or reads project-root config counterparts: `.aider.conf.yml`, `.aider.model.settings.yml`, `.aiderignore`, and `.aider.model.metadata.json` in the project root are ignored; config flags always point at the `.agent/` copies
- The root-config merge machinery is removed from `.agent/ai_assistant.py`: counterpart detection, deep merge, model-settings merge, ignore-pattern union, the YAML/JSON subset parser and serializer, merged-config intermediates and their cleanup, and protected-key stripping (repo files are never read, so filtering becomes unnecessary)
- `./agent.sh --init-project-args` creates a commented template args file at `~/.config/aider-agent/projects/<project>-<hash8>.args` (same workspace-hash formula as the command log), refuses to overwrite an existing file, and works without Docker
- The args-file template includes commented examples for `--model-settings-file` and `--aiderignore` with override guidance: reference files under a distinctive name unlikely to exist in any repository (a hostile repo could ship a same-named file that silently satisfies the reference), create the referenced file in the project root and copy the needed entries from the `.agent/` copy so it is self-sufficient, and use the override only when a project genuinely needs extra or different configurations — otherwise leave the flag alone so the `.agent/` copy stays in force
- `./agent.sh --show-project-config` prints the args-file path, its contents, and the effective argument order (typed CLI > project args file > `.agent/` defaults), and works without Docker
- At launch, the args file loads with one argument token per line, blank lines and `#` comments ignored, no shell parsing; loaded tokens are prepended to the assistant arguments so explicitly typed CLI args win
- A TTY-gated launch line reports the args-file status: path and number of args loaded, or a hint to run `--init-project-args` when absent
- When a root config counterpart exists, a one-line notice states it is not read and points at `--init-project-args`
- README's "Mergeable configuration with your project root" section is replaced with a "Per-project customization" section documenting the args file, precedence, the project-directory-move caveat, and the same override guidance (distinctive filename, self-sufficient copy from the `.agent/` file, use only when needed); the install and update sections gain the one-line customization hint
- Verification suites cover: args loading and precedence, `--init-project-args` no-overwrite, the root-counterpart notice, and both flags working without Docker; obsolete merge tests are removed

Dependencies: None

Developer Notes:

- Maps to REQ-1, REQ-2 (launcher behavior) and REQ-14 (frictionless per-project setup)
- Security model: repository content can never configure the assistant; the args file lives in the user's home config directory — trusted, outside the repo, and untouched by assistant updates
- Unchanged guardrails: `.env` LLM-endpoint neutralization, the Dockerfile rebuild-approval gate, command-log placement, Docker-config sanitization
- Obsolete tests to remove: `tests/test_s4_1_step1.py`–`test_s4_1_step5.py`, `tests/test_audit_finding1_config_merge.py`, `tests/test_audit_finding2_ignore_negation.py`; `tests/test_audit_assistant_config_trust.py` survives
- The launcher is stdlib-only Python (host pin 3.12.12); the args-file path/hash math stays in the launcher — the installer delegates to the new flags rather than duplicating it
- README edit requires the GFM conventions reference at implementation time

## Story S5.2: Sprint 5 Record Documentation

As a developer, I want the Sprint 5 work recorded in the project docs, so that the sprint history and implementation status reflect the host-side per-project configuration work that replaced root-config merging.

Acceptance Criteria:

- `docs/implementation_status.md` gains a Sprint 5 section listing the S5.1 work as completed steps, and its Priority Order section is updated to reflect the new backlog state
- Documentation passes the markdown conventions

Dependencies: S5.1

Developer Notes:

- Follows the Sprint 3/Sprint 4 record-keeping pattern (S3.3, S4.4)
- Documentation-only; load the GFM conventions reference before editing (routing table)

## Sprint Technical Rationale

This sprint replaces S4.1's root-config merging with a host-side per-project args file: repository content loses all ability to configure the assistant (guardrails become structural instead of enforced), while per-project customization survives assistant updates because the args file lives outside `.agent/`. S5.1 and S5.2 form a minimal two-story sprint matching the project's established modification-plus-record pattern.
