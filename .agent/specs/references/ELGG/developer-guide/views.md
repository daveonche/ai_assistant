# Elgg Developer Guide: Views

Delta distillation of <https://learn.elgg.org/en/stable/guides/views.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/views.rst`, Elgg ref `7.1`). Records only what counters
stale training-data memory: current API names, signatures, defaults,
deprecations, gotchas. Update in place when the stable manual changes.

Views create output: page layouts, presentation chunks (footer, toolbar),
individual links and form inputs, and the images/js/css a page needs. A
view is a PHP file under `views/<viewtype>/`; its name mirrors the path
below the viewtype directory (`views/default/hello/world.php` →
`elgg_view('hello/world')`). Subpages `views/page-structure`,
`views/simplecache`, `views/foot-vs-footer` are pending (see `index.md`).

## Views as templates

- Pass arbitrary data via the `$vars` array:
  `elgg_view('hello/world', ['name' => 'World'])` renders
  `<h1>Hello, <?= $vars['name']; ?>!</h1>`.
- Warning: views do no automatic output sanitization — sanitize yourself
  to prevent XSS.

## Cacheable asset views

Asset views (JS, CSS, images) must:

- take no `$vars` parameters;
- not change output based on global state (who is logged in, time of day);
- have a valid file extension (`my/cool/template.html`, not
  `my/cool/template`).

- Gotcha: leave off the trailing `.php` from the filename and Elgg
  recognizes the view as cacheable — `views/default/mystyles.css.php` is
  the view `mystyles.css`.
- URL: `elgg_get_simplecache_url('mystyles.css')` returns e.g.
  `https://mysite.com/.../289124335/default/mystyles.css` — the magic
  numbers bust caches; long-term expires headers are set automatically.
- Load on a page with `elgg_require_css('mystyles')` (no `.css` suffix
  here, unlike `elgg_get_simplecache_url`).
- Warning: the URL is not stable by design (structure may change between
  releases; the numbers change on every cache flush). Anti-patterns:
  relying on the exact URL structure/location, generating the URLs
  yourself, storing returned URLs in a database.

## Third-party assets and extra view directories

- Map assets into the views system via the `"views"` key in
  `elgg-plugin.php`: a 2-dimensional array — first level maps a viewtype
  to mappings, then view name → file path (absolute, or relative to the
  install root when the leading slash is omitted, e.g. Composer/NPM asset
  `vendor/npm-asset/...`). Core returns its mappings directly from
  `/engine/views.php` (see `plugins.md`).

```php
return [
   'views' => [
      'default' => [
         'js/jquery-ui.js' => __DIR__ . '/node_modules/components-jqueryui/jquery-ui.min.js',
      ],
   ],
];
```

- Additional view directories: a view-name prefix ending with `/` maps to
  a scanned directory — `'file/icon/' => __DIR__ . '/graphics/icons'`
  creates view `file/icon/general.gif` from
  `mod/file/graphics/icons/general.gif`. The scan is fully recursive.
- Multiple paths can share one prefix (array of paths); they are processed
  in order, so later paths may override.

## Viewtypes

- The subdirectory under `/views` is the *viewtype* — the output format
  (default = HTML; also RSS, ATOM, JSON, mobile/TV-optimized HTML, ...).
- Force a viewtype with the `view` input (`https://mysite.com/?view=rss`)
  or `elgg_set_viewtype('iphone')` (e.g. after detecting an iPhone's
  browser string).

## Altering views via plugins

Four ways without modifying core: override, extend, alter input by event,
alter output by event.

### Overriding

- Plugin views always override core views; between plugins, later plugins
  take precedent (plugin order).
- `/mod/example/views/default/hello/world.php` replaces the core
  `hello/world` view.
- Note: overriding core/bundled views has a maintenance cost — upgrades
  change views and overrides miss those changes; prefer altering input or
  output via events.
- Note: Elgg caches view locations — disable the system cache while
  developing; flush caches when installing to production.

### Extending

```php
elgg_extend_view('hello/world', 'hello/greeting');       // appends
elgg_extend_view('hello/world', 'hello/greeting', 450);  // prepends (< 500)
```

- Register all extensions in `elgg-plugin.php` (`view_extensions`).

### Altering input — `["view_vars", $view_name]` event

Runs before each rendering; the handler receives an `\Elgg\Event` whose
value is the modified `$vars`, with params:

- `vars` — the original `$vars` array, unaltered
- `view` — the view name
- `viewtype` — the viewtype being rendered

Example — default pagination limit for comments:

```php
elgg_register_event_handler('view_vars', 'page/elements/comments', 'myplugin_alter_comments_limit');

function myplugin_alter_comments_limit(\Elgg\Event $event) {
   $vars = $event->getValue();

   // only 10 comments per page
   $vars['limit'] = elgg_extract('limit', $vars, 10);

   return $vars;
}
```

### Altering output — `["view", $view_name]` event

Runs on every view's output before `elgg_view()` returns it; params
contain `viewtype`. Return a new string to alter; return nothing to leave
the output unchanged. Example — drop breadcrumbs without links:

```php
function myplugin_alter_breadcrumb($event, $type, $returnvalue, $params) {
   // we only want to alter when viewtype is "default"
   if ($params['viewtype'] !== 'default') {
      return $returnvalue;
   }

   // output nothing if the content doesn't have a single link
   if (false === elgg_strpos($returnvalue, '<a ')) {
      return '';
   }

   // returning nothing means "don't alter the returnvalue"
}
```

- Gotcha: the source's output example uses the legacy four-argument
  handler signature (`$event, $type, $returnvalue, $params`) while the
  input example type-hints `\Elgg\Event` — prefer the object form.

### Replacing output completely

- Pre-set `$vars['__view_output']` in a `view_vars` handler: the value is
  returned as a string, view extensions are not used, and the `view`
  event is not triggered.

```php
function myplugin_no_page_breadcrumbs(\Elgg\Event $event) {
   if (elgg_in_context('pages')) {
      return ['__view_output' => ""];
   }
}
```

- Note: `\Elgg\Values::preventViewOutput` is a ready-made callback for
  this.

## Displaying entities

- `echo elgg_view_entity($entity);` resolves the view chain:
  `type/subtype` → (no subtype: `type/type`) → `type/default`. Blog:
  `object/blog`; user: `user/default`. RSS feeds generally output
  `object/default` in the `rss` viewtype.
- Optional parameters: `$viewtype` (force e.g. an RSS snippet inside an
  HTML page) and `$full_view` (defaults `true`; passed as
  `$vars['full_view']` — usually gates comments and similar info).

## Listing entities

```php
echo elgg_list_entities([
   'type' => 'object',
   'subtype' => 'blog',
]);
```

- Renders the `navigation/pagination` view first, then `elgg_view_entity()`
  per item.
- Gotcha: the URL can set `limit` and `offset` — set them explicitly when
  you need particular values (e.g. non-paginated use).
- RSS autodiscovery: pages using `elgg_list_entities` initialize the
  `["head","page"]` event (used by the header).
- Preloading: entity owners and container owners are preloaded by
  default; disable with `'preload_owners' => false`. See also
  `database.md`.

### No results

- `'no_results'` accepts `true` (default message), a message string, or a
  Closure.
- With `true`, the language key `list:<type>:<subtype>:no_results` is
  checked (e.g. "No blogs found"), falling back to
  `elgg_echo('notfound')`.

### Alternate item view

- `'item_view' => 'group/format/invitationrequest'` customizes the look
  while preserving pagination and the list's HTML markup — e.g.
  invitations are not entities and cannot be listed via `elgg_list_*`;
  the alternative view uses the group entity to render the invitation
  with access/reject buttons.

### Lists as tables (since 2.3)

- `'list_type' => 'table'` plus `'columns'` — an array of `TableColumn`
  objects from the `elgg()->table_columns` service:

```php
'columns' => [
   elgg()->table_columns->icon(),
   elgg()->table_columns->getDisplayName(),
   elgg()->table_columns->time_created(null, [
      'format' => 'friendly',
   ]),
],
```

- See `Elgg\Views\TableColumn\ColumnFactory` for how columns are
  specified and rendered; `elgg()->table_columns` methods can be added or
  overridden (based on views, item properties/methods, or functions).

## Icons

### Generic icons

- `elgg_view_icon($icon_name, $vars)` — `$icon_name` is the FontAwesome
  name without `fa-` (e.g. `user`); renders the `output/icon` view.
- Replace an icon via a `view_vars`, `output/icon` event handler; some
  older Elgg icon names are translated to FontAwesome equivalents for
  backwards compatibility.

### Entity icons

- `elgg_view_entity_icon($entity, $size, $vars)`; sizes: `large`,
  `medium`, `small`, `tiny`, `topbar` (`master` exists but don't use it).
- View chain: `icon/<type>/<subtype>` → `icon/<type>/default` →
  `icon/default` — override the matching view to customize the layout.

```php
// get the user
$user = elgg_get_logged_in_user_entity();

// show the small icon
echo elgg_view_entity_icon($user, 'small');

// don't add the user_hover menu to the icon
echo elgg_view_entity_icon($user, 'small', [
   'use_hover' => false,
]);
```
