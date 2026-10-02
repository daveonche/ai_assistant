# Elgg Developer Guide: Events List — Search

Category table for the events-list distillation: marker legend and the
behavioral traps live in `../events-list.md`. Distilled from the stable
manual on 2026-09-30 (source: `docs/guides/events-list.rst`, Elgg ref
`7.1`); update in place when the stable manual changes.

## Search plugin configuration

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `search:config, search_types` | results | implemented in the **search** plugin; filters the array of custom search types, letting plugins add custom types (e.g. tag or location search); adding a type extends the search plugin UI with appropriate links and lists |
| `search:config, type_subtype_pairs` | results | implemented in the **search** plugin; filters entity type/subtype pairs before entity search is performed; remove types/subtypes from results, group multiple subtypes together, or reorder search sections |

## Query preparation (triggered by `elgg_search()`)

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `search:fields, <entity_type>` | results | filters search fields before search clauses are prepared; `$return` maps each entity property type to the field names to match against the query (e.g. `['attributes' => [], 'metadata' => ['title', 'description'], 'annotations' => ['revision']]`); `$params`: the search params passed to and filtered by `elgg_search()` |
| `search:fields, <entity_type>:<entity_subtype>` | results | subtype-granular variant of `search:fields, <entity_type>` |
| `search:fields, <search_type>` | results | search-type variant of `search:fields, <entity_type>` |
| `search:options, <entity_type>` | results | prepares the search clauses (options) to be passed to `elgg_get_entities()` |
| `search:options, <entity_type>:<entity_subtype>` | results | subtype-granular variant of `search:options, <entity_type>` |
| `search:options, <search_type>` | results | search-type variant of `search:options, <entity_type>` |
| `search:params, <search_type>` | results | filters search parameters (query, sorting, search fields etc) before search clauses are prepared for a given search type; Elgg core only provides support for the `entities` search type |

## Results and formatting

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `search:format, entity` | results | implemented in the **search** plugin; populate the entity's volatile data before it is passed to the search view; used for highlighting search hits, extracting relevant substrings in long text fields, etc. |
| `search:results, <search_type>` | results | receives normalized options suitable for an `elgg_get_entities()` call and must return an array of entities matching the options; designed for plugins integrating third-party indexing services such as Solr and Elasticsearch |
