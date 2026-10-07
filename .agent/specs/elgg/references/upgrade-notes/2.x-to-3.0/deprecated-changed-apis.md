# Deprecated and Changed APIs: 2.x to 3.0

Exhaustive enumeration of the API deprecations, hook and event removals,
and signature and behaviour changes in Elgg 3.0 — 91 entries: 25 deprecated
APIs, 13 removed hooks and events, 10 methods that now accept only an
`$options` array, 8 plugin functions that now require an explicit
`$plugin_id`, and 35 miscellaneous API changes. Distilled from the official
upgrade notes at
<https://learn.elgg.org/en/stable/appendix/upgrade-notes/2.x-to-3.0.html>.
Companion detail file for the canonical note `2.x-to-3.0.md`, which carries
the surrounding narrative and breaking-change guidance.

## Deprecated APIs

- `ban_user`: Use `ElggUser->ban()`
- `create_metadata`: Use an `ElggEntity` setter or
  `ElggEntity->setMetadata()`
- `update_metadata`: Use `ElggMetadata->save()`
- `get_metadata_url`
- `create_annotation`: Use `ElggEntity->annotate()`
- `update_metadata`: Use `ElggAnnotation->save()`
- `elgg_get_user_validation_status`: Use `ElggUser->isValidated()`
- `make_user_admin`: Use `ElggUser->makeAdmin()`
- `remove_user_admin`: Use `ElggUser->removeAdmin()`
- `unban_user`: Use `ElggUser->unban()`
- `elgg_get_entities_from_attributes`: Use `elgg_get_entities()`
- `elgg_get_entities_from_metadata`: Use `elgg_get_entities()`
- `elgg_get_entities_from_relationship`: Use `elgg_get_entities()`
- `elgg_get_entities_from_private_settings`: Use `elgg_get_entities()`
- `elgg_get_entities_from_access_id`: Use `elgg_get_entities()`
- `elgg_list_entities_from_metadata`: Use `elgg_list_entities()`
- `elgg_list_entities_from_relationship`: Use `elgg_list_entities()`
- `elgg_list_entities_from_private_settings`: Use `elgg_list_entities()`
- `elgg_list_entities_from_access_id`: Use `elgg_list_entities()`
- `elgg_list_registered_entities`: Use `elgg_list_entities()`
- `elgg_batch_delete_callback`
- `\Elgg\Project\Paths::sanitize`: Use `\Elgg\Project\Paths::sanitize()`
- `elgg_group_gatekeeper`: Use `elgg_entity_gatekeeper()`
- `get_entity_dates`: Use `elgg_get_entity_dates()`
- `messages_set_url`: Use `ElggEntity::getURL()`

## Removed events

- `login, user`: use `login:before` or `login:after`; the user is not
  logged in during `login:before`
- `delete, annotations`: use `delete, annotation`
- `pagesetup, system`: use the menu or page shell hooks instead
- `upgrade, upgrade`: use `upgrade, system`

## Removed hooks

- `index, system`: override the `resources/index` view
- `object:notifications, <type>`: use the `send:before, notifications`
  hook
- `output:before, layout`: use `view_vars, page/layout/<layout_name>`
- `output:after, layout`: use `view, page/layout/<layout_name>`
- `email, system`: use the more granular `<hook>, system:email` hooks
- `email:message, system`: use the `zend:message, system:email` hook
- `members:list, <page>`: use your own page handler or route hook
- `members:config, <page>`: use `register, menu:filter:members`
- `profile_buttons, group`: use `register, menu:title`

## APIs that now accept only an `$options` array

- `ElggEntity::getAnnotations`
- `ElggEntity::getEntitiesFromRelationship`
- `ElggGroup::getMembers`
- `ElggUser::getGroups`
- `ElggUser::getFriends` (as part of `Friendable`)
- `ElggUser::getFriendsOf` (as part of `Friendable`)
- `ElggUser::getFriendsObjects` (as part of `Friendable`)
- `ElggUser::getObjects` (as part of `Friendable`)
- `find_active_users`
- `elgg_get_admin_notices`

## Plugin functions that now require an explicit `$plugin_id`

- `elgg_get_all_plugin_user_settings`
- `elgg_set_plugin_user_setting`
- `elgg_unset_plugin_user_setting`
- `elgg_get_plugin_user_setting`
- `elgg_set_plugin_setting`
- `elgg_get_plugin_setting`
- `elgg_unset_plugin_setting`
- `elgg_unset_all_plugin_settings`

## Miscellaneous API changes

### Entities, users and groups

- `ElggBatch`: you may only access public properties
- `ElggEntity`: the `tables_split` and `tables_loaded` properties were
  removed
- `ElggEntity`: empty URLs are no longer normalized — entities without
  URLs no longer result in the site URL
- `ElggGroup::removeObjectFromGroup()` requires an `ElggObject` (no longer
  accepts a GUID)
- `ElggUser::$salt` no longer exists as an attribute, nor is it used for
  authentication
- `ElggUser::$password` no longer exists as an attribute, nor is it used
  for authentication
- Group entities no longer have the magic `username` attribute
- `ElggEntity::saveIconFromUploadedFile` only saves the `master` size; the
  other sizes are created when requested by `ElggEntity::getIcon()` based
  on the `master` size
- `ElggEntity::saveIconFromLocalFile` only saves the `master` size; the
  other sizes are created when requested by `ElggEntity::getIcon()` based
  on the `master` size
- `ElggEntity::saveIconFromElggFile` only saves the `master` size; the
  other sizes are created when requested by `ElggEntity::getIcon()` based
  on the `master` size

### Function signatures and options

- `elgg_get_widget_types()` no longer supports `$exact` as the second
  argument
- `elgg_instanceof()` no longer supports the fourth `class` argument
- `elgg_view()`: the third and fourth (unused) arguments were removed; if
  you use the `$viewtype` argument, you must update your usage
- `elgg_view_icon()` no longer supports `true` as the second argument
- `elgg_list_entities()` no longer supports the option `view_type_toggle`
- `elgg_list_registered_entities()` no longer supports the option
  `view_type_toggle`
- `elgg_log()` no longer accepts the level `"DEBUG"`
- `elgg_dump()` no longer accepts a `$to_screen` argument
- `Application::getDb()` no longer returns an instance of
  `Elgg\Database` but an `Elgg\Application\Database`

### Gatekeepers and page handling

- `elgg_gatekeeper()` and `elgg_admin_gatekeeper()` no longer report
  `login` or `admin` as the forward reason, but `403`
- Page handling no longer detects `group:<guid>` in the URL

### Configuration

- `$CONFIG` is no longer available as a local variable inside plugin
  `start.php` files
- `elgg_get_config('siteemail')` is no longer available; use
  `elgg_get_site_entity()->email`
- `set_config()`, `unset_config()`, and `get_config()` are deprecated and
  replaced by `elgg_set_config()`, `elgg_remove_config()`, and
  `elgg_get_config()`
- The config values `path`, `wwwroot`, and `dataroot` are not read from the
  database; the `settings.php` values are always used
- Config functions like `elgg_get_config()` no longer trim keys
- If you override the view `navigation/menu/user_hover/placeholder`, change
  the config key `lazy_hover:menus` to `elgg_lazy_hover_menus`
- The config value `entity_types` is no longer present or used

### URLs, cron and other changes

- The URL endpoints `js/` and `css/` are no longer supported; use
  `elgg_get_simplecache_url()`
- The CRON interval `reboot` is removed
- Uploaded images are autorotated based on their orientation metadata
- The view `object/widget/edit/num_display` now uses an `input/number`
  field instead of `input/select`; widget edit views may need updating
- Annotation names are no longer trimmed during save
- The generic comment save action no longer sends the notification
  directly; this is offloaded to the notification system
- The script `engine/start.php` is removed
