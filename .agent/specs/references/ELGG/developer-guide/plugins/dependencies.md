# Elgg Developer Guide: Plugin Dependencies

Delta distillation of
<https://learn.elgg.org/en/stable/guides/plugins/dependencies.html>,
distilled from the stable manual on 2026-10-01 (source:
`docs/guides/plugins/dependencies.rst`, Elgg ref `7.1`). Records only what
counters stale training-data memory: current API names, signatures,
defaults, deprecations, gotchas. Update in place when the stable manual
changes.

The dependencies system prevents plugins from being used on incompatible
systems. It is controlled through a plugin's `elgg-plugin.php` file or
`composer.json`. Plugin authors can specify that a plugin:

- requires certain Elgg plugins, PHP version or PHP extensions;
- conflicts with certain Elgg versions or plugins.

## PHP version or extension

Add a `require` section in `composer.json` (Composer JSON schema, package
links):

```json
{
    "require": {
        "php": ">8.3",
        "ext-json": "*"
    }
}
```

## Require an Elgg plugin

Add a `plugin` → `dependencies` section to `elgg-plugin.php` (see the
plugins guide):

```php
return [
    'plugin' => [
        'dependencies' => [
            // optional list of plugin dependencies
            'blog' => [], // blog needs to be active
            'activity' => [
                'position' => 'after', // in the plugin order this plugin must be after the activity plugin
                'must_be_active' => false, // but the plugin isn't required to be active, but if active order will be checked
            ],
            'file' => [
                'position' => 'before', // file must be active and this plugin needs to be before the file plugin in the plugin order
                'version' => '>2', // composer notation of required version constraint
            ],
        ],
    ],
];
```

- `position` — `after`/`before` constrains the plugin order relative to
  the dependency.
- `must_be_active` — `false` means the dependency need not be active, but
  if it is active the order is still checked.
- `version` — Composer version-constraint notation.

## Conflicts

Add a `conflict` section in `composer.json`:

```json
{
    "conflict": {
        "elgg/elgg": "<4.0",
        "elgg/dataviews": "<1.0 || >= 1.5"
    }
}
```
