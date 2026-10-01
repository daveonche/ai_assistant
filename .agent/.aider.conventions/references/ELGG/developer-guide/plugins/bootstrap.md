# Elgg Developer Guide: Plugin Bootstrap

Delta distillation of
<https://learn.elgg.org/en/stable/guides/plugins/bootstrap.html>,
distilled from the stable manual on 2026-10-01 (source:
`docs/guides/plugins/bootstrap.rst`, Elgg ref `7.1`). Records only what
counters stale training-data memory: current API names, signatures,
defaults, deprecations, gotchas. Update in place when the stable manual
changes.

As of Elgg 3.0, bootstrap a plugin with a bootstrap class implementing
`\Elgg\PluginBootstrapInterface`. Recommended: extend the
`\Elgg\PluginBootstrap` abstract class (preparations already done). If you
need only a limited subset, extend `\Elgg\DefaultPluginBootstrap` — every
interface function is implemented, so you overload only what you need.

## Registration

Register the bootstrap class in `elgg-plugin.php`:

```php
return [
    // Bootstrap must implement \Elgg\PluginBootstrapInterface
    'bootstrap' => MyPluginBootstrap::class,
];
```

## Lifecycle functions

- `load()` — during `plugins_load`, `system` event: require additional
  files, configure services prior to booting the plugin.
- `boot()` — during `plugins_boot:before`, `system` event: register
  handlers for `plugins_boot`/`init` system events, implement boot-time
  logic.
- `init()` — during `init`, `system` event: implement business logic,
  register all other handlers.
- `ready()` — during `ready`, `system` event: logic after all plugins are
  initialized.
- `shutdown()` — during `shutdown`, `system` event: logic during shutdown.
- `activate()` — on plugin activation, after the `activate`, `plugin`
  event.
- `deactivate()` — on plugin deactivation, after the `deactivate`,
  `plugin` event.
- `upgrade()` — registered as handler for `upgrade`, `system` event:
  logic during system upgrade.

## Helper functions

Available when extending `\Elgg\PluginBootstrap` or
`\Elgg\DefaultPluginBootstrap`.

`elgg()` returns Elgg's public DI container — e.g. to register event
listeners:

```php
$events = $this->elgg()->events;
$events->registerHandler('create:after', 'object', MyCustomObjectHandler::class);
```

`plugin()` returns the plugin entity this bootstrap is related to — e.g.
to read plugin settings:

```php
$plugin = $this->plugin();
$my_setting = $plugin->getSetting('my_setting');
```
