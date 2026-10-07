# Elgg Developer Guide: Events List — Permissions

Category table for the events-list distillation: marker legend and the
behavioral traps live in `../events-list.md`. Distilled from the stable
manual on 2026-09-30 (source: `docs/guides/events-list.rst`, Elgg ref
`7.1`); update in place when the stable manual changes.

## Container checks

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `container_logic_check, <entity_type>` | results | triggered by `ElggEntity::canWriteToContainer()` before the `permissions_check` and `container_permissions_check` events; use it to prevent certain entity types from being contained by others (e.g. discussion replies only within discussions) or to apply status logic (e.g. disallow replies for closed discussions); return `false` to prevent containment — the default value passed to the event is `null`, so check whether the value is set to detect another handler's change; when it returns `false`, `container_permissions_check` and `permissions_check` are not triggered; `$params`: `container`, `user`, `subtype` (entity type is assumed from the event type) |
| `container_permissions_check, <entity_type>` | results | return whether the user `$params['user']` can use the entity `$params['container']` as a container for an entity of `<entity_type>` and subtype `$params['subtype']`; called *twice* when an entity is created with neither `container_guid` nor `owner_guid` matching the logged-in user — the first call passes the *owner* as `container` (see traps in `../events-list.md`); `$params`: `container`, `user`, `subtype` |

## Permission checks

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `permissions_check, <entity_type>` | results | return whether the user `$params['user']` can edit the entity `$params['entity']` |
| `permissions_check:delete, <entity_type>` | results | return whether the user `$params['user']` can delete the entity `$params['entity']`; defaults to `$entity->canEdit()` |
| `permissions_check:delete, river` | results | return whether the user `$params['user']` can delete the river item `$params['item']`; defaults to `true` for admins and `false` for other users |
| `permissions_check:download, file` | results | return whether the user `$params['user']` can download the file in `$params['entity']`; `$params`: `entity` (an `ElggFile`), `user` |
| `permissions_check, widget_layout` | results | return whether `$params['user']` can edit the widgets in the context `$params['context']` with a page owner of `$params['page_owner']` |
| `permissions_check:comment, <entity_type>` | results | return whether the user `$params['user']` can comment on the entity `$params['entity']` |
| `permissions_check:annotate:<annotation_name>, <entity_type>` | results | return whether the user `$params['user']` can create an annotation `<annotation_name>` on the entity `$params['entity']`; default `true` when logged in; called before the more general `permissions_check:annotate` event, and its return value is that event's initial value |
| `permissions_check:annotate, <entity_type>` | results | return whether the user `$params['user']` can create an annotation `$params['annotation_name']` on the entity `$params['entity']`; default `true` when logged in |

## API and gatekeeper

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `api_key, use` | results | triggered in `\Elgg\WebServices\PAM\API\APIKey`; return `false` to prevent the key from being authenticated |
| `gatekeeper, <entity_type>:<entity_subtype>` | results | filters the result of `elgg_entity_gatekeeper()` to deny or allow access to an entity the user would otherwise not have or have access to; return `false` or an `\Elgg\Exceptions\HttpException` to deny access, `true` to override the gatekeeper result; the entity arrives fetched with ignored access and including disabled entities — never use it to bypass the access system (see traps in `../events-list.md`); `$params`: `entity`, `user` (`null` implies the logged-in user) |
