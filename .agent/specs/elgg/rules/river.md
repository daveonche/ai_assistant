# Elgg Developer Guide: River

Delta distillation of <https://learn.elgg.org/en/stable/guides/river.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/river.rst`, Elgg ref `7.1`). Records only what counters
stale training-data memory: current API names, signatures, defaults,
deprecations, gotchas. Update in place when the stable manual changes.

The river is Elgg's activity stream: descriptions of activities performed
by site members. Plugins push items with `elgg_create_river_item()`; views
and summaries resolve through fallback chains keyed on the object entity's
`type`/`subtype`.

## Pushing river items

```php
elgg_create_river_item([
   'view' => 'river/object/blog/create',
   'action_type' => 'create',
   'subject_guid' => $blog->owner_guid,
   'object_guid' => $blog->getGUID(),
]);
```

All parameters:

| Parameter | Type | Meaning |
| :--- | :--- | :--- |
| `view` | STR | view that handles the river item (must exist) |
| `action_type` | STR | arbitrary action string (`create`, `update`, `vote`, `review`, ...) |
| `subject_guid` | INT | GUID of the entity doing the action (default: logged-in user guid) |
| `object_guid` | INT | GUID of the entity being acted upon |
| `target_guid` | INT | GUID of the object entity's container (optional) |
| `access_id` | INT | access ID of the river item (default: same as the object) |
| `posted` | INT | UNIX epoch timestamp of the river item (default: now) |
| `annotation_id` | INT | annotation ID associated with the entry (optional) |

- Gotcha: the example passes `$blog->owner_guid` as `subject_guid` — the
  subject is the actor, not the acted-upon entity.
- When an item is deleted or changed, the river item is updated
  automatically.

## River view fallback chain

As of Elgg 3.0 the `view` parameter is no longer required; Elgg checks in
order (both `type` and `subtype` come from the `object_guid` entity):

1. `river/{$type}/{$subtype}/{$action_type}` — e.g. `river/object/blog/create`
2. `river/{$type}/{$subtype}/default` — e.g. `river/object/blog/default`
3. `river/{$type}/{$action_type}` — e.g. `river/object/create`
4. `river/{$type}/default` — e.g. `river/object/default`
5. `river/elements/layout` — ultimate fallback; should always be called by
   any river view for a consistent layout

## Summary

Without a `summary` parameter, `river/elements/layout` builds one of the
form "Somebody did something on Object" (linked subject and object) from
the first matching language key:

1. `river:{$type}:{$subtype}:{$action_type}` — e.g. `river:object:blog:create`
2. `river:{$type}:{$subtype}:default` — e.g. `river:object:blog:default`
3. `river:{$type}:{$action_type}` — e.g. `river:object:create`
4. `river:{$type}:default` — e.g. `river:object:default`

## Custom river view

- The `view` passed to `elgg_create_river_item()` MUST exist; recommended
  naming: `river/{type}/{subtype}/{action}`.
- The river item arrives as `$vars['item']` with (at least)
  `$vars['item']->subject_guid` and `$vars['item']->object_guid`;
  timestamps etc. are generated for you.
- Blog plugin pattern — extract, guard, inject `$vars['message']`, then
  delegate to the layout:

```php
$item = elgg_extract('item', $vars);
if (!$item instanceof ElggRiverItem) {
   return;
}

$blog = $item->getObjectEntity();
if (!$blog instanceof ElggBlog) {
   return;
}

$vars['message'] = $blog->getExcerpt();

echo elgg_view('river/elements/layout', $vars);
```

## Capability

- Entities can carry the `river_emittable` capability (see
  `capabilities.md`). It determines whether the type/subtype is filterable
  on activity pages and, when not explicitly requested, filters the entity
  out of `elgg_get_river()` queries.
- With the default `EntityEditAction`, the capability also determines
  whether the default `create` river activity is created.
