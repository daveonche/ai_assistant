# GitHub Actions CI/CD Best Practices

Applies to every workflow file under `.github/workflows/*.yml` and
`*.yaml`. Summarized from the [GitHub Actions CI/CD Best Practices
instructions](https://github.com/github/awesome-copilot/blob/main/instructions/github-actions-ci-cd-best-practices.instructions.md)
in the `github/awesome-copilot` repository.

Use these rules when creating or reviewing GitHub Actions workflows.

## Workflow structure

- Start every workflow with a descriptive `name` and the narrowest
  appropriate `on` trigger (`push`, `pull_request`, `workflow_dispatch`,
  `schedule`, `repository_dispatch`, `workflow_call`).
- Use branch, tag, and path filters so workflows do not run when
  irrelevant.
- Name workflow files consistently and descriptively (e.g.,
  `build-and-test.yml`, `deploy-prod.yml`).
- Add a `concurrency` group for critical workflows or shared resources to
  prevent simultaneous runs and race conditions.
- Define `permissions` at the workflow level as a secure default;
  override at the job level only when needed.
- Extract patterns repeated across workflows into reusable workflows
  (`workflow_call`).

## Jobs

- Model each job as a distinct, independent phase (build, lint, test,
  security scan, deploy) with a clear `name` and an appropriate
  `runs-on`.
- Declare inter-job dependencies explicitly with `needs`.
- Pass data between jobs with job `outputs` instead of re-computing it.
- Use `if` conditions for conditional execution (branch, event type, or
  previous job status via `success()`, `failure()`, `always()`).
- Split large workflows into smaller focused jobs running in parallel or
  sequence.
- Set `timeout-minutes` on long-running jobs to prevent hung workflows.

## Steps and actions

- Give every step a descriptive `name` for readable logs and easier
  debugging.
- Pin every `uses` reference to a full-length commit SHA with a
  human-readable version comment:

  ```yaml
  uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4.3.1
  ```

- Never use mutable references (`@main`, `@latest`, or major tags such as
  `@v4`); a moved tag can execute attacker-controlled code in the
  pipeline (supply chain attack).
- Audit marketplace actions before use; prefer the trusted `actions/`
  organization and use Dependabot to keep pinned SHAs updated.
- Use `run` for shell commands; combine related commands with `&&` and
  use `|` blocks for multi-line scripts.
- Define `env` at the narrowest useful scope (step, then job, then
  workflow); never hardcode sensitive data.
- Supply all required action inputs via `with`; use `${{ }}` expressions
  for dynamic values.

## Security

### Secret management

- Store all sensitive values (API keys, passwords, cloud credentials,
  tokens) as GitHub Secrets and access them only via
  `secrets.<SECRET_NAME>`.
- Use environment-specific secrets with protection rules (manual
  approvals, branch restrictions) for deployment environments.
- Never print secrets to logs or construct them dynamically, even though
  GitHub masks them.

### OpenID Connect (OIDC)

- Prefer OIDC over long-lived static credentials for cloud
  authentication (AWS, Azure, GCP).
- OIDC exchanges a short-lived JWT for temporary cloud credentials;
  configure the cloud-side identity provider and trust policies to trust
  GitHub's OIDC issuer.
- Pin cloud credential actions (e.g.,
  `aws-actions/configure-aws-credentials@<SHA> # v4.x.x`) to full SHAs.

### Least privilege for GITHUB_TOKEN

- Explicitly set `permissions` on every workflow; start from
  `contents: read` and add write permissions only when strictly needed.
- Do not use `contents: write` or `pull-requests: write` unless the
  workflow must modify the repository.
- Override permissions per job when a job needs less than the workflow
  default.

### Supply chain scanning

- Integrate dependency review / SCA (e.g., `dependency-review-action`,
  Snyk, Trivy, Mend) early in the pipeline to catch vulnerable or
  license-problematic dependencies before deployment.
- Integrate SAST (CodeQL, SonarQube, Bandit, security-enabled ESLint)
  and make critical findings block builds or PRs.
- Enable secret scanning on the repository and recommend pre-commit
  secret-scanning hooks (e.g., `git-secrets`).
- Sign container images (Cosign, Notary) and verify signatures at
  deployment; aim for reproducible builds.

## Optimization and performance

### Caching

- Cache dependencies and build outputs with `actions/cache` (pinned to a
  full SHA).
- Build cache keys from dependency file hashes, e.g.
  `${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}`, so
  caches invalidate only when dependencies change.
- Provide `restore-keys` fallbacks for partial cache hits.
- Remember caches are scoped to the repository and branch.

### Matrix strategies

- Use `strategy.matrix` to test across OS, language versions, and
  browsers in parallel.
- Fine-tune combinations with `include`/`exclude`.
- Keep the default `fail-fast: true` for quick feedback on critical
  failures; use `fail-fast: false` when comprehensive reporting matters
  more.

### Checkout and artifacts

- Use `fetch-depth: 1` for checkout unless the job truly needs full
  history (release tagging, deep commit analysis).
- Skip submodules (`submodules: false`) and Git LFS (`lfs: false`) when
  not required.
- Pass build outputs between jobs with `actions/upload-artifact` and
  `actions/download-artifact` (both SHA-pinned) instead of rebuilding.
- Set explicit `retention-days` on artifacts to control storage cost and
  meet compliance needs.
- Upload test reports, coverage reports, and security scan results as
  artifacts.

### Runners

- Use self-hosted runners only when GitHub-hosted runners cannot meet
  hardware, network, or cost requirements.
- Self-hosted runners are your responsibility: hardening, patching,
  access control, network restriction, and scaling.

## Testing in CI

- Run fast unit tests on every push and pull request in a dedicated
  early job; parallelize them and publish coverage with a minimum
  threshold.
- Run integration tests after unit tests, provisioning databases,
  queues, and caches with job-level `services` (Docker containers) for
  consistency and isolation.
- Run E2E tests (Cypress, Playwright, Selenium) against a deployed
  staging environment; mitigate flakiness with explicit waits, robust
  selectors, and retries; capture screenshots and videos on failure.
- Add performance/load tests (JMeter, k6, Locust, Gatling) for critical
  applications on a less frequent schedule (nightly, weekly, or on major
  merges); define thresholds and fail the build when they are exceeded.
- Publish test results as GitHub Checks/Annotations for inline PR
  feedback and upload detailed reports (JUnit XML, HTML, coverage) as
  artifacts; add status badges to the README.

## Deployment

- Create dedicated GitHub `environment`s for staging and production with
  protection rules: required reviewers, branch restrictions, and secret
  isolation.
- Deploy to staging automatically on merges to development or release
  branches; keep staging as close to production as possible and run
  post-deployment smoke tests.
- Require manual approvals for production deployments and monitor
  closely during and after rollout.
- Choose the deployment type deliberately:
  - Rolling update: default for stateless apps; tune `maxSurge` and
    `maxUnavailable`.
  - Blue/green: zero-downtime releases with instant rollback; needs two
    environments and a traffic switch.
  - Canary: gradual rollout to a small user subset with metric-based
    analysis; needs traffic splitting.
  - Dark launch / feature flags: decouple deployment from release.
- Plan rollback: keep versioned artifacts and images retrievable,
  automate rollback on health-check or alert failures, document
  runbooks, and conduct blameless post-incident reviews.

## Review checklist

When reviewing a workflow, verify:

- [ ] Clear `name` and appropriate, filtered `on` triggers.
- [ ] `concurrency` set for critical workflows or shared resources.
- [ ] Workflow-level `permissions` follow least privilege
      (`contents: read` baseline) with job-level overrides.
- [ ] Every `uses` pinned to a full commit SHA with a version comment.
- [ ] Jobs named, ordered with `needs`, and communicating via `outputs`.
- [ ] `timeout-minutes` set for long-running jobs.
- [ ] Secrets accessed only via the `secrets` context; OIDC used for
      cloud auth where possible.
- [ ] SCA and SAST scanning integrated and blocking on critical
      findings.
- [ ] Caching with effective `key`/`restore-keys`; matrix used for
      parallelizable work; `fetch-depth: 1` checkout.
- [ ] Artifacts used for inter-job data with sensible
      `retention-days`.
- [ ] Unit, integration, and (where relevant) E2E and performance tests
      wired in with reports published.
- [ ] Environments protected, approvals configured, rollback strategy
      defined and tested.

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
the effective `permissions` block, and re-check every item in the review
checklist above.

When `actionlint` is not installed, a minimal PyYAML fallback checks
YAML syntax only. It does not catch workflow schema or semantic errors,
so treat a pass as necessary but not sufficient:

```bash
python3 -c "import glob, yaml; [yaml.safe_load(open(p)) for p in glob.glob('.github/workflows/*.y*ml')]; print('YAML OK')"
```
