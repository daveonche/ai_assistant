# Elgg Developer Guide: Plugins

Delta distillation of <https://learn.elgg.org/en/stable/guides/plugins.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/plugins.rst`, Elgg ref `7.1`). Records only what counters
stale training-data memory: current API names, signatures, defaults,
deprecations, gotchas. Update in place when the stable manual changes.

A plugin is recognized by a `composer.json` file in the plugin root. The
page's pillars: the static `elgg-plugin.php` config, a bootstrap class,
optional `elgg-services.php` DI definitions, and PHPUnit tests. Its subpages
(`plugin-skeleton`, `dependencies`, `bootstrap`) live in the `plugins/`
subdirectory (pending enumeration; see `index.md`).

## elgg-plugin.php — static plugin configuration

- Read by Elgg to configure various services; must return an array if
  present.
- Should NOT be included by plugins and is not guaranteed to run at any
  particular time.
- Besides magic constants like `__DIR__`, its return value must not change.

Supported sections (each eliminates a manual registration call):

| Section | Replaces / configures |
| :--- | :--- |
| `plugin` | readable `name`, `version`, `activate_on_install` (fresh install only), `dependencies` |
| `bootstrap` | class implementing `\Elgg\PluginBootstrapInterface` |
| `entities` | type/subtype/class registration + `capabilities` (e.g. `searchable`) |
| `actions` | `elgg_register_action()` |
| `routes` | `elgg_register_route()` |
| `settings` / `user_settings` | defaults for `elgg_get_plugin_setting()` / `elgg_get_plugin_user_setting()` |
| `views` | vendor asset aliases into the view system |
| `widgets` | `elgg_register_widget_type()` |
| `events` | `elgg_register_event_handler()` |
| `cli_commands` | `Elgg\Cli\Command` classes extending `elgg-cli` |
| `view_extensions` | `elgg_extend_view()` / `elgg_unextend_view()` |
| `theme` | theme variables array |
| `group_tools` | group tool options |
| `view_options` | per-view options (ajax, simplecache) |
| `notifications` | notification events |
| `web_services` | exposed web service API methods |

Key defaults and gotchas:

- Actions: default access is `logged_in`; Elgg looks for the file at
  `actions/<action>.php` in the plugin by default; `access` supports
  `public`, `logged_in`, `logged_out`, `admin`; a `controller` key swaps the
  action file for a callable receiving `\Elgg\Request` as first and only
  argument (e.g. `MyActionController::__invoke(\Elgg\Request $request)`).
- Routes: associate a `resource` view or a `controller`; other parameters
  (`middleware`, `requirements`, `defaults`) — see `elgg_register_route()`.
- Widgets: entry `my_stuff` corresponds to view `widgets/my_stuff/content`.
- Events / view_extensions / group_tools / view_options / notifications:
  support `'unregister' => true` (or `'unextend' => true`) to remove
  registrations made elsewhere; `priority` orders handlers.
- Notifications: handler classes must extend
  `Elgg\Notifications\NotificationEventHandler`.
- Web services: per HTTP method (`GET|POST`), `callback` is required;
  `params` types are limited to `int|integer|bool|string|float|array`;
  `require_api_auth`, `require_user_auth`, `associative` all default to
  `false`; a missing `description` falls back to translation key
  `web_services:api_methods:<method>:<http call method>:description`.
- `plugin.dependencies` entries: `position` (`before`/`after`),
  `must_be_active`, `version` (Composer version constraint).
- `view_options`: `'ajax' => true` registers a view as ajax-available,
  `false` unregisters it; `'simplecache' => true` marks a view
  simplecache-usable.

## Bootstrap class

- Recommended since Elgg 3.0; must implement `\Elgg\PluginBootstrapInterface`
  and is registered under the `bootstrap` key of `elgg-plugin.php`.
- The interface defines methods called at different points of the system
  boot process — see the `plugins/bootstrap` subpage.

## elgg-services.php — DI definitions

- Optional file in the plugin root; must return an array of PHP-DI
  definitions; attached services become available via `elgg()`:

```php
return [
   PluginService::class => \DI\object()->constructor(\DI\get(DependencyService::class)),
];
```

```php
$service = elgg()->get(PluginService::class);
```

- See the PHP-DI documentation for autowiring and invocation possibilities.

## composer.json

- Minimum for Composer compatibility: a `composer.json` in the plugin root.
- `name`: keep inline with the plugin folder name for correct installation.
- `type`: ALWAYS `elgg-plugin`.
- Suggested: a `conflict` rule excluding Elgg versions below the plugin's
  minimum, preventing accidental installation on incompatible versions.
- Register the project on Packagist so others can install it.

## Tests

- Location: `tests/phpunit/unit` (extend `Elgg\UnitTestCase`) and
  `tests/phpunit/integration` (extend `Elgg\Plugins\IntegrationTestCase`).
- Global integration tests run against all active plugins:

| Test | Checks |
| :--- | :--- |
| `Elgg\Plugins\ActionRegistrationIntegrationTest` | all registered actions, without supplying data |
| `Elgg\Plugins\ComposerIntegrationTest` | `composer.json` validity |
| `Elgg\Plugins\StaticConfigIntegrationTest` | `elgg-plugin.php` section format |
| `Elgg\Plugins\TranslationsIntegrationTest` | language file format and encoding |
| `Elgg\Plugins\ViewStackIntegrationTest` | PHP parsing errors in views |
