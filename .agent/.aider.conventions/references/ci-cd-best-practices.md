# GitHub Actions CI/CD Delta Reference

Applies to every workflow file under `.github/workflows/*.yml` and
`*.yaml`. A delta reference: only repo-relevant rules, easily-got-wrong
details, and exact syntax that supplement built-in CI/CD knowledge.
Generic best practices are intentionally omitted.

## SHA pinning verification

Pin every `uses` reference to a full-length commit SHA with a version
comment. Before merging, verify each SHA against its upstream tag:

```bash
git ls-remote https://github.com/actions/<action>.git 'refs/tags/<version>*'
```

- One advertised line means a lightweight tag: the SHA shown is the
  commit to pin.
- A second line ending in `^{}` means an annotated tag: pin the SHA from
  the `^{}` line, not the tag object SHA.
- Empty output with exit code 0 means the tag does not exist as queried;
  list candidates with
  `git ls-remote --tags https://github.com/actions/<action>.git 'refs/tags/<major>*'`.
- Never use mutable references (`@main`, `@latest`, or major tags such
  as `@v4`).

## Review checklist (easily-missed items)

- [ ] Every `uses` pinned to a full commit SHA with a version comment.
- [ ] Workflow-level `permissions` explicitly set (`contents: read`
      baseline) with job-level overrides.
- [ ] Cache keys change only when the cached content changes (no
      `github.run_id`).
- [ ] `fetch-depth: 0` used only when full history is genuinely
      required.
- [ ] `paths-ignore`/`branches-ignore` precedence considered when
      debugging skipped triggers.
- [ ] Flaky tests isolated; no bare `sleep` waits.
- [ ] Artifact `retention-days` set where storage cost or compliance
      matters.

## Gotchas

- Tags and branches on actions are mutable; `@v4` can be silently moved
  to a malicious commit. Only full-length commit SHAs are immutable.
- `GITHUB_TOKEN` defaults are broad; an unset `permissions` block is a
  security finding, not a convenience.
- A cache key that is too dynamic (e.g., includes `github.run_id`)
  always misses; keys must change only when the cached content changes.
- `fetch-depth: 0` on large repositories is slow; only use it when full
  history is genuinely required.
- `paths-ignore` and `branches-ignore` take precedence over their
  positive counterparts; a skipped trigger is often a filter mismatch.
- Flaky tests erode trust in the pipeline; replace `sleep` with explicit
  waits and isolate non-deterministic tests.
- Artifacts are immutable once uploaded; a bad artifact can only be
  rebuilt and re-uploaded, never patched.

## Validation

Before committing workflow changes, validate with `actionlint` (or `act`
for local runs), confirm every `uses` reference is SHA-pinned, review
the effective `permissions` block, and re-check the checklist above.

When `actionlint` is not installed, a minimal PyYAML fallback checks
YAML syntax only. It does not catch workflow schema or semantic errors,
so treat a pass as necessary but not sufficient:

```bash
python3 -c "import glob, yaml; [yaml.safe_load(open(p)) for p in glob.glob('.github/workflows/*.y*ml')]; print('YAML OK')"
```
