# Elgg Developer Guide: Permissions Check

Delta distillation of <https://learn.elgg.org/en/stable/guides/permissions-check.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/permissions-check.rst`, Elgg ref `7.1`). Records only what counters
stale training-data memory: current API names, signatures, defaults,
deprecations, gotchas. Update in place when the stable manual changes.

The `permissions_check` event (cross-referenced from `events-list.md`) lets a
plugin override write permission checks, so plugin code can write to all
accessible entities regardless of access settings. Hidden entities remain
unavailable to the plugin either way.

## Scope warning

- This mechanism works **only** for granting **write** access to entities.
- It cannot be used to retrieve or view entities for which the user does not
  have read access.

## Registration

```php
elgg_register_event_handler('permissions_check', 'all', 'myplugin_permissions_check');
```

## Handler contract

The handler receives an `\Elgg\Event` and can return three values:

| Return | Meaning |
| :--- | :--- |
| `true` | the entity has write access |
| `false` | the entity does not have write access |
| `null` | this plugin doesn't care; the security system consults other plugins |

```php
function myplugin_permissions_check(\Elgg\Event $event) {
   $has_access = determine_access_somehow();

   if ($has_access === true) {
      return true;
   } else if ($has_access === false) {
      return false;
   }

   return null;
}
```

- Gotcha: keep Elgg secure — grant write access only after checking a
  variety of situations, including page context and the logged-in user.

## Context-scoped pattern (page's full example)

1. `myaccess_init()` registers the `permissions_check` handler and a cron
   handler whose period comes from
   `elgg_get_plugin_setting('period', 'myaccess', 'fiveminute')`.
2. The cron handler wraps its work in `elgg_push_context('myaccess_cron')` /
   `elgg_pop_context()`; inside that context `get_entities()` returns all
   entities regardless of access permissions, but will NOT return hidden
   entities.
3. `myaccess_permissions_check()` returns `true` only when
   `elgg_in_context('myaccess_cron')`; otherwise `null`.

- Gotcha: the example's closing line registers `init` with
  `register_elgg_event_handler('init', 'system', 'myaccess_init')` — a
  non-`elgg_`-prefixed form inconsistent with the
  `elgg_register_event_handler(...)` used everywhere else on the page;
  prefer the `elgg_` form.
