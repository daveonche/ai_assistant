# Elgg Developer Guide: Capabilities

Delta distillation of <https://learn.elgg.org/en/stable/guides/capabilities.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/capabilities.rst`, Elgg ref `7.1`). Records only what counters
stale training-data memory: current API names, signatures, defaults,
deprecations, gotchas. Update in place when the stable manual changes.

## Defining capabilities

There is no need to explicitly define or register a new capability in the
system: a capability name exists as soon as some code uses it. For example,
the `search` plugin uses the `searchable` capability.

## Registering for capabilities

If an entity supports a capability (or feature), register it in the
`entities` section of the plugin's `elgg-plugin.php`:

```php
'entities' => [
    [
        'type' => 'object',
        'subtype' => 'blog',
        'capabilities' => [
            'searchable' => true,
        ],
    ],
],
```

A capability can also be enabled or disabled for a type/subtype after the
fact:

- `elgg_entity_enable_capability($type, $subtype, $capability)` — enable a
  capability.
- `elgg_entity_disable_capability($type, $subtype, $capability)` — disable a
  capability.

## Checking for capabilities

- `$entity->hasCapability($capability)` — check whether an entity supports a
  capability.
- `elgg_entity_has_capability($type, $subtype, $capability)` — same check
  when no entity instance is at hand.
- `elgg_entity_types_with_capability($capability)` — get an array of all
  type/subtypes in the system that support a capability:

```php
$types_subtypes = elgg_entity_types_with_capability('searchable');

// output
[
    'object' => [
        'blog',
        'page',
    ],
    'group' => [
        'group',
    ],
]
```
