# Sprint 4 Stories

## Story S4.1: Mergeable Aider Configuration with Project Root

As a developer, I want the launcher to make `.agent/`'s `.aider.conf.yml`, `.aider.model.settings.yml`, `.aiderignore`, and `.aider.model.metadata.json` mergeable with same-named files found in the project root, so that consumer projects can override or extend assistant defaults without editing the installed assistant files.

Acceptance Criteria:

- When a project-root counterpart of any of the four config files exists, the launcher combines the `.agent/` and project-root versions instead of passing only the `.agent/` copy
- Project-root values take precedence over `.agent/` defaults for `.aider.conf.yml`, `.aider.model.settings.yml`, and `.aider.model.metadata.json`; ignore patterns are combined (union) for `.aiderignore`
- When no project-root counterpart exists, launcher behavior is unchanged from the current single-file pass-through
- Merging is deterministic and the merge behavior is documented (README or prerequisite docs)
- Verification suites cover: merge case, no-counterpart case, and precedence rules

Dependencies: None

Developer Notes:

- Maps to environment/launcher requirements REQ-1, REQ-2
- Current behavior: `_aider_config_args()` in `.agent/ai_assistant.py` passes `--config`, `--model-settings-file`, `--aiderignore`, and `--model-metadata-file` pointing solely at the `.agent/` copies
- The launcher is stdlib-only Python (host pin 3.12.12) — implement YAML-aware merging within that constraint
- Shell/Python changes must pass the existing static checks and verification suites

## Story S4.2: Framework Detection and Conventions Recommendation

As a developer, I want the assistant to detect the framework used in the `src/` directory and recommend the matching conventions file from `.agent/.aider.conventions/` (e.g., `ELGG.md`, `RAILS.md`), so that coding guidance automatically follows the detected framework's conventions.

Acceptance Criteria:

- The assistant inspects the project (framework indicators under `src/` and root manifests/config files) to identify the framework in use
- When a detected framework has a matching conventions file in `.agent/.aider.conventions/`, the assistant recommends loading it via `/read-only`, following the routing conventions in `.agent/AGENTS.md`
- When no matching conventions file exists for the detected framework, no recommendation is made
- Seed convention files `ELGG.md` and `RAILS.md` are added to `.agent/.aider.conventions/` with meaningful starter content and pass the markdown conventions
- The framework-based routing rule is documented in the conventions routing table in `.agent/AGENTS.md`

Dependencies: None

Developer Notes:

- Maps to REQ-7 (project-specific prompt library) and REQ-9 (SDLC best practices enforcement)
- Detection is performed by the LLM via AGENT.md orchestration instructions (indicators such as `composer.json`, `Gemfile`, `package.json`), not by launcher code
- Creating/editing `ELGG.md`, `RAILS.md`, and `AGENT.md` requires the GFM conventions reference (already in context) and, per the routing table, the agent-skills reference for `SKILL.md` files if any are touched

## Story S4.3: README `--auto` Release Example Fix

As a developer, I want the `--auto` increment example in the README "Cutting a release" section corrected, so that it shows the patch segment changing and matches the usage text in `scripts/release.sh`.

Acceptance Criteria:

- The README `--auto` example shows the patch segment changing (e.g., `v1.0.3` -> `v1.0.4`), consistent with the correct usage example in `scripts/release.sh` (`v1.0.2` -> `v1.0.3`)
- The full test suite remains green (release-reference consistency checks unaffected)
- Documentation passes the markdown conventions

Dependencies: None

Developer Notes:

- Supports REQ-15 (release-reference consistency across documented instructions)
- Resolves the non-blocking nit recorded in `docs/implementation_status.md`; documentation-only
- GFM conventions reference already in context

## Story S4.5: Container SSH Support for Git Remotes

As a developer, I want the launcher to bootstrap SSH so git push/pull over SSH remotes works inside the session container, so that remote operations never stall on host-key or passphrase prompts.

Acceptance Criteria:

- The launcher mounts the host `~/.ssh` directory read-only into the container at the identical path when it exists, so keys, config, and `known_hosts` travel together and the container cannot modify host SSH state
- The launcher forwards the host ssh-agent socket at its identical path and passes `SSH_AUTH_SOCK` by name when the socket exists, so passphrase-protected keys work without copying them
- The entry script starts or reuses a persistent per-user ssh-agent on a fixed socket before launch; interactive-only, best-effort, and never fatal — when no agent ends up reachable the variable is dropped so the container falls back to direct-key auth
- The image installs `openssh-client` so `ssh` and git-over-SSH work inside the container
- The entry script pins GitHub's published SSH host keys for `github.com` so first-use connections never stall on a host-key prompt: ed25519 and ecdsa keys are embedded, the rsa key is fetched from `api.github.com` once, and every key is appended only after its SHA256 fingerprint matches GitHub's published value; pinning is idempotent, skipped for non-TTY callers, and never fatal
- SSH usage and the host-key rotation caveat are documented in `README.md`

Dependencies: S1.5

Developer Notes:

- Extends the S1.5 containerization layer; no installer or configuration changes
- Embedded key blobs are split across concatenated literals to satisfy the 80-character script rule; a mangled chunk is caught by re-deriving the fingerprints with `ssh-keygen -lf -`
- Rotation behavior: the read-only mount means a rotated GitHub key requires removing the stale `github.com` line from the host `known_hosts` (`ssh-keygen -R github.com`) and relaunching with an updated entry script; the rsa key self-heals because it is re-fetched and re-verified whenever no rsa key is pinned

Definition of Done:

- `tests/test_s1_5_step2.py` covers the read-only `~/.ssh` mount and agent-socket forwarding; full suite green
- Fingerprint re-derivation from the embedded literals prints GitHub's published values
- `README.md` documents the behavior

## Story S4.6: Container Build Tooling Fixes

As a developer, I want `docker compose build` to work inside the session container, so that debugging sibling compose stacks does not fail on missing buildx tooling or read-only state.

Acceptance Criteria:

- The image installs `docker-buildx-plugin` so in-container `docker compose build` runs without a missing-buildx warning
- The launcher redirects Buildx's mutable state to the writable cache mount (`BUILDX_CONFIG=/home/.cache/buildx`), because `~/.docker` is mounted read-only for registry credentials only

Dependencies: S1.5

Developer Notes:

- Both fixes serve Docker-outside-of-Docker: sibling compose builds run against the host daemon through the mounted socket
- Verified alongside the S4.5 tests in `tests/test_s1_5_step2.py`

Definition of Done:

- `tests/test_s1_5_step2.py` asserts the `BUILDX_CONFIG` redirect; full suite green
- The CI image build smoke test exercises the Dockerfile including the plugin layer

## Story S4.7: Container Image Pins and Offline Pre-bakes

As a developer, I want the image-internal component pins and offline pre-bakes recorded so that the image's reproducibility decisions are visible in the project documentation alongside the base-image pin.

Acceptance Criteria:

- `docs/tech_stack.md` gains an "Image-Internal Component Pins" table covering ShellCheck, pytest, the embedding model, Node.js, mermaid-cli, and the distro-managed packages, with each pin's nature
- The Version Lock Rationale states the exact-pin scope and records the accepted ecosystem deviations (Node.js major line, mermaid-cli caret range, distro-managed packages)
- The deliberate choices are documented: the static ShellCheck binary instead of the npm wrapper, the pre-baked embedding model for offline first run, and Puppeteer pointed at the system Chromium

Dependencies: S1.5

Developer Notes:

- Documentation-only; the image itself is unchanged
- Evidence: `.agent/Dockerfile.aider` layers A through D3 and the CI image build smoke test (`tests/test_s1_6_step4.py`)

Definition of Done:

- `docs/tech_stack.md` records every image-internal pin and the deviation note
- Documentation passes the markdown conventions

## Story S4.4: Sprint 4 Record Documentation

As a developer, I want the Sprint 4 work recorded in the project docs, so that the sprint history and implementation status reflect the config-merging, framework-detection, and README-fix work.

Acceptance Criteria:

- `docs/implementation_status.md` gains a Sprint 4 section listing the S4.1, S4.2, S4.3, S4.5, S4.6, and S4.7 work as completed steps, and its Priority Order section is updated to reflect the new backlog state
- Documentation passes the markdown conventions

Dependencies: S4.1, S4.2, S4.3, S4.5, S4.6, S4.7

Developer Notes:

- Follows the Sprint 3 record-keeping pattern (S3.3, Sprint 3 section in `docs/implementation_status.md`)
- Documentation-only; GFM conventions reference already in context

## Sprint Technical Rationale

These stories pair the two user-introduced features (config merging, framework-aware conventions) and the one recorded documentation nit with three later additions from the same sprint's needs: S4.5 restores seamless SSH git operations in the container (read-only `~/.ssh` mount, agent forwarding, ssh-agent bootstrap, and fingerprint-verified GitHub host-key pinning), S4.6 fixes in-container compose builds (buildx plugin plus writable buildx state), and S4.7 records the image-internal component pins and offline pre-bakes. S4.1, S4.2, S4.3, S4.5, S4.6, and S4.7 are independent of one another; S4.4 depends on all of them.
