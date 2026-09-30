# Elgg Developer Guide: Menus

Delta distillation of <https://learn.elgg.org/en/stable/guides/menus.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/menus.rst`, Elgg ref `7.1`). Records only what counters stale
training-data memory: current API names, signatures, defaults, deprecations,
gotchas. Update in place when the stable manual changes.

Every menu requires a name, as does every menu item — required to allow easy
overriding and manipulation, and to provide events for theming.

## Basic usage

- `elgg_register_menu_item()` adds an item to a menu;
  `elgg_unregister_menu_item()` removes one. Call them normally from the
  plugin's init function:

```php
// Add a new menu item to the site main menu
elgg_register_menu_item('site', [
    'name' => 'itemname',
    'text' => 'This is text of the item',
    'href' => '/item/url',
]);

// Remove the "Elgg" logo from the topbar menu
elgg_unregister_menu_item('topbar', 'elgg_logo');
```

## Admin menu

- Register `page` menu items to the admin backend menu; set the item context
  to `admin` so the items only show in the `admin` context. Three default
  sections:
  - `administer` — daily tasks, user management, other actionable tasks
  - `configure` — settings, configuration, utilities that configure stuff
  - `information` — statistics, overview of information or status

## Headers

- For accessibility reasons each menu gets an `aria-label`, defaulting to the
  menu name; translate it via the language key `menu:<menu name>:header`.
- Show menu section headers by setting `show_section_headers` to `true` in
  `elgg_view_menu()`:

```php
echo elgg_view_menu('my_menu', [
    'show_section_headers' => true,
]);
```

- Section headers have the magic language key
  `menu:<menu name>:header:<section name>` for translation.

## Events

Get more control over menus with events and the public methods of the
`ElggMenuItem` class. Three events modify a menu (replace `<menu name>` with
the menu's internal name when registering a handler):

| Event | Use |
| :--- | :--- |
| `'parameters', 'menu:<menu name>'` | add or modify parameters used for menu building (e.g. sorting) |
| `'register', 'menu:<menu name>'` | add or modify items (especially in dynamic menus) |
| `'prepare', 'menu:<menu name>'` | modify the menu structure before it is displayed |

- The third parameter passed into the handler contains all menu items
  registered so far by Elgg core and other enabled plugins; loop through them
  and use the class methods to interact with the item properties.
- Granular versions `menu:<menu name>:<type>:<subtype>` of the `register` and
  `prepare` events apply when the menu is provided an `\ElggEntity` in
  `$params['entity']`, an `\ElggAnnotation` in `$params['annotation']`, or an
  `\ElggRelationship` in `$params['relationship']`.

**Example 1:** change the URL of the "albums" item in the `owner_block` menu:

```php
function my_plugin_init() {
    elgg_register_event_handler('register', 'menu:owner_block', 'my_owner_block_menu_handler');
}

function my_owner_block_menu_handler(\Elgg\Event $event) {
    $owner = $event->getEntityParam();

    // Owner can be either user or group, so take both URLs into consideration
    switch ($owner->getType()) {
        case 'user':
            $url = "album/owner/{$owner->guid}";
            break;
        case 'group':
            $url = "album/group/{$owner->guid}";
            break;
    }

    $items = $event->getValue();
    if ($items->has('albums')) {
        $items->get('albums')->setURL($url);
    }

    return $items;
}
```

**Example 2:** customize the `entity` menu for `ElggBlog` objects — remove
the thumb icon and change the "Edit" text into a custom icon:

```php
function my_plugin_init() {
    elgg_register_event_handler('register', 'menu:entity', 'my_entity_menu_handler');
}

function my_entity_menu_handler(\Elgg\Event $event) {
    $entity = $event->getEntityParam();

    // Only modify ElggBlog objects; return immediately for anything else
    if (!$entity instanceof ElggBlog) {
        return;
    }

    $items = $event->getValue();

    $items->remove('likes');

    if ($items->has('edit')) {
        $items->get('edit')->setText('Modify');
        $items->get('edit')->icon = 'pencil';
    }

    return $items;
}
```

## Creating a new menu

- Create your own menu with `elgg_view_menu()`, called from the view where
  the menu should be displayed:

```php
// in a resource view
echo elgg_view_menu('my_menu', ['sort_by' => 'text']);
```

- Add new items from the plugin init:

```php
elgg_register_menu_item('my_menu', [
    'name' => 'my_page',
    'href' => 'path/to/my_page',
    'text' => elgg_echo('my_plugin:my_page'),
]);
```

- The menu can then be modified with the events `'register', 'menu:my_menu'`
  and `'prepare', 'menu:my_menu'`.

## Child dropdown menus

- Configure child menus with the `child_menu` factory option on the parent
  item. The options array accepts `display` (`dropdown` or `toggle`); all
  other key/value pairs are passed as attributes to the `ul` element:

```php
// Parent item with a dropdown submenu
elgg_register_menu_item('my_menu', [
    'name' => 'parent_item',
    'href' => false,
    'text' => 'Show dropdown menu',
    'child_menu' => [
        'display' => 'dropdown',
        'class' => 'elgg-additional-child-menu-class',
        'data-position' => json_encode([
            'at' => 'right bottom',
            'my' => 'right top',
            'collision' => 'fit fit',
        ]),
        'data-foo' => 'bar',
        'id' => 'dropdown-menu-id',
    ],
]);

// Parent item with a hidden submenu toggled when the item is clicked
elgg_register_menu_item('my_menu', [
    'name' => 'parent_item',
    'href' => false,
    'text' => 'Show submenu',
    'child_menu' => [
        'display' => 'dropdown',
        'class' => 'elgg-additional-submenu-class',
        'data-toggle-duration' => 'medium',
        'data-foo' => 'bar2',
        'id' => 'submenu-id',
    ],
]);
```

## Theming

- Menu name, section names, and item names are embedded into the HTML as CSS
  classes (normalized to contain only hyphens, rather than underscores or
  colons) — slightly larger markup, but high styling control for themers.
- Output of the `foo` menu with sections `alt` and `default` containing items
  `baz` and `bar` respectively:

```html
<ul class="elgg-menu elgg-menu-foo elgg-menu-foo-alt">
    <li class="elgg-menu-item elgg-menu-item-baz"></li>
</ul>
<ul class="elgg-menu elgg-menu-foo elgg-menu-foo-default">
    <li class="elgg-menu-item elgg-menu-item-bar"></li>
</ul>
```

## Toggling menu items

- For opposite action pairs (like/unlike, friend/unfriend, ban/unban, …),
  register both items and point each at its opposite via `data-toggle`; an
  Ajax call is made using the item's `href`:

```php
elgg_register_menu_item('my_menu', [
    'name' => 'like',
    'data-toggle' => 'unlike',
    'href' => 'action/like',
    'text' => elgg_echo('like'),
]);

elgg_register_menu_item('my_menu', [
    'name' => 'unlike',
    'data-toggle' => 'like',
    'href' => 'action/unlike',
    'text' => elgg_echo('unlike'),
]);
```

- Gotcha: the items are toggled optimistically — before the actions finish;
  if an action fails, the items are toggled back.

## JavaScript

- Bind client-side events to menu items by placing the JavaScript into a
  module and declaring it during registration via `deps`:

```php
elgg_register_menu_item('my_menu', [
    'name' => 'hide_on_click',
    'href' => false,
    'text' => elgg_echo('hide:on:click'),
    'item_class' => '.hide-on-click',
    'deps' => ['navigation/menu/item/hide_on_click'],
]);
```

```js
// in navigation/menu/item/hide_on_click.mjs
import 'jquery';

$(document).on('click', '.hide-on-click', function(e) {
    e.preventDefault();
    $(this).hide();
});
```
