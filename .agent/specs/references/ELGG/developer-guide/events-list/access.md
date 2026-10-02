# Elgg Developer Guide: Events List — Access

Category table for the events-list distillation: marker legend and the
behavioral traps live in `../events-list.md`. Distilled from the stable
manual on 2026-09-30 (source: `docs/guides/events-list.rst`, Elgg ref
`7.1`); update in place when the stable manual changes.

## Access collection events

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `access_collection:url, access_collection` | results | filter the URL of the access collection; `$params['access_collection']` holds the `ElggAccessCollection` |
| `access_collection:name, access_collection` | results | filter the display name (readable access level) of the access collection; `$params['access_collection']` holds the `ElggAccessCollection` |
| `access:collections:read, user` | results | filter the array of access IDs the user `$params['user_id']` can see; the handler must not use APIs that re-trigger the event, or must ignore the second call — otherwise an infinite loop (see traps in `../events-list.md`) |
| `access:collections:write, user` | results | filter the array of access IDs the user `$params['user_id']` can write to; filters the return value of `elgg_get_write_access_array()`, so it alters the options in the `input/access` view; core plugins receive `input_params` with keys `entity` (`ElggEntity\|false`), `entity_type`, `entity_subtype`, `container_guid` — an empty entity generally means a create form; same infinite-loop constraint as the read event (see traps in `../events-list.md`) |
| `access:collections:write:subtypes, user` | results | return the array of access collection subtypes used when retrieving access collections owned by a user in `elgg_get_write_access_array()` |
| `access:collections:add_user, collection` | results | before adding user `$params['user_id']` to collection `$params['collection_id']`; return `false` to prevent adding |
| `access:collections:remove_user, collection` | results | before removing user `$params['user_id']` from collection `$params['collection_id']`; return `false` to prevent removal |
| `create, access_collection` | seq | during the creation of an `ElggAccessCollection` |
| `delete, access_collection` | seq | during the deletion of an `ElggAccessCollection` |
| `update, access_collection` | seq | during the update of an `ElggAccessCollection` |

## Access SQL events

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `get_sql, access` | results | filters the SQL clauses restricting/allowing access to entities and annotations; triggered even when access is ignored — check `$params['ignore_access']` and return early unless the clauses should apply in access-controlled contexts (see traps in `../events-list.md`); `$return` is a nested array of `ands` and `ors`; `$params` includes `table_alias`, `ignore_access`, `use_enabled_clause`, `access_column`, `owner_guid_column`, `guid_column`, `enabled_column`, and `query_builder` (a `QueryBuilder` instance) |
