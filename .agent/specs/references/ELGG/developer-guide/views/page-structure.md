# Elgg Developer Guide: Page Structure

Delta distillation of
<https://learn.elgg.org/en/stable/guides/views/page-structure.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/views/page-structure.rst`, Elgg ref `7.1`). Records only what
counters stale training-data memory: current API names, signatures,
defaults, deprecations, gotchas. Update in place when the stable manual
changes.

An Elgg page has an overall pageshell, a main layout, and several page
elements.

## Layout and page

Always use the `default` layout — every page element can be controlled
through it. For other layouts, call `elgg_view_layout($layout_name,
$elements)`: the page elements are passed as an array in the second
parameter; array keys correspond to elements in the layout, values are the
HTML displayed in those areas:

```php
$layout_area = elgg_view_layout($layout_name, [
    'content' => $content,
    'section' => $section,
]);
```

For the `default` layout:

```php
$layout_area = elgg_view_layout('default', [
    'content' => $content,
    'sidebar' => $sidebar,
]);
```

Pass the layout into `elgg_view_page`:

```php
echo elgg_view_page($title, $layout_area);
```

With the `default` layout you can skip `elgg_view_layout` and pass the
elements array directly to `elgg_view_page`:

```php
echo elgg_view_page($title, [
    'content' => $content,
    'sidebar' => $sidebar,
]);
```

## Controllable page elements

```php
echo elgg_view_page('This is the browser title', [
    'title' => 'This is the page title',
    'content' => $content,
    'sidebar' => false, // no default sidebar
    'sidebar_alt' => $sidebar_alt, // show an alternate sidebar
]);
```

- Gotcha: the first `elgg_view_page` argument is the browser title; the
  `'title'` array key sets the page title separately.
- `'sidebar' => false` suppresses the default sidebar; `'sidebar_alt'`
  renders an alternate sidebar.

See the `page/layouts/default` view for the full list of supported page
elements.
