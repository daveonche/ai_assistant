# Plugin Upgrade Notes: 3.x to 4.0 — Removed APIs

Exhaustive enumeration of the functions, views, hooks, events, actions, and
web services APIs removed in the 3.x to 4.0 transition, distilled from
<https://learn.elgg.org/en/stable/appendix/upgrade-notes/3.x-to-4.0.html>.
Load this file on demand from the main `3.x-to-4.0.md` notes when auditing
removed API calls after an upgrade.

## Removed class functions

- `Elgg\Config::getEntityTypes()` — use the `Elgg\Config::ENTITY_TYPES`
  constant
- `ElggFile::setDescription()` — use `$file->description = $new_description`
- `ElggGroup::addObjectToGroup()`
- `ElggGroup::removeObjectFromGroup()`
- `ElggPlugin::getAllUserSettings()`
- `ElggPlugin::getDependencyReport()`
- `ElggPlugin::getError()`
- `ElggPlugin::unsetAllUserSettings()`
- `ElggPlugin::unsetAllUserAndPluginSettings()` — use
  `ElggPlugin::unsetAllEntityAndPluginSettings()`
- `ElggWidget::getContext()` — use `$entity->context`
- `ElggWidget::setContext()` — use `$entity->context = $context`
- `Elgg\Notifications\NotificationsService::getDeprecatedHandler()`
- `Elgg\Notifications\NotificationsService::getMethodsAsDeprecatedGlobal()`
  — use `elgg_get_notification_methods()`
- `Elgg\Notifications\NotificationsService::registerDeprecatedHandler()`
- `Elgg\Notifications\NotificationsService::setDeprecatedNotificationSubject()`
- `Elgg\Email::getRecipient()` — use `Elgg\Email::getTo()`
- `Elgg\Email::setRecipient()`
- `Elgg\Entity::getLocation()` — use `$entity->location`
- `Elgg\Entity::setLocation()` — use `$entity->location = $location`

## Removed lib functions

### Access and session

- `access_get_show_hidden_status()` — use
  `elgg()->session->getDisabledEntityVisibility()`

### Diagnostics

- `diagnostics_md5_dir()`

### External files

- `elgg_get_loaded_css()` — use
  `elgg_get_loaded_external_files('css', 'head')`
- `elgg_get_loaded_js()` — use
  `elgg_get_loaded_external_files('js', $location)`
- `elgg_prepend_css_urls()`

### Groups

- `group_access_options()`

### Menus and filter tabs

- `elgg_get_filter_tabs()` — use menu hooks on
  `'register', 'menu:filter:<filter_id>'`

### Pages

- `pages_is_page()`

### Plugin settings

- `elgg_get_all_plugin_user_settings()`
- `elgg_get_entities_from_plugin_user_settings()` — use
  `elgg_get_entities()` with private settings parameters and prefix your
  setting name with `plugin:user_setting:`
- `elgg_set_plugin_setting()` — use `$plugin->setSetting($name, $value)`
- `elgg_set_plugin_user_setting()` — use `ElggUser::setPluginSetting()`
- `elgg_unset_plugin_setting()` — use `$plugin->unsetSetting($name)`
- `elgg_unset_plugin_user_setting()` — use `ElggUser::removePluginSetting()`

### Subscriptions

- `elgg_add_subscription()` — use `\ElggEntity::addSubscription()`
- `elgg_remove_subscription()` — use `\ElggEntity::removeSubscription()`

### System messages

- `elgg_get_system_messages()` — use
  `elgg()->system_messages->loadRegisters()`
- `elgg_set_system_messages()` — use
  `elgg()->system_messages->saveRegisters()`

### System log

- `system_log_archive_log()`
- `system_log_browser_delete_log()`
- `system_log_get_log()`
- `system_log_get_log_entry()`
- `system_log_get_object_from_log_entry()`
- `system_log_get_seconds_in_period()`

### The wire

- `thewire_get_parent()` — use `\ElggWire::getParent()`

### Translations

- `elgg_get_available_languages()` — use
  `elgg()->translator->getAvailableLanguages()`
- `get_installed_translations()` — use
  `elgg()->translator->getInstalledTranslations()`
- `get_language_completeness()` — use
  `elgg()->translator->getLanguageCompleteness()`

### Validation

- `validate_email_address()` — use `elgg()->accounts->assertValidEmail()`
- `validate_password()` — use `elgg()->accounts->assertValidPassword()`
- `validate_username()` — use `elgg()->accounts->assertValidUsername()`

## Removed views and resources

- `admin/develop_tools/inspect/webservices`
- `elgg/thewire.js`
- `input/urlshortener`
- `messages/js` — moved to `forms/messages/process.js`
- `navigation/menu/elements/item_deps` — the functionality has been merged
  into `navigation/menu/elements/item`
- `object/plugin/elements/contributors`
- `notifications/groups`
- `notifications/personal` — use `notifications/settings` or
  `notifications/users`
- `notifications/settings/collections`
- `notifications/settings/other` — extend `notifications/settings/records`
- `notifications/settings/personal` — moved to
  `notifications/settings/records`
- `notifications/subscriptions/groups` — use
  `forms/notifications/subscriptions/groups`
- `notifications/subscriptions/users` — use
  `forms/notifications/subscriptions/users`
- `reportedcontent/admin_css`
- `resources/comments/view` — use
  `\Elgg\Controllers\CommentEntityRedirector`
- `resources/river` — use `resources/activity/all`,
  `resources/activity/owner`, or `resources/activity/friends`
- `thewire/previous`

## Removed hooks / events

- Event `created, river` has been removed; use the `create:after, river`
  event
- Hook `creating, river` has been removed; use the `create:before, river`
  event if you want to block the creation of a river item
- Hook `filter_tabs, <context>` has been removed; use the
  `register, menu:filter:<filter_id>` hook
- Hook `output, ajax` has been removed; use the `ajax_response` hook if you
  want to influence the results
- Hook `reportedcontent:add` has been removed; use the `create, object`
  event to prevent creation
- Hook `reportedcontent:archive` has been removed; use the
  `permissions_check, object` hook
- Hook `reportedcontent:delete` has been removed; use the `delete, object`
  event to prevent deletion

## Removed actions

- The action `reportedcontent/delete` has been replaced with a generic
  entity delete action

## Web services plugin

### Removed classes

- `ElggHMACCache` — replaced by `_elgg_services()->hmacCacheTable` (for
  internal use only)
- `Elgg\Notifications\Event` — replaced by
  `Elgg\Notifications\SubscriptionNotificationEvent`

### Removed functions

- `create_api_user()` — replaced by
  `_elgg_services()->apiUsersTable->createApiUser()`
- `create_user_token()` — replaced by
  `_elgg_services()->usersApiSessions->createToken()`
- `get_api_user()` — replaced by
  `_elgg_services()->apiUsersTable->getApiUser()`
- `get_standard_api_key_array()` — use
  `\Elgg\WebServices\ElggApiClient::setApiKeys()`
- `get_user_tokens()` — replaced by
  `_elgg_services()->usersApiSessions->getUserTokens()`
- `pam_auth_session()`
- `remove_api_user()` — replaced by
  `_elgg_services()->apiUsersTable->removeApiUser()`
- `remove_expired_user_tokens()` — replaced by
  `_elgg_services()->usersApiSessions->removeExpiresTokens()`
- `remove_user_token()` — replaced by
  `_elgg_services()->usersApiSessions->removeToken()`
- `send_api_call()` — use `\Elgg\WebServices\ElggApiClient`
- `send_api_get_call()` — use `\Elgg\WebServices\ElggApiClient`
- `send_api_post_call()` — use `\Elgg\WebServices\ElggApiClient`
- `service_handler()`
- `validate_user_token()` — replaced by
  `_elgg_services()->usersApiSessions->validateToken()`
- `ws_page_handler()`
- `ws_rest_handler()` — replaced by
  `\Elgg\WebServices\RestServiceController`

### Miscellaneous changes

- The config value for `servicehandler` has been removed
- In certain edge cases the default value of an API parameter will not be
  applied
