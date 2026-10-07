# Elgg Developer Guide: Page Owner

Delta distillation of <https://learn.elgg.org/en/stable/guides/page-owner.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/page-owner.rst`, Elgg ref `7.1`). Records only what counters stale
training-data memory: current API names, signatures, defaults, deprecations,
gotchas. Update in place when the stable manual changes.

One recurring task of any plugin is to determine the page ownership in order
to decide which actions are allowed or not. Elgg has a number of functions
related to page ownership and also offers plugin developers flexibility by
letting the plugin handle page ownership requests as well.

## Core API

| Function | Purpose |
| :--- | :--- |
| `elgg_get_page_owner_guid()` | Returns the GUID of the owner of the current page |
| `elgg_get_page_owner_entity()` | Retrieves the whole page owner entity |
| `elgg_set_page_owner_guid($guid)` | Sets the page owner when the page already knows who the owner is but the system doesn't |

- Gotcha: the page owner entity can be any `ElggEntity`. If you wish to only
  apply some setting in case of a user or a group, make sure you check that
  you have the correct entity.

## Page owner detection

Based on the route definition:

- If the name starts with `view` or `edit` the parameters `username` and
  `guid` are checked
- If the name starts with `add` or `collection` the parameters `username`,
  `guid` and `container_guid` are checked
- If in the route definition the value `detect_page_owner` is set to `true`
  the parameters `username`, `guid` and `container_guid` are checked
