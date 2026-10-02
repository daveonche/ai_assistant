# Removed Functions and Methods: 2.x to 3.0

Exhaustive enumeration of the functions, methods, and classes removed in
Elgg 3.0 — 156 entries, grouped thematically. In addition, every function
in `engine/lib/deprecated-1.9.php` and `engine/lib/deprecated-1.10.php` was
removed (see the first section below). Distilled from the official upgrade
notes at
<https://learn.elgg.org/en/stable/appendix/upgrade-notes/2.x-to-3.0.html>.
Companion detail file for the canonical note `2.x-to-3.0.md`, which carries
the surrounding narrative and breaking-change guidance.

## Deprecated function files emptied

All the functions in `engine/lib/deprecated-1.9.php` and
`engine/lib/deprecated-1.10.php` were removed. The 2.0 versions of these
files list them, and each `@deprecated` declaration includes instructions
on what to use instead:

- <https://github.com/Elgg/Elgg/blob/2.0/engine/lib/deprecated-1.9.php>
- <https://github.com/Elgg/Elgg/blob/2.0/engine/lib/deprecated-1.10.php>

## Library loading

- `elgg_register_library`: require your library files so they are available
  globally to other plugins
- `elgg_load_library`

## Metadata, metastrings and extenders

- `create_metadata_from_array`
- `metadata_array_to_values`
- `detect_extender_valuetype`
- `elgg_disable_metadata`
- `elgg_enable_metadata`
- `elgg_get_metastring_id`
- `elgg_get_metastring_map`
- `garbagecollector_orphaned_metastrings`

## Configuration and datalists

- `datalist_get`
- `datalist_set`

## Class and viewtype registration

- `elgg_get_class_loader`
- `elgg_register_class`
- `elgg_register_classes`
- `elgg_register_viewtype`
- `elgg_is_registered_viewtype`

## Files and filestores

- `file_delete`: Use `ElggFile->deleteIcon()`
- `file_get_type_cloud`
- `file_type_cloud_get_url`
- `get_default_filestore`
- `set_default_filestore`
- `ElggFile::setFilestore`: ElggFile objects can no longer use custom
  filestores
- `ElggFile::size`: Use `getSize`
- `ElggDiskFilestore::makeFileMatrix`: Use `Elgg\EntityDirLocator`

## Entity row helpers

- `get_site_entity_as_row`
- `get_group_entity_as_row`
- `get_object_entity_as_row`
- `get_user_entity_as_row`

## Groups

- `groups_access_collection_override`
- `groups_get_group_tool_options`: Use `elgg()->group_tools->all()`
- `groups_join_group`: Use `ElggGroup::join`
- `groups_prepare_profile_buttons`: Use `register, menu:title` hook
- `groups_register_profile_buttons`: Use `register, menu:title` hook
- `groups_setup_sidebar_menus`
- `groups_set_icon_url`

## Access and permissions

- `can_write_to_container`: Use `ElggEntity->canWriteToContainer()`
- `elgg_override_permissions`: No longer used as handler for the
  `permissions_check` and `container_permissions_check` hooks
- `elgg_check_access_overrides`
- `elgg_view_access_collections()`

## Miscellaneous core functions

- `get_missing_language_keys`
- `generate_user_password`: Use `ElggUser::setPassword`
- `row_to_elggrelationship`
- `run_function_once`: Use `Elgg\Upgrade\Batch` interface
- `system_messages`
- `elgg_format_url`: Use `elgg_format_element()` or the `output/text` view
  for HTML escaping
- `get_site_by_url`

## River

- `update_river_access_by_object`
- `ElggRiverItem::getPostedTime`: Use `getTimePosted`

## Session

- `ElggSession`: all deprecated methods were removed
- `ElggSession::get_ignore_access`: Use `getIgnoreAccess`
- `ElggSession::set_ignore_access`: Use `setIgnoreAccess`

## Menu classes

- `ElggMenuBuilder::compareByWeight`: Use `compareByPriority`
- `ElggMenuItem::getWeight`: Use `getPriority`
- `ElggMenuItem::getContent`: Use `elgg_view_menu_item()`
- `ElggMenuItem::setWeight`: Use `setPriority`

## ElggEntity methods

- `ElggEntity::addToSite`
- `ElggEntity::disableMetadata`
- `ElggEntity::enableMetadata`
- `ElggEntity::getSites`
- `ElggEntity::removeFromSite`
- `ElggEntity::isFullyLoaded`
- `ElggEntity::clearAllFiles`
- `ElggEntity::setURL`: See `getURL` for details on the plugin hook

## ElggSite methods

- `ElggSite::addEntity`
- `ElggSite::addObject`
- `ElggSite::addUser`
- `ElggSite::getEntities`: Use `elgg_get_entities()`
- `ElggSite::getExportableValues`: Use `toObject`
- `ElggSite::getMembers`: Use `elgg_get_entities()`
- `ElggSite::getObjects`: Use `elgg_get_entities()`
- `ElggSite::listMembers`: Use `elgg_list_entities()`
- `ElggSite::removeEntity`
- `ElggSite::removeObject`
- `ElggSite::removeUser`
- `ElggSite::isPublicPage`: Logic moved to the router and should not be
  accessed directly
- `ElggSite::checkWalledGarden`: Logic moved to the router and should not be
  accessed directly

## ElggPlugin methods

- `ElggPlugin::getFriendlyName`: Use `ElggPlugin::getDisplayName()`
- `ElggPlugin::setID`
- `ElggPlugin::unsetAllUsersSettings`

## ElggData methods

- `ElggData::get`: Usually can be replaced by property read
- `ElggData::getClassName`: Use `get_class()`
- `ElggData::set`: Usually can be replaced by property write

## Other class methods

- `AttributeLoader`: became obsolete and was removed
- `Application::loadSettings`
- `ElggUser::countObjects`: Use `elgg_get_entities()`
- `Logger::getClassName`: Use `get_class()`
- `Elgg\Application\Database::getTablePrefix`: Read the `prefix` property

## Plugin-specific and UI functions

- `activity_profile_menu`
- `developers_setup_menu`
- `messages_notification_msg`
- `notifications_plugin_pagesetup`
- `profile_pagesetup`
- `pages_can_delete_page`: Use `$entity->canDelete()`
- `pages_search_pages`
- `pages_is_page`: use `$entity instanceof ElggPage`
- `uservalidationbyemail_generate_code`

## Search

- `search_get_where_sql`
- `search_get_ft_min_max`
- `search_get_order_by_sql`
- `search_consolidate_substrings`
- `search_remove_ignored_words`
- `search_get_highlighted_relevant_substrings`
- `search_highlight_words`
- `search_get_search_view`
- `search_custom_types_tags_hook`
- `search_tags_hook`
- `search_users_hook`
- `search_groups_hook`
- `search_objects_hook`

## Members

- `members_list_popular`
- `members_list_newest`
- `members_list_online`
- `members_list_alpha`
- `members_nav_popular`
- `members_nav_newest`
- `members_nav_online`
- `members_nav_alpha`

## Discussion

All removed as part of the discussion-replies migration to comments; see
the "Discussion replies moved to comments" section of the canonical note.

- `discussion_comment_override`
- `discussion_can_edit_reply`
- `discussion_reply_menu_setup`
- `discussion_reply_container_logic_override`
- `discussion_reply_container_permissions_override`
- `discussion_update_reply_access_ids`
- `discussion_search_discussion`
- `discussion_add_to_river_menu`
- `discussion_prepare_reply_notification`
- `discussion_redirect_to_reply`
- `discussion_ecml_views_hook`

## Entity subtype functions

All API around the entity subtypes table was removed:

- `add_subtype`: Use `elgg_set_entity_class` at runtime
- `update_subtype`: Use `elgg_set_entity_class` at runtime
- `remove_subtype`
- `get_subtype_id`
- `get_subtype_from_id`
- `get_subtype_class`: Use `elgg_get_entity_class`
- `get_subtype_class_from_id`

## Cache consolidation

All caches were consolidated into a single API layer; the following
functions, classes, and interfaces were removed:

- `is_memcache_available`
- `_elgg_get_memcache`
- `_elgg_invalidate_memcache_for_entity`
- `ElggMemcache`
- `ElggFileCache`
- `ElggStaticVariableCache`
- `ElggSharedMemoryCache`
- `Elgg\Cache\Pool` interface and all extending classes

## System log functions

All moved to the `system_log` plugin, most under new names:

- `system_log_default_logger`: moved to the `system_log` plugin
- `system_log_listener`: moved to the `system_log` plugin
- `system_log`: moved to the `system_log` plugin
- `get_system_log`: renamed to `system_log_get_log`
- `get_log_entry`: renamed to `system_log_get_log_entry`
- `get_object_from_log_entry`: renamed to
  `system_log_get_object_from_log_entry`
- `archive_log`: renamed to `system_log_archive_log`
- `logbrowser_user_hover_menu`: renamed to `system_log_user_hover_menu`
- `logrotate_archive_cron`: renamed to `system_log_archive_cron`
- `logrotate_delete_cron`: renamed to `system_log_delete_cron`
- `logrotate_get_seconds_in_period`: renamed to
  `system_log_get_seconds_in_period`
- `log_browser_delete_log`: renamed to `system_log_browser_delete_log`
