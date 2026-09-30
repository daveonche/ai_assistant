# Elgg Developer Guide: JavaScript

Delta distillation of <https://learn.elgg.org/en/stable/guides/javascript.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/javascript.rst`, Elgg ref `7.1`). Records only what counters stale
training-data memory: current API names, signatures, defaults, deprecations,
gotchas. Update in place when the stable manual changes.

## Modules: load, define, register

- Write JavaScript as browser-native ECMAScript modules.
- Load an existing module in the current page from PHP — this asynchronously
  loads the module, its dependencies, and executes its code:

```php
elgg_import_esm('myplugin/say_hello');
```

- Files with the `.mjs` extension are automatically added to the importmap and
  importable by view name: `views/default/myplugin/say_hello.mjs` is
  importable as `myplugin/say_hello` — from PHP via
  `elgg_import_esm('myplugin/say_hello')`, from JS via
  `import 'myplugin/say_hello';`, or on demand via `import()`.
- Modules without an `.mjs` extension (e.g. from a dependency) must be
  registered to the importmap first; afterwards they import under their
  registered name:

```php
elgg_register_esm('myplugin/say_hello', elgg_get_simplecache_url('external/dependency/modulename.js'));
```

## Passing settings to modules: `elgg.data`

- The `elgg` module exposes an `elgg.data` object populated from server-side
  events (the documented one: **`elgg.data, page`**, which filters an
  associative array of data passed to the client):

```php
function myplugin_config_page(\Elgg\Event $event) {
    $value = $event->getValue();
    $value['myplugin']['api'] = elgg_get_site_url() . 'myplugin-api';
    $value['myplugin']['key'] = 'none';

    $user = elgg_get_logged_in_user_entity();
    if ($user) {
        $value['myplugin']['key'] = $user->myplugin_api_key;
    }

    return $value;
}

elgg_register_event_handler('elgg.data', 'page', 'myplugin_config_page');
```

```js
define(['elgg'], function(elgg) {
    var api = elgg.data.myplugin.api;
    var key = elgg.data.myplugin.key; // "none" or a user's key
});
```

## Mapping module names to files

- For an AMD script outside your views, configure its path in the `views`
  section of the plugin root's `elgg-plugin.php`:

```php
<?php // elgg-plugin.php
return [
    'views' => [
        'default' => [
            'underscore.js' => 'vendor/npm-asset/underscore/underscore.min.js',
        ],
    ],
];
```

- If the script was copied into the plugin instead of managed by Composer,
  point at it directly, e.g. `__DIR__ . '/node_modules/underscore/underscore.min.js'`.
- Elgg then loads the file whenever the "underscore" module is requested.

## Module `elgg`

- `elgg.normalize_url('/blog')` — normalize a URL relative to the Elgg root
  (e.g. `"http://localhost/elgg/blog"`).
- `elgg.forward('/blog')` — redirect to a new page; normalizes the URL
  automatically.
- `elgg.parse_url('http://community.elgg.org/file.php?arg=val#fragment')` —
  returns `{fragment, host, path, query}`.
- `elgg.get_logged_in_user_guid()`, `elgg.is_logged_in()`,
  `elgg.is_admin_logged_in()`.
- Config values: `elgg.config.wwwroot` (site root), `elgg.config.language`
  (default site language), `elgg.config.release` (Elgg release, X.Y.Z).

## Module `elgg/Ajax`

- See `ajax.md`.

## Module `elgg/hooks`

- Lets plugins interact with each other:

```js
hooks.register('my_plugin:filter', 'value', handler, priority);
var result = hooks.trigger('my_plugin:filter', 'value', {}, 'default');
```

## Module `elgg/i18n`

- `i18n.echo('example:text', ['arg1']);`

## Module `elgg/system_messages`

- `system_messages.success('Your success message')`,
  `system_messages.error('Your error message')`, `system_messages.clear()`.

## Module `elgg/security`

- Adds a security token to an object, URL, or query string:

```js
security.addToken({'other': 'data'});
// {__elgg_token: "1468dc...", __elgg_ts: 1328143779, other: "data"}

security.addToken("action/add");
// "action/add?__elgg_ts=...&__elgg_token=..."

security.addToken("?arg=val");
// "?arg=val&__elgg_ts=...&__elgg_token=..."
```

## Module `elgg/spinner`

- Loading indicator fixed to the top of the window: `spinner.start()` /
  `spinner.stop()`. Gives feedback on longer-running tasks; Ajax features from
  `elgg/Ajax` use it by default.

## Module `elgg/popup`

- Displays an overlay positioned relative to its anchor (trigger).
- Auto-loaded for content drawn with `output/url` using `class: 'elgg-popup'`
  and a target defined via `href` (or `data-href`); positioning via the
  trigger's `data-position` attribute (JSON options for `$.position()`, see
  <http://api.jqueryui.com/position/>):

```php
echo elgg_format_element('div', [
   'class' => 'elgg-module-popup hidden',
   'id' => 'popup-module',
], 'Popup module content');

echo elgg_view('output/url', [
   'href' => '#popup-module',
   'text' => 'Show popup',
   'class' => 'elgg-popup',
]);

// Button with custom positioning
elgg_import_esm('elgg/popup');
echo elgg_format_element('button', [
   'class' => 'elgg-button elgg-button-submit elgg-popup',
   'text' => 'Show popup',
   'data-href' => '#popup-module',
   'data-position' => json_encode([
      'my' => 'center bottom',
      'at' => 'center top',
   ]),
]);
```

- Programmatic open/close: `popup.open($trigger, $target, {'collision': 'fit none'})`
  and `popup.close`.
- The `getOptions, ui.popup` hook manipulates the position before opening;
  jQuery `open`/`close` events fire after open/close (e.g. lazy-load content
  via `elgg/Ajax` in the `open` handler, toggling the trigger).
- Open popups expose via `$.data()`: `trigger` (the jQuery trigger element)
  and `position` (the object passed to `$.position()`).
- Gotcha: by default the target element is appended to `$('body')`, altering
  DOM hierarchy; add `.elgg-popup-inline` to the trigger to preserve the DOM
  position.

## Module `elgg/lightbox`

- Colorbox-based (<http://www.jacklmoore.com/colorbox> for options). Bind
  anchors with classes: `elgg-lightbox` (HTML resource), `elgg-lightbox-photo`
  (image — use it to avoid displaying raw image bytes instead of an `img`
  tag), `elgg-lightbox-inline` (inline HTML element), `elgg-lightbox-iframe`
  (resource in an `iframe`).
- Per-element options: `data-colorbox-opts` attribute holding a JSON object.
- The `"getOptions", "ui.lightbox"` hook filters options passed to
  `$.colorbox()` whenever a lightbox is opened.
- Programmatic: `lightbox.open({...})`, `lightbox.resize({width: '300px'})`.
- Gallery sets (via `rel` attribute) need direct binding:
  `lightbox.default.bind('a[rel="my-gallery"]', options, false)` — the third
  argument binds without proxies, and direct binding ignores
  `data-colorbox-opts` on all elements in the set.
- `ajaxLoadWithDependencies: true` has the `elgg/Ajax` module load the content
  and its JS dependencies automatically.

## Module `elgg/ckeditor`

- WYSIWYG editor for textareas; requires the `ckeditor` plugin; automatically
  attached to all `.elgg-input-longtext` instances.

```js
import('elgg/ckeditor').then((elggCKEditor) => {
   elggCKEditor.default.bind('#my-text-area');
   elggCKEditor.default.toggle('#my-text-area');
   elggCKEditor.default.focus('#my-text-area'); // or $('#my-text-area').trigger('focus')
   elggCKEditor.default.reset('#my-text-area'); // or $('#my-text-area').trigger('reset')
});
```

## Inline tabs component

- Fires an `open` event whenever a tab opens and, for ajax tabs, once it has
  finished loading.

## Traditional scripts

- There is no Elgg API for loading non-module scripts; register them in a
  `head, page` event handler to add elements to the head links:

```php
elgg_register_event_handler('head', 'page', $callback);
```

## JS hooks system

- Mirrors the PHP events engine: `hooks.register('name', 'type', {handler},
  {priority});` — multiple handlers can register for the same hook.
- Handlers receive 4 arguments: `hook`, `type`, `params`, `value`; `value` is
  passed through each handler — callbacks react or alter data.
- Trigger custom hooks: `hooks.trigger('name', 'type', {params}, "value");`
- Available hooks:

| Hook | Purpose |
| :--- | :--- |
| `init, system` | fired after Elgg's JS is loaded and all plugin boot modules initialized; register init functions here |
| `getOptions, ui.popup` | customized placement options for popup displays (`rel="popup"`) |
| `getOptions, ui.lightbox` | filters options passed to `$.colorbox()` |
| `config, ckeditor` | filters the CKEditor config object; register in a plugin boot module; defaults in module `elgg/ckeditor/config` |
| `prepare, ckeditor` | decorates the `CKEDITOR` global; register CKEditor plugins and event bindings |
| `ajax_request_data, *` | filters request data sent by `elgg/Ajax` (see `ajax.md`); the hook must check whether the data is a plain object or a `FormData` instance to piggyback values using the correct API |
| `ajax_response_data, *` | filters response data returned to `elgg/Ajax` users (see `ajax.md`) |

## Third-party assets

- Manage third-party scripts and styles with Composer; Elgg's composer.json
  installs from the NPM/Yarn package repositories via Asset Packagist
  (<https://asset-packagist.org>, a repository managed by the Yii community).
- Example: `composer require npm-asset/jquery:~2.0`
- Starter projects pulling Elgg in as a Composer dependency add this to their
  own `composer.json`:

```json
{
    "repositories": [
        {
            "type": "composer",
            "url": "https://asset-packagist.org"
        }
    ],
    "config": {
        "fxp-asset": {
            "enabled": false
        }
    }
}
```

- Alternative: install `fxp/composer-asset-plugin` globally for the same
  result, but installation and update take much longer.
