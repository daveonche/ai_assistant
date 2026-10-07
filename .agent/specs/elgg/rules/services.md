# Elgg Developer Guide: Services

Delta distillation of <https://learn.elgg.org/en/stable/guides/services.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/services.rst`, Elgg ref `7.1`). Records only what counters stale
training-data memory: current API names, signatures, defaults, deprecations,
gotchas. Update in place when the stable manual changes.

## Application

- `Elgg\Application` loads and bootstraps Elgg.
- A set of service objects for plugins to use on this class is planned for
  future releases.

## Menus

- `elgg()->menus` provides low-level methods for constructing menus.
- Pass menus to `elgg_view_menu()` for rendering instead of rendering them
  manually.

## Contributing

- New service proposals belong in the contributing guide:
  <https://learn.elgg.org/en/stable/contribute/services.html>.
