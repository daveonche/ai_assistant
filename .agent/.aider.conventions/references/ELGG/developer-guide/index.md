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
| `menus.md` | `menus.rst` | menu system | done |
| `notifications.md` | `notifications.rst` | notification system | done |
| `page-owner.md` | `page-owner.rst` | page owner detection | done |
| `permissions-check.md` | `permissions-check.rst` | write-permission override via `permissions_check` event | done |
| `plugins.md` | `plugins.rst` | static config (`elgg-plugin.php`), bootstrap, DI services, composer, tests | done |
| `restore.md` | `restore.rst` | trash/restore via `restorable` capability, deletion functions, cleanup cron | done |
| `river.md` | `river.rst` | activity stream: `elgg_create_river_item()`, view/summary fallback chains, `river_emittable` | done |
| `routing.md` | `routing.rst` | route registration/names, middleware gatekeepers, generic controllers, `route:rewrite` | done |
| `search.md` | `search.rst` | `elgg_search()` params, `search:fields`/`search:config` events, livesearch endpoints | done |
| `services.md` | `services.rst` | service providers | done |
| `settings.md` | `settings.rst` | plugin/user/group settings forms, get/set APIs, defaults | done |
| `themes.md` | `themes.rst` | theming principles, CSS view map, variables/dark mode, view extension/overload, icons | done |
| `upgrading-data.md` | `upgrading-data.rst` | async plugin upgrades: `AsynchronousUpgrade` contract, `Result` API, admin panel | done |
| `views.md` | `views.rst` | `elgg_view()`, `$vars`, cacheable assets, viewtypes, override/extend, view events, entity listing, icons | done |
| `walled-garden.md` | `walled-garden.rst` | walled garden mode: admin toggle, `'walled' => false` routes, `public_pages` event | done |
| `web-services.md` | `web-services.rst` | exposing methods, param types, API/user auth, PAM setup | done |
| `widgets.md` | `widgets.rst` | widget registration (`elgg-plugin.php`/`elgg_register_widget_type()`), edit/content views, default widgets | done |

## Subdirectories (subpages)

| Directory / subpage | Source | Status |
| :--- | :--- | :--- |
| `plugins/` | `docs/guides/plugins/` | enumerated 2026-10-01 — 3 subpages below |
| `plugins/bootstrap.md` | `docs/guides/plugins/bootstrap.rst` | plugin bootstrap | done |
| `plugins/dependencies.md` | `docs/guides/plugins/dependencies.rst` | plugin dependencies | done |
| `plugins/plugin-skeleton.md` | `docs/guides/plugins/plugin-skeleton.rst` | plugin file skeleton | pending |
| `views/` | `docs/guides/views/` | enumerated 2026-09-30 — 3 subpages below |
| `views/foot-vs-footer.md` | `docs/guides/views/foot-vs-footer.rst` | foot vs footer views | done |
| `views/page-structure.md` | `docs/guides/views/page-structure.rst` | page structure | done |
| `views/simplecache.md` | `docs/guides/views/simplecache.rst` | simplecache | done |
| `web-services/` | `docs/guides/web-services/` | enumerated 2026-09-30 — 2 subpages below |
| `web-services/hmac.md` | `docs/guides/web-services/hmac.rst` | HMAC signature authentication | done |
| `web-services/result.md` | `docs/guides/web-services/result.rst` | API result format | done |

Enumerate each with the same contents-API call used for `docs/guides/`
(`?ref=7.1`, path substituted) when its topics are distilled.

## Notes

- `index.rst` is the manual's TOC (a `:glob:` toctree); it is not distilled
  as a topic.
- Baseline contents listing kept at `source-listing-7.1.json` (per-file SHAs
  and sizes): diff a fresh listing against it to find upstream changes.
- `events-list.rst` is large (~58 KB); distill as a compact lookup list or
  split it if it exceeds the topic-file size cap.
