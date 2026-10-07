# Elgg Developer Guide: Events List — Views

Category table for the events-list distillation: marker legend and the
behavioral traps live in `../events-list.md`. Distilled from the stable
manual on 2026-09-30 (source: `docs/guides/events-list.rst`, Elgg ref
`7.1`); update in place when the stable manual changes.

## HTMLawed

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `attributes, htmlawed` | results | change individual attributes |
| `allowed_styles, htmlawed` | results | configure allowed styles for HTMLawed |
| `config, htmlawed` | results | filter the HTMLawed `$config` array |
| `spec, htmlawed` | results | filter the HTMLawed `$spec` string (default empty) |

## Forms

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `form:prepare:fields, <form_name>` | results | prepare field values for use in the form (e.g. fill with the current values when editing a blog); sticky form values are added to the field values automatically when available |
| `form:register:fields, <entity_type>:<entity_subtype>` | results | register fields to be drawn on an entity form, prefilled with the registered entity fields; add or remove fields as needed; `$params`: `entity_type`, `entity_subtype`, `entity` (the entity being edited, or `null` when adding a new entity) |

## Page shell

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `head, page` | results | in `elgg_view_page()`, filters `$vars['head']`; return an array with `title` (page title), `metas` (elements formatted as `<meta>` head tags), and `links` (elements formatted as `<link>` head tags); each meta and link element is a set of key/value pairs formatted into HTML tag attributes (e.g. a viewport meta, or an RSS link with `rel`, `type`, `title`, `href` keys) |
| `layout, page` | results | in `elgg_view_layout()`, filters the layout name; `$params`: `identifier` (ID of the page being rendered), `segments` (URL segments of the page), plus the other `$vars` received by `elgg_view_layout()` |
| `shell, page` | results | in `elgg_view_page()`, filters the page shell name |

## Views

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `table_columns:call, <name>` | results | called when `elgg()->table_columns->$name()` is invoked, to let plugins override or provide an implementation; `$params`: `arguments` (the method arguments); return an `Elgg\Views\TableColumn` instance to specify the column directly |
| `view, <view_name>` | results | filters the returned content of the view |
| `view_vars, <view_name>` | results | filters the `$vars` array passed to the view |
