# Sprint 3 Stories

## Story S3.1: Release Reference Consistency Verification

As a developer, I want the existing release-reference consistency checks verified against REQ-15 so that the enforced pin across `DEFAULT_REF`, documented install URLs, and the tested install command is confirmed correct.

Acceptance Criteria:

- `tests/test_release_ref_consistency.py` passes, proving `scripts/install.sh` (`DEFAULT_REF` + usage examples), `README.md` install URLs, and `tests/test_s2_1_step5.py` all pin the same ref (`v1.0.3`)
- The checks' failure messages identify the mismatched location
- Any inconsistency found is fixed in the same change

Dependencies: None

Developer Notes:

- Verification-focused; only edit source files if a check exposes a real mismatch

## Story S3.2: Release Tag Guard Verification

As a developer, I want the CI `release-tag-guard` job verified so that a tag cannot ship with a stale installer pin.

Acceptance Criteria:

- The `release-tag-guard` job in `.github/workflows/ci.yml` runs on `v*` tag pushes and asserts the tag equals `DEFAULT_REF`
- All `uses:` references remain pinned to full-length verified commit SHAs per `docs/tech_stack.md`
- A green CI run on the current `main` is recorded as evidence

Dependencies: S3.1

Developer Notes:

- Load the CI/CD conventions reference only if workflow edits become necessary

## Story S3.3: Release Work Sprint-Record Documentation

As a developer, I want the release-management work recorded in the project docs so that the sprint history and implementation status reflect the completed REQ-15 implementation.

Acceptance Criteria:

- `docs/implementation_status.md` gains a Sprint 3 section listing the release-consistency, tag-guard, and release-script work as completed steps
- `docs/tech_stack.md` references the release tooling (`scripts/release.sh`, `release-tag-guard`) where relevant to the pin philosophy
- Documentation passes the project's markdown conventions

Dependencies: S3.1, S3.2

Developer Notes:

- Documentation-only; load the markdown conventions reference before editing (routing table)

## Sprint Technical Rationale

The backlog is empty, so Sprint 3 formally verifies and records the REQ-15 release-management implementation already present in the tree: S3.1 proves pin consistency, S3.2 proves the release gate, and S3.3 records the work so the sprint history is complete.
