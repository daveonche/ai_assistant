# Elgg Developer Guide: Topic Map

Index for the Elgg developer-guide distillations under this directory. Built
from the GitHub contents listing of `docs/guides/` in the Elgg repository
(ref `7.1`, retrieved 2026-09-30) — the source of the stable manual at
<https://learn.elgg.org/en/stable/guides/index.html>.

Load rule: load this `index.md` first, then only the topic files the current
task touches. Topic files track the stable manual and are updated in place;
the per-version change list that drives updates lives in
`../upgrade-notes/`.

Topic-file names mirror their source page (`access.md` ↔ `access.rst`), so
upstream diffs map mechanically onto updates. Scopes below are provisional
(derived from source filenames); each distilled topic file's own header is
authoritative. Status: `pending` = not yet distilled.

## Topics

| Topic file | Source page | Scope (provisional) | Status |
| :--- | :--- | :--- | :--- |
| `access.md` | `access.rst` | access system: read/write controls | done |
| `accessibility.md` | `accessibility.rst` | accessibility practices | done |
| `actions.md` | `actions.rst` | actions: form submission handlers | done |
| `ajax.md` | `ajax.rst` | Ajax API | done |
| `authentication.md` | `authentication.rst` | authentication handlers and APIs | done |
| `capabilities.md` | `capabilities.rst` | capability checks | done |
| `context.md` | `context.rst` | page context stack | done |
| `cron.md` | `cron.rst` | cron periods and jobs | done |
| `database.md` | `database.rst` | database layer and queries | done |
| `dont-modify-core.md` | `dont-modify-core.rst` | policy: never modify core | done |
| `email.md` | `email.rst` | email sending and handling | done |
| `errors.md` | `errors.rst` | error logging via Monolog and custom handlers | done |
| `events-list.md` | `events-list.rst` | reference list of events and hooks | done |
| `file-system.md` | `file-system.rst` | file storage | done |
| `group-tools.md` | `group-tools.rst` | group tool options | done |
| `guidelines.md` | `guidelines.rst` | coding guidelines | done |
| `helpers.md` | `helpers.rst` | helper functions | done |
| `i18n.md` | `i18n.rst` | translations and languages | done |
| `javascript.md` | `javascript.rst` | JS modules and `elgg` JS API | done |
| `menus.md` | `menus.rst` | menu system | pending |
| `notifications.md` | `notifications.rst` | notification system | pending |
| `page-owner.md` | `page-owner.rst` | page owner detection | pending |
| `permissions-check.md` | `permissions-check.rst` | permission callbacks | pending |
| `plugins.md` | `plugins.rst` | plugin structure and lifecycle | pending |
| `restore.md` | `restore.rst` | restore procedures | pending |
| `river.md` | `river.rst` | activity river | pending |
| `routing.md` | `routing.rst` | routes and page handlers | pending |
| `search.md` | `search.rst` | search API | pending |
| `services.md` | `services.rst` | service providers | done |
| `settings.md` | `settings.rst` | plugin and user settings | pending |
| `themes.md` | `themes.rst` | theming | pending |
| `upgrading-data.md` | `upgrading-data.rst` | plugin data upgrades | pending |
| `views.md` | `views.rst` | view system | pending |
| `walled-garden.md` | `walled-garden.rst` | walled garden mode | pending |
| `web-services.md` | `web-services.rst` | web services API | pending |
| `widgets.md` | `widgets.rst` | widget system | pending |

## Subdirectories (subpages not yet enumerated)

| Directory | Source | Status |
| :--- | :--- | :--- |
| `plugins/` | `docs/guides/plugins/` | pending |
| `views/` | `docs/guides/views/` | pending |
| `web-services/` | `docs/guides/web-services/` | pending |

Enumerate each with the same contents-API call used for `docs/guides/`
(`?ref=7.1`, path substituted) when its topics are distilled.

## Notes

- `index.rst` is the manual's TOC (a `:glob:` toctree); it is not distilled
  as a topic.
- Baseline contents listing kept at `source-listing-7.1.json` (per-file SHAs
  and sizes): diff a fresh listing against it to find upstream changes.
- `events-list.rst` is large (~58 KB); distill as a compact lookup list or
  split it if it exceeds the topic-file size cap.
