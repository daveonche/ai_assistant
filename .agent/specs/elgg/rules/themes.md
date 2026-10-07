# Elgg Developer Guide: Themes

Delta distillation of <https://learn.elgg.org/en/stable/guides/themes.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/themes.rst`, Elgg ref `7.1`). Records only what counters
stale training-data memory: current API names, signatures, defaults,
deprecations, gotchas. Update in place when the stable manual changes.

A theme is a plugin that overrides display aspects of Elgg. The guide
assumes familiarity with the admin plugins page and the view system
(`views.md`).

## Theming principles and best practices

- **No third-party CSS frameworks** — frameworks lock users into specific
  HTML markup, making it harder for plugins to collaborate on appearance
  (`is-primary` in one theme means something else in another). Without a
  framework, plugins alter appearance with pure CSS on semantic classes
  (`box-role`) instead of overwriting views or appending
  framework-specific selectors to markup.
- **8-point grid system** — size elements, padding, and margins in
  increments and fractions of `8px`; default font-size is `16px`, so use
  `rem` fractions (`0.5rem = 8px`). BAD: `margin: 2px 2px 2px 0`,
  `padding: 3px 5px`; GOOD: `padding: 0.25rem 0.5rem`.
- **Mobile first** — two breakpoints: `50rem` and `80rem` (800px and
  1280px at 16px/rem). Mobile styles by default; media blocks style larger
  viewports with `min-width` (the BAD example restyles mobile inside a
  `max-width: 820px` block).
- **Flexbox driven** — flexbox for everything from menus to layout
  elements; the BAD pattern is clearfix + floats, the GOOD pattern is
  `display: flex` + `order` (with `margin-right: auto` pushing the
  heading's controls right).
- **Simple color transitions** — 4 color sets for text, background and
  border: `soft`, `mild`, `strong`, `highlight`. Hover/active: one level
  up (e.g. `soft` → `mild`) or `highlight`; inactive/disabled: one level
  down.
- **Increase the click area** — with nested anchors, enlarge the anchor's
  click area (padding on the `<a>`), not the parent's.
- **No z-index 999999** — z-indexes increment with a step of 1.
- **Wrap HTML siblings** — no orphaned strings inside a parent; wrap
  siblings so CSS can target them (two `<span>`s inside `<label>` instead
  of an orphan text node + one `<span>`; title + subtitle wrapped in a
  `div.left` beside a `div.right`).

## Create your plugin

Create the theme as a normal plugin (see the developer guide): a new
directory under `mod/`, an `elgg-plugin.php`, and a `composer.json`
describing the theme.

## Customize the CSS

CSS is split into files by site aspect so they can be tackled one at a
time. Existing CSS views:

| View | Covers |
| :--- | :--- |
| `elements/buttons.css` | all button kinds; plugins expect 5: `action`, `cancel`, `delete`, `submit`, `special` |
| `elements/chrome.css` | miscellaneous look-and-feel classes |
| `elements/components.css` | css objects used site-wide: media block, list, gallery, table, owner block, system messages, river, tags, photo, comments |
| `elements/forms.css` | forms and input elements |
| `elements/icons.css` | icons and avatars |
| `elements/layout.css` | page layout: sidebars, page wrapper, main body, header, footer |
| `elements/modules.css` | modules (boxes with title + content body): `info`, `aside`, `featured`, `dropdown`, `popup`, `widget`; widget styles live here too (widgets are a module subset) |
| `elements/navigation.css` | menus |
| `elements/typography.css` | content and headings |
| `rtl.css` | rules for right-to-left languages |
| `admin.css` | separate admin-area theme (usually not overridden) |
| `elgg.css` | compiles all core `elements/*` files into one (DO NOT OVERRIDE) |
| `elements/reset.css` | reset stylesheet forcing elements to the same default (description ends mid-sentence in the source) |

### CSS variables

- Global CSS variables are available in PHP and in CSS; plugins should use
  them and extend the core theme with their own variables so other plugins
  can alter them simply.
- Add or alter variables via the `theme` section in `elgg-plugin.php`
  (see `plugins.md`); flush the cache to see changes.
- Default core variables: see `engine/theme.php`.

### Dark mode

- The theme supports different color schemes, separated by a key in the
  `theme` configuration; the `dark` scheme is the site's dark mode.
- When a site administrator enables the user choice for dark mode, a user
  decides in their personal settings whether dark mode (or another
  available color scheme) is enabled or auto-detected.

### View extension

Add extra content to an existing view via the `view_extensions` section of
`elgg-plugin.php` — e.g. append `mytheme/css` to Elgg's core css file:

```php
<?php
return [
   'view_extensions' => [
      'mytheme/css' => [],
   ],
];
```

- Gotchas in the source: the prose calls the section `views_extensions`
  while the example (and the plugins page) use `view_extensions`; and the
  printed example maps `mytheme/css` directly under `view_extensions`
  without naming the extended target view (`elgg.css`) that the prose
  says is being extended — cross-check the expected key structure before
  adapting.

### View overloading

- A plugin's view hierarchy replaces core files while the plugin is
  active: `/mod/myplugin/views/default/elements/typography.css` replaces
  `/views/default/elements/typography.css`.
- This gives total control over the way Elgg looks and behaves: slightly
  modify or totally replace existing views.

## Icons

- Default Elgg icons come from the FontAwesome library (since Elgg 2.0):
  `elgg_view_icon('icon-name')`.
- `icon-name` is any FontAwesome icon without the `fa-` prefix.
- Default variant is solid; postfix the name with `-solid`, `-regular` or
  `-light` to target a specific style.
- Gotcha: the `light` variant is only available as a FontAwesome Pro
  licensed icon.

## Tools

- Turn on the "Developers" plugin and use its "Theme Preview" page to
  track the theme's progress.

## Customizing the front page

- The main Elgg index page is served via a resource view; override it by
  providing `your_plugin/views/default/resources/index.php`.
