# Elgg Developer Guide: Events List — Entities

Category table for the events-list distillation: marker legend and the
behavioral traps live in `../events-list.md`. Distilled from the stable
manual on 2026-09-30 (source: `docs/guides/events-list.rst`, Elgg ref
`7.1`); update in place when the stable manual changes.

## Entity events

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `comments, <entity_type>` | results | triggered in `elgg_view_comments()`; returning content overrides the `page/elements/comments` view |
| `comments:count, <entity_type>` | results | return the number of comments on `$params['entity']` |
| `create, <entity type>` | | after creation of user, group, object, and site entities; fires just before `create:after`, mostly for BC — prefer `create:after` |
| `create:after, <entity type>` | | after creation of user, group, object, and site entities; preferred over `create, <entity type>` |
| `create:before, <entity type>` | | before creation; return `false` to prevent creating the entity |
| `delete, <entity type>` | seq | when an entity is permanently removed from the database; see the manual's restore guide |
| `disable, <entity type>` | | before the entity is disabled; return `false` to prevent disabling |
| `disable:after, <entity type>` | | after the entity is disabled |
| `enable, <entity type>` | | return `false` to prevent enabling |
| `enable:after, <entity type>` | | after the entity is enabled |
| `likes:count, <entity_type>` | results | return the number of likes for `$params['entity']` |
| `trash, <entity type>` | seq | when an entity is marked as deleted in the database; see the manual's restore guide |
| `update, <entity type>` | | before an update of user, group, object, and site entities; return `false` to prevent the update; `getOriginalAttributes()` identifies which attributes changed since the last save |
| `update:after, <entity type>` | | after an update of user, group, object, and site entities; `getOriginalAttributes()` identifies which attributes changed since the last save |

## Relationship events

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `create, relationship` | seq | during the creation of a relationship |
| `delete, relationship` | seq | during the deletion of a relationship |
| `join, group` | | after the user `$params['user']` has joined the group `$params['group']` |
| `leave, group` | | before the user `$params['user']` has left the group `$params['group']` |

## Metadata events

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `create, metadata` | | after the metadata has been created; return `false` to delete the just-created metadata |
| `delete, metadata` | | before metadata is deleted; return `false` to prevent deletion |
| `update, metadata` | | after the metadata has been updated; return `false` to *delete the metadata* (see traps in `../events-list.md`) |

## Annotation events

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `annotate, <entity type>` | | before the annotation has been created; return `false` to prevent annotating the entity |
| `create, annotation` | | after the annotation has been created; return `false` to delete the annotation |
| `delete, annotation` | | before the annotation is deleted; return `false` to prevent deletion |
| `update, annotation` | | after the annotation has been updated; return `false` to *delete the annotation* (see traps in `../events-list.md`) |

## River events

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `create:after, river` | | after a river item is created |
| `create:before, river` | | before the river item is saved to the database; return `false` to prevent creation |
| `delete:after, river` | | after a river item was deleted |
| `delete:before, river` | | before the river item is deleted; return `false` to cancel the deletion |
