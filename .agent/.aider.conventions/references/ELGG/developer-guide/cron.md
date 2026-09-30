# Elgg Developer Guide: Cron

Delta distillation of <https://learn.elgg.org/en/stable/guides/cron.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/cron.rst`, Elgg ref `7.1`). Records only what counters stale
training-data memory: current API names, signatures, defaults, deprecations,
gotchas. Update in place when the stable manual changes.

## Prerequisite

Cron must be set up as described in `/admin/cron` before special events are
triggered; only then can plugins register for these events from their own
code.

## Registering a cron handler

Register a function for a cron period (here: the daily cron) from the
plugin's init:

```php
function my_plugin_init() {
    elgg_register_event_handler('cron', 'daily', 'my_plugin_cron_handler');
}
```

The handler receives an `\Elgg\Event`:

```php
function my_plugin_cron_handler(\Elgg\Event $event) {
    $start_time = $event->getParam('time');
}
```

## Timing

Cron functions are executed in order of registration, so a handler may start
(a lot) later than expected. The event parameters contain the original
starting time of the cron, so timing-sensitive handlers should use
`$event->getParam('time')` rather than the actual execution time.

## Custom intervals

Plugin developers can configure their own custom intervals:

```php
elgg_register_event_handler('cron:intervals', 'system', 'my_custom_cron_interval');

function my_custom_cron_interval(\Elgg\Event $event) {
    $cron_intervals = $event->getValue();

    // add custom interval
    $cron_intervals['my_custom_interval'] = '30 16 * * *'; // every day at 16:30 hours

    return $cron_intervals;
}
```

Warning: it is **not** recommended to add custom intervals — users of the
plugin would also need to configure the custom interval. Work with the
default intervals instead. For a task that must run at 16:30 daily, use the
`halfhour` interval and check `date('G', $start_time) == 16` and
`date('i', $start_time) == 30`.

## See also

- `/design/events` for more information about events.
- For the supported cron interval definition see the
  [PHP Scheduler documentation](https://github.com/peppeocchi/php-cron-scheduler#schedules-execution-time).
