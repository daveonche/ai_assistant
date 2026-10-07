# Elgg Developer Guide: Events List

Delta distillation of <https://learn.elgg.org/en/stable/guides/events-list.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/events-list.rst`, Elgg ref `7.1`). This main file holds the
marker legend and the behavioral traps that counter stale training-data
memory; exhaustive per-category event tables live in the `events-list/`
directory next to this file. Update in place when the stable manual changes.
Event mechanics (triggering, handler priorities, `:before`/`:after`
variants) are covered by the manual's `design/events` page, not here.

## Detail references

Exhaustive per-category tables live in the `events-list/` directory; load on
demand for the category the current task touches.

- `events-list/system.md` — system events: boot sequence, caches, cron,
  menus, page shell, translations, upgrades
- `events-list/users.md` — user events: ban, login/logout, profile,
  registration and validation, user settings
- `events-list/entities.md` — entity, relationship, metadata, annotation,
  and river lifecycle events
- `events-list/access.md` — access collection and access SQL events
- `events-list/permissions.md` — permission checks and gatekeeper events
- `events-list/notifications.md` — notification queue, subscription,
  preparation, and delivery events, plus email events
- `events-list/files.md` — file upload, download URL, and mimetype events
- `events-list/actions-ajax.md` — action validation and Ajax result events
- `events-list/routing.md` — response, route config, rewrite, and match
  events
- `events-list/views.md` — view, form, page shell, and HTMLawed events
- `events-list/search.md` — search plugin events
- `events-list/other.md` — config, icon, form fields, widgets, maintenance,
  plugin settings, robots.txt, `to:object`, and bundled-plugin (site pages,
  groups, web services) events

## Marker legend

Category tables mark each event with:

- `seq` — the event also fires as `:before` and `:after` variants
- `results` — the return value is used: handlers act as filters and must
  return the (possibly altered) value
- `seq + results` — both apply

## Traps

- `register, user` fires from the `register` action only — `register_user()`
  does *not* trigger it. Return `false` to delete the just-registered user;
  throw `\Elgg\Exceptions\Configuration\RegistrationException` to show the
  user a message.
- `usersettings:save, user`: return `false` to keep sticky forms (values not
  saved), `null` on success; never return `true` — it overrides other
  handlers' output.
- `access:collections:read, user` / `access:collections:write, user`:
  handlers must avoid APIs that re-trigger the event, or ignore the second
  call — otherwise an infinite loop.
- `get_sql, access` fires even when access is ignored: check
  `$params['ignore_access']` and return early unless the clauses should
  apply in access-ignored contexts.
- `gatekeeper, <type>:<subtype>` receives the entity fetched with ignored
  access and including disabled entities — never use it to bypass the access
  system. Return `false`, an `\Elgg\Exceptions\HttpException`, or `true` to
  override the result.
- `container_permissions_check, <entity_type>` is called twice when neither
  `container_guid` nor `owner_guid` matches the logged-in user; the first
  call passes the *owner* as `container`.
- Metadata and annotation `update` handlers that return `false` cause the
  metadata/annotation to be *deleted*, not left unchanged.
- `shutdown, system`: the session is already closed; preferred over
  `register_shutdown_function` (services remain available); long-running
  work may still delay page load depending on server output buffering.
- `route:config, <route_name>` and `route:rewrite, <identifier>` handlers
  must be registered outside `init, system` (core routes register during
  `plugins_boot`; rewrites run after it).
- `public_pages, walled_garden`: system public routes arrive as the default
  value — extend the regex list, never replace it wholesale.
- `get, subscriptions`: validate the notification event, object, and action
  before adding recipients, or instant notifications (e.g. mentions) can
  reach the wrong users.
