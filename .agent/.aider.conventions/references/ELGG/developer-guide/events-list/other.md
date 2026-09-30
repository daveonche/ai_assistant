# Elgg Developer Guide: Events List — Other

Category table for the events-list distillation: marker legend and the
behavioral traps live in `../events-list.md`. Distilled from the stable
manual on 2026-09-30 (source: `docs/guides/events-list.rst`, Elgg ref
`7.1`); update in place when the stable manual changes.

## Config and defaults

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `config, comments_per_page` | results | filters the number of comments displayed per page (default 25); `$params['entity']` holds the containing entity or `null`; read the value with `elgg_comments_per_page()` |
| `config, comments_latest_first` | results | filters the order of comments (default `true`, latest first); `$params['entity']` holds the containing entity or `null` |
| `default, access` | results | in `elgg_get_default_access()`, filters the return value to alter the default in the `input/access` view; core plugins receive `input_params` with keys `entity` (`ElggEntity\|false`), `entity_type`, `entity_subtype`, `container_guid` — an empty entity generally means a create form |

## Icons

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `classes, icon` | results | filters the CSS classes applied to icon glyphs; Elgg uses FontAwesome by default — switch to a different font family and remap icon classes |
| `entity:icon:sizes, <entity_type>` | results | triggered by `elgg_get_icon_sizes()`; sets entity type/subtype specific icon sizes; `entity_subtype` is passed in `$params` |
| `entity:<icon_type>:sizes, <entity_type>` | results | filters sizes for custom icon types; return an associative array keyed by size name (e.g. `large`) where each value has keys `w`, `h`, `square`, `upscale`, `crop` (default `true`); an empty configuration array saves the image as an exact copy of the source without resizing or cropping |
| `entity:icon:url, <entity_type>` | results | triggered when an entity icon URL is requested; return the URL for the icon of size `$params['size']` for `$params['entity']`; `$params`: `entity`, `viewtype` (e.g. `default` or `json`), `size` |
| `entity:<icon_type>:url, <entity_type>` | results | filters URLs for custom icon types, see `entity:icon:url, <entity_type>` |
| `entity:icon:file, <entity_type>` | results | triggered by `ElggEntity::getIcon()`; provide an alternative `ElggIcon` object pointing to a custom icon location on the filestore; the handler must return an `ElggIcon` instance or an exception is thrown |
| `entity:<icon_type>:file, <entity_type>` | results | filters the icon file object for custom icon types, see `entity:icon:file, <entity_type>` |
| `entity:<icon_type>:prepare, <entity_type>` | results | triggered by `ElggEntity::saveIcon*()`; prepare the uploaded/linked image before it is resized/cropped (e.g. rotate it, or extract an image frame from a video upload); return an `ElggFile` whose `simpletype` resolves to `image`; the `$return` passed to the event is an `ElggFile` pointing to a temporary copy of the input; `$params`: `entity`, `file` (original input file) |
| `entity:<icon_type>:save, <entity_type>` | results | triggered by `ElggEntity::saveIcon*()`; apply custom image manipulation logic to resizing/cropping icons; return `true` to prevent the core APIs from resizing/cropping the icons; `$params`: `entity`, `file` (source image), `x1`, `y1`, `x2`, `y2` (cropping coordinates) |
| `entity:<icon_type>:saved, <entity_type>` | results | triggered by `ElggEntity::saveIcon*()` once icons have been created; create river items, update cropping coordinates for custom icon types, etc.; access the created icons via `ElggEntity::getIcon()`; `$params`: `entity`, `x1`, `y1`, `x2`, `y2` |
| `entity:<icon_type>:delete, <entity_type>` | results | triggered by `ElggEntity::deleteIcon()` before the icons are deleted; clean-up operations; return `false` to prevent deletion; `$params`: `entity` |

## Entity, extender, and relationship URLs

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `entity:url, <entity_type>:<entity_subtype>` | results | return the URL for `$params['entity']`; generally better to override `ElggEntity::getUrl()` — use the event when subclassing is not possible (e.g. extending a bundled plugin without overriding many views) |
| `entity:url, <entity_type>` | results | less granular variant of `entity:url, <entity_type>:<entity_subtype>` with the same guidance |
| `extender:url, <annotation\|metadata>` | results | return the URL for the annotation or metadata `$params['extender']` |
| `relationship:url, <relationship_name>` | results | filter the URL for the relationship object `$params['relationship']` |

## Forms and widgets

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `fields, <entity_type>:<entity_subtype>` | results | return an array of fields usable for `elgg_view_field()`; each field must provide `name` and `#type` |
| `get_list, default_widgets` | results | filters the list of default widgets added for newly registered users; an array of arrays with keys `name`, `widget_columns`, `widget_context`, `event_name`, `event_type`, `entity_type`, `entity_subtype` |
| `handlers, widgets` | results | triggered when a list of available widgets is needed; conditionally add or remove widgets, or modify attributes of existing widgets such as `context` or `multiple` |

## Maintenance, settings, and walled garden

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `maintenance:allow, url` | results | return whether the URL `$params['current_url']` and path `$params['current_path']` are allowed during maintenance mode |
| `plugin_setting, <entity type>` | results | change the value of the setting being saved; `$params`: `entity` (the `ElggEntity` the setting is saved on), `plugin_id`, `name`, `value` (original value); return a scalar so it can be saved to the database — an error is logged otherwise |
| `setting, plugin` | results | filter plugin settings; `$params`: `plugin` (an `ElggPlugin`), `plugin_id`, `name`, `value` |
| `public_pages, walled_garden` | results | filters the list of URL path regexes visible to logged-out users in walled garden mode; return an array of regex strings; system public routes arrive as the default value — extend the list, never replace it wholesale (see traps in `../events-list.md`); `$params`: `url` |
| `robots.txt, site` | results | filter the robots.txt values for `$params['site']` |

## Data export

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `to:object, <entity_type\|metadata\|annotation\|relationship\|river_item>` | | converts `$params['entity']` to a `StdClass` object; used mostly for exporting entity properties to portable data formats like JSON and XML |

## Bundled plugins

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `names, externalpages` | results | returns the set of allowed names for external pages (Site Pages plugin) |
| `tool_options, group` | results | filters the tools available within a specific group; `$return` is a `\Elgg\Collections\Collection<\Elgg\Groups\Tool>`; `$params`: `entity` (a `\ElggGroup`) |
| `register, api_methods` | results | triggered when the `ApiRegistrationService` is constructed; add/remove/edit web service configurations |
| `rest, init` | results | triggered by the web services REST handler; set up custom authentication handlers, then return `true` to prevent the default handlers from being registered |
| `rest:output, <method_name>` | results | filter the result (and subsequently the output) of the API method |
