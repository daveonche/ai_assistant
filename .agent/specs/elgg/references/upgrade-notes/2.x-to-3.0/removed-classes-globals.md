# Removed Classes, Interfaces and Globals: 2.x to 3.0

Exhaustive enumeration of the classes, interfaces, global variables,
inheritance changes, and constructor restrictions from the Elgg 3.0
upgrade — 35 entries across four groups. Distilled from the official
upgrade notes at
<https://learn.elgg.org/en/stable/appendix/upgrade-notes/2.x-to-3.0.html>.
Companion detail file for the canonical note `2.x-to-3.0.md`, which carries
the surrounding narrative and breaking-change guidance.

## Removed classes and interfaces

- `FilePluginFile`: replace with `ElggFile` (or load with `get_entity()`)
- `Elgg_Notifications_Notification`
- `Elgg\Database\EntityTable\UserFetchResultException.php`
- `Elgg\Database\MetastringsTable`
- `Elgg\Database\SubtypeTable`
- `Exportable` and its methods `export` and `getExportableValues`: Use
  `toObject`
- `ExportException`
- `Importable` and its method `import`
- `ImportException`
- `ODD` and all classes beginning with `ODD*`
- `XmlElement`
- `Elgg_Notifications_Event`: Use `\Elgg\Notifications\Event`
- `Elgg\Mail\Address`: use `Elgg\Email\Address`
- `ElggDiscussionReply`: use `ElggComment` — see the "Discussion replies
  moved to comments" section of the canonical note

## Removed global variables

- `$CURRENT_SYSTEM_VIEWTYPE`
- `$DEFAULT_FILE_STORE`
- `$ENTITY_CACHE`
- `$SESSION`: Use the API provided by `elgg_get_session()`
- `$CONFIG->site_id`: Use `1`
- `$CONFIG->search_info`
- `$CONFIG->input`: Use `set_input` and `get_input`

## Inheritance changes

- `ElggData` (and hence most Elgg domain objects) no longer implements
  `Exportable`
- `ElggEntity` no longer implements `Importable`
- `ElggGroup` no longer implements `Friendable`
- `ElggRelationship` no longer implements `Importable`
- `ElggSession` no longer implements `ArrayAccess`
- `Elgg\Application\Database` no longer extends `Elgg\Database`

## Class constructors now accept only a `stdClass` object or `null`

- `ElggAnnotation`: No longer accepts an annotation ID
- `ElggGroup`: No longer accepts a GUID
- `ElggMetadata`: No longer accepts a metadata ID
- `ElggObject`: No longer accepts a GUID
- `ElggRelationship`: No longer accepts a relationship ID or `null`
- `ElggSite`: No longer accepts a GUID or URL
- `ElggUser`: No longer accepts a GUID or username
- `ElggPlugin`: No longer accepts a GUID or path. Use `ElggPlugin::fromId`
  to construct a plugin from its path
