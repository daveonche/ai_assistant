# Elgg Developer Guide: Walled Garden

Delta distillation of <https://learn.elgg.org/en/stable/guides/walled-garden.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/walled-garden.rst`, Elgg ref `7.1`). Records only what counters
stale training-data memory: current API names, signatures, defaults,
deprecations, gotchas. Update in place when the stable manual changes.

Elgg supports a "Walled Garden" mode: almost all pages are restricted to
logged-in users. Useful for sites that don't allow public registration.
Routing tie-in: the `WalledGarden` middleware (see `routing.md`) is
auto-enabled for ALL routes when the site is walled-garden configured and
no user is logged in; the per-route `'walled' => false` option documented
below is how a route opts out.

## Activating Walled Garden mode

- In the Administration section, right sidebar menu under "Configure":
  expand "Settings", then click "Advanced".
- On the Advanced Settings page, find the option labelled "Restrict pages
  to logged-in users", enable it, and click "Save" to switch the site into
  Walled Garden mode.

## Exposing pages through Walled Gardens

- Walled Garden mode prevents plugin-added pages from being viewed by
  logged-out users. Elgg uses events to manage which pages are visible
  through the Walled Garden (the source links the events documentation in
  the design docs — outside this guide set).
- Plugin authors must register pages as public if they should be viewable
  through Walled Gardens:
  - by setting `'walled' => false` in route configuration (preferred), or
  - by responding to the `public_pages`, `walled_garden` event — the
    returned value is an array of regexp expressions for public pages.

Example — expose `http://example.org/my_plugin/public_page` through a
Walled Garden, assuming the plugin has registered a route for
`my_plugin/public_page` (route registration: `routing.md`):

```php
// Preferred way
elgg_register_route('my_plugin:public_page', [
    'path' => '/my_plugin/public_page',
    'resource' => 'my_plugin/public_page',
    'walled' => false,
]);

// Legacy approach
elgg_register_event_handler('public_pages', 'walled_garden', 'my_plugin_walled_garden_public_pages');

function my_plugin_walled_garden_public_pages(\Elgg\Event $event) {
   $pages = $event->getValue();

   $pages[] = 'my_plugin/public_page';

   return $pages;
}
```

- Gotcha: legacy-handler entries are regexp expressions — the example's
  `'my_plugin/public_page'` (no leading slash) is matched as a pattern, so
  craft entries accordingly.
