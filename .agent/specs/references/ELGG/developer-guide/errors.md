# Elgg Developer Guide: Errors

Delta distillation of <https://learn.elgg.org/en/stable/guides/errors.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/errors.rst`, Elgg ref `7.1`). Records only what counters stale
training-data memory: current API names, signatures, defaults, deprecations,
gotchas. Update in place when the stable manual changes.

## Monolog logging

- Under the hood, Elgg uses [Monolog](https://github.com/Seldaek/monolog) for
  logging errors to the server's error log; CLI commands log to stdout.
- Monolog comes with a number of tools that help administrators keep track of
  errors and debugging information.
- Custom handlers are added to the `elgg()->logger` Monolog instance via
  `pushHandler()`; see the Monolog documentation for a full list of handlers.
- Handler levels are `\Monolog\Level` enum cases (e.g.
  `\Monolog\Level::Critical` below).

```php
// Add a new handler to notify a given email about a critical error
elgg()->logger->pushHandler(
    new \Monolog\Handler\NativeMailerHandler(
        'admin@example.com',
        'Critical error',
        'no-reply@mysite.com',
        \Monolog\Level::Critical
    )
);
```
