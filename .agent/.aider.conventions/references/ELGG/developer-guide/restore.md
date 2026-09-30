# Elgg Developer Guide: Restore Capability

Delta distillation of <https://learn.elgg.org/en/stable/guides/restore.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/restore.rst`, Elgg ref `7.1`). Records only what counters
stale training-data memory: current API names, signatures, defaults,
deprecations, gotchas. Update in place when the stable manual changes.

Since Elgg 6.0 an `ElggEntity` can carry the `restorable` capability (see
`capabilities.md`): `ElggEntity::delete()` then marks the entity as deleted
in the database instead of removing it. A deleted entity no longer shows up
in listings and does not work when viewed directly. Restore features are
OFF by default site-wide.

## Site setting

- A site administrator enables/disables all restore features; default is
  disabled.
- Gotcha: with the feature disabled, an entity with the `restorable`
  capability is still permanently removed from the database — the
  capability alone changes nothing.

## Registration

Enable the capability in `elgg-plugin.php` like any other entity
capability:

```php
'entities' => [
   [
      'type' => 'object',
      'subtype' => 'my_custom_subtype',
      'capabilities' => [
         'restorable' => true,
      ],
   ],
],
```

## Entity menu and generic actions

- By default the entity menu gets a delete item (when the user has the
  rights); for `restorable` entities it is replaced by an item that marks
  the entity as deleted.
- Gotcha: when the site administrator has not enabled the feature, no menu
  items are replaced.
- Two generic actions for developers (both require a `guid`):

| Action | Effect |
| :--- | :--- |
| `entity/delete` | permanently deletes the entity from the database |
| `entity/trash` | marks the entity as deleted in the database |

## Viewing deleted items

- Deleted entities disappear from normal site functionality.
- A link in the user settings lists all deleted items owned by that user.
- Group owners see deleted content contained by their group from the group
  profile page.
- Gotcha: the lists show only deleted entities with the `restorable`
  capability. A deleted blog's comments never appear in any deleted-items
  list — only the blog does (owner list, and the group's list if it was
  posted in a group).

## Custom trash views

- View chain for a deleted item: `trash/<entity_type>/<entity_subtype>` →
  fallback `trash/<entity_type>/default` → core-provided
  `trash/entity/default`; the deleted entity is passed in `$vars['entity']`.
- Sub-elements live in the `trash/elements/*` views.
- Gotcha: a custom trash view must not link to the deleted entity (the link
  will not work); also beware links to other entities that could have been
  deleted.

## Restoring

- From the deleted list the user (or group owner) restores an item to its
  original state.
- If the entity was contained in a group that was removed, the user can
  restore it to a different container.

## Events

- Marking an entity as deleted triggers the `'trash', '<entity_type>'`
  event sequence for additional program logic.

## ElggEntity deletion functions

The page says "3 functions" but lists four — `isDeleted()` is the fourth:

| Function | Visibility | Purpose |
| :--- | :--- | :--- |
| `delete(bool $recursive = true, ?bool $persistent = null): bool` | public | the only public delete entry point |
| `persistentDelete(bool $recursive = true): bool` | protected | permanent removal |
| `trash(bool $recursive = true): bool` | protected | mark as deleted |
| `isDeleted(): bool` | public | is the entity marked as deleted |

- `delete()`: `$recursive` (default `true`) also deletes entities that have
  this entity as owner or container. `$persistent` forces permanent removal
  (`true`) or trash (`false`); default `null` defers to the `restorable`
  capability check.
- Warning: do not overrule `delete()` — the overruling developer must then
  handle the logic of determining the correct `$persistent` value.
- `persistentDelete()`: called when `$persistent` is `true`; triggers the
  `'delete', '<entity_type>'` event sequence. Overrule it e.g. in
  `ElggFile` to remove the physical file from disk on permanent removal but
  keep it when the entity is only trashed.
- `trash()`: called when `$persistent` is `false`; triggers the
  `'trash', '<entity_type>'` event sequence.

## Including/excluding deleted entities in queries

- To be sure to include deleted entities when fetching/listing, wrap the
  code in `elgg_call()` with the flag `ELGG_SHOW_DELETED_ENTITIES`.
- `ELGG_HIDE_DELETED_ENTITIES` is the counterpart to be sure to exclude all
  deleted items.

## Cleanup cron

- An hourly cron job removes deleted entities whose retention period has
  passed; the site administrator sets the retention period (default:
  30 days).
- The cron runs at most 5 minutes per hour; leftovers are removed in the
  next period.
- Order: oldest deleted entity first (by when the entity was deleted).

## More information

- See the capabilities documentation (`capabilities.md`).
