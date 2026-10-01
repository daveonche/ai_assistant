# Elgg Developer Guide: Simplecache

Delta distillation of
<https://learn.elgg.org/en/stable/guides/views/simplecache.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/views/simplecache.rst`, Elgg ref `7.1`). Records only what
counters stale training-data memory: current API names, signatures,
defaults, deprecations, gotchas. Update in place when the stable manual
changes.

A mechanism that alleviates the need for certain views to be regenerated
dynamically: they are generated once, saved as a static file, and served in
a way that entirely bypasses the Elgg engine.

If Simplecache is turned off (from the administration panel), these views
are served as normal — with the exception of site CSS.

## Suitability criteria

A view is suitable for the Simplecache only if:

- it does not change depending on who or when it is being looked at;
- it does not depend on variables fed to it (except for global variables
  like the site URL that never change).

## Regenerating the cache

The Simplecache regenerates when you:

- load `/upgrade.php`, even if you have nothing to upgrade;
- click 'Flush the caches' in the admin panel;
- enable or disable a plugin;
- reorder your plugins.

## Using it in plugins

Register a view at init-time:

```php
elgg_register_simplecache_view($viewname);
```

Get the URL to the cached view with `elgg_get_simplecache_url($view)` — for
a view stored as `your_view.js` or `your_view.css` in the view folder:

```php
$js = elgg_get_simplecache_url('your_view.js');
$css = elgg_get_simplecache_url('your_view.css');
```

Gotcha: never hardcode simplecache URLs — always resolve them with
`elgg_get_simplecache_url()`.

See also: the admin performance docs and the views guide (the source
page's `.. seealso::` targets).
