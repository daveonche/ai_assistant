# Plugin Upgrade Notes: 3.x to 4.0 — Type Hints

Exhaustive enumeration of the type-hint changes in the 3.x to 4.0
transition, distilled from
<https://learn.elgg.org/en/stable/appendix/upgrade-notes/3.x-to-4.0.html>.
Load this file on demand from the main `3.x-to-4.0.md` notes when auditing
`TypeError` failures after an upgrade.

The following functions now have their arguments type-hinted; this can cause
`TypeError` errors. Some class functions also have their return value
type-hinted, and you should update your function definitions accordingly.
Functions that lost default parameter values or parameters entirely are
listed in the last section.

## Class function parameters

- `ElggEntity::setLatLong()` now requires a `float` for `$lat` and `$long`
- `ElggUser::setNotificationSetting()` now requires a `string` for `$method`
  and a `bool` for `$enabled`
- `Elgg\Database\Seeds\Seed::__construct()` now requires an `int` for
  `$limit`
- `Elgg\Http\ErrorResponse::__construct()` now requires an `int` for
  `$status_code`
- `Elgg\Http\OkResponse::__construct()` now requires an `int` for
  `$status_code`
- `Elgg\Http\RedirectResponse::__construct()` now requires an `int` for
  `$status_code`
- `Elgg\I18n\Translator::getInstalledTranslations()` now requires a `bool`
  for `$calculate_completeness`
- `SiteNotification::setActor()` now requires an `ElggEntity` for `$entity`
- `SiteNotification::setURL()` now requires a `string` for `$url`
- `SiteNotification::setRead()` now requires a `bool` for `$read`

## Class function return types

- `Elgg\Upgrade\Batch::getVersion()` now requires an `int` return value
- `Elgg\Upgrade\Batch::shouldBeSkipped()` now requires a `bool` return value
- `Elgg\Upgrade\Batch::needsIncrementOffset()` now requires a `bool` return
  value
- `Elgg\Upgrade\Batch::countItems()` now requires an `int` return value
- `Elgg\Upgrade\Batch::run()` now requires an `Elgg\Upgrade\Result` return
  value

## Lib function parameters

### Access collections

- `add_user_to_access_collection()` now requires an `int` for `$user_guid`
  and `$collection_id`
- `can_edit_access_collection()` now requires an `int` for `$collection_id`
  and `$user_guid`
- `create_access_collection()` now requires a `string` for `$name` and an
  `int` for `$owner_guid`
- `delete_access_collection()` now requires an `int` for `$collection_id`
- `elgg_get_access_collections()` now requires an `array` for `$options`
- `get_members_of_access_collection()` now requires an `int` for
  `$collection_id` and a `bool` for `$guids_only`
- `remove_user_from_access_collection()` now requires an `int` for
  `$user_guid` and `$collection_id`

### Access checks

- `get_access_array()` now requires an `int` for `$user_guid`
- `get_readable_access_level()` now requires an `int` for
  `$entity_access_id`
- `get_write_access_array()` now requires an `int` for `$user_guid` and a
  `bool` for `$flush`
- `has_access_to_entity()` now requires an `ElggEntity` for `$entity` and an
  `ElggUser` for `$user`

### Actions

- `elgg_action_exists()` now requires a `string` for `$action`
- `elgg_register_action()` now requires a `string` for `$action` and
  `$access`
- `elgg_unregister_action()` now requires a `string` for `$action`

### Admin notices

- `elgg_add_admin_notice()` now requires a `string` for `$id` and
  `$message`
- `elgg_admin_notice_exists()` now requires a `string` for `$id`
- `elgg_delete_admin_notice()` now requires a `string` for `$id`

### Annotations

- `elgg_annotation_exists()` now requires an `int` for `$entity_guid`, a
  `string` for `$name` and an `int` for `$owner_guid`
- `elgg_delete_annotation_by_id()` now requires an `int` for `$id`
- `elgg_get_annotation_from_id()` now requires an `int` for `$id`
- `elgg_list_annotations()` now requires an `array` for `$options`

### External files

- `elgg_register_external_file()` now requires all arguments to be of the
  type `string`
- `elgg_unregister_external_file()` now requires all arguments to be of the
  type `string`
- `elgg_load_external_file()` now requires all arguments to be of the type
  `string`
- `elgg_get_loaded_external_files()` now requires all arguments to be of the
  type `string`

### Email

- `elgg_send_email()` now requires an `\Elgg\Email` for `$email`

### Plugins

- `elgg_get_plugin_from_id()` now requires a `string` for `$plugin_id`
- `elgg_get_plugin_setting()` now requires a `string` for `$name` and
  `$plugin_id`
- `elgg_get_plugin_user_setting()` now requires a `string` for `$name` and
  `$plugin_id` and an `int` for `$user_guid`
- `elgg_get_plugins()` now requires a `string` for `$status`
- `elgg_plugin_exists()` now requires a `string` for `$plugin_id`
- `elgg_set_plugin_user_setting()` now requires a `string` for `$name` and
  `$plugin_id` and an `int` for `$user_guid`

### Responses

- `elgg_error_response()` now requires an `int` for `$status_code`
- `elgg_ok_response()` now requires an `int` for `$status_code`
- `elgg_redirect_response()` now requires an `int` for `$status_code`

### Miscellaneous

- `elgg_deprecated_notice()` now requires a `string` for `$msg` and
  `$dep_version`
- `elgg_get_river_item_from_id()` now requires an `int` for `$id`
- `elgg_get_subscriptions_for_container()` now requires an `int` for
  `$container_guid`
- `get_entity_statistics()` now requires an `int` for `$owner_guid`
- `messageboard_add()` now requires an `ElggUser`, `ElggUser`, `string` and
  an `int`
- `system_log_get_log()` now requires an `array` for `$options`

## Lost defaults and removed parameters

### Class functions

- `Elgg\Http\ResponseBuilder::setStatusCode()` no longer has a default value
- `ElggEntity::canWriteToContainer()` no longer has a default value for
  `$type` and `$subtype`, but these are required

### Lib functions

- `elgg_get_page_owner_guid()` no longer accepts `$guid` as a parameter
- `get_access_array()` no longer accepts `$flush` as a parameter
- `elgg_register_external_file()` no longer accepts `$priority` as a
  parameter
