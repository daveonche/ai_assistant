# Removed APIs: 4.x to 5.0

Exhaustive enumeration of the classes, functions, class functions, events,
exceptions and constants removed in the 4.x to 5.0 transition, distilled
from <https://learn.elgg.org/en/stable/appendix/upgrade-notes/4.x-to-5.0.html>.

## Moved classes

- `\ElggAutoP` — moved to `\Elgg\Views\AutoParagraph`
- `\ElggCache` — moved to `\Elgg\Cache\BaseCache`
- `\ElggDiskFilestore` — moved to
  `\Elgg\Filesystem\Filestore\DiskFilestore`
- `\ElggFilestore` — moved to `\Elgg\Filesystem\Filestore`
- `\ElggRewriteTester` — moved to `\Elgg\Router\RewriteTester`
- `\ElggTempDiskFilestore` — moved to
  `\Elgg\Filesystem\Filestore\TempDiskFilestore`
- `\Elgg\Database\SiteSecret` — moved to `\Elgg\Security\SiteSecret`

## Removed classes

- `Elgg\WebServices\ApiKeyForm`
- `Loggable` — this interface has been merged into the `ElggData` class

## Removed functions

- `blog_prepare_form_vars`
- `bookmarks_prepare_form_vars`
- `discussion_prepare_form_vars`
- `elgg_get_breadcrumbs`
- `elgg_pop_breadcrumb`
- `elgg_set_email_transport` — use
  `_elgg_services()->set('mailer', ...)`
- `elgg_trigger_deprecated_plugin_hook`
- `elgg_ws_expose_function` — use `elgg-plugin.php` or the
  `'register', 'api_methods'` event
- `file_prepare_form_vars`
- `get_user_by_email` — use `elgg_get_user_by_email`
- `get_user_by_username` — use `elgg_get_user_by_username`
- `groups_prepare_form_vars`
- `messages_prepare_form_vars`
- `pages_prepare_form_vars`
- `thewire_latest_guid`

## Removed class functions

- `\ElggWidget::saveSettings()`

## Removed events

- `access:collections:addcollection, collection` — use the
  `create, access_collection` sequence
- `access:collections:deletecollection, collection` — use the
  `delete, access_collection` sequence
- `prepare, breadcrumbs` — use `register, menu:breadcrumbs`
- `widget_settings, <widget_handler>`

## Removed exceptions

- `\Elgg\Exceptions\InvalidParameterException`

## Constants

- The misspelled `REFERER` constant has been removed; use `REFERRER`
  instead
- The `REFERRER` constant has been changed to a string with the value
  `__elgg_referrer`
