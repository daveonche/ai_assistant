# Elgg Developer Guide: Widgets

Delta distillation of <https://learn.elgg.org/en/stable/guides/widgets.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/widgets.rst`, Elgg ref `7.1`). Records only what counters
stale training-data memory: current API names, signatures, defaults,
deprecations, gotchas. Update in place when the stable manual changes.

Widgets are content areas users can drag around their page to customize
the layout; the owner can show more/less content and determine who sees
the widget. Core ships plugins that customize the profile page and the
dashboard via widgets.

## Structure

- A widget needs two views: `widgets/<id>/content` (all content output
  within the widget) and `widgets/<id>/edit` (extra edit functions).
- You do not need to add an access level input — it comes as part of the
  widget framework.
- Gotcha (note): HTML checkboxes to set widget flags are problematic — an
  unchecked checkbox is omitted from the form submission, so flags can be
  set but never cleared. The `input/checkboxes` view does not work
  properly in a widget's edit panel.

## Register the widget

Easiest: the `widgets` section of `elgg-plugin.php` (see `plugins.md`):

```php
return [
    'widgets' => [
        'filerepo' => [
            'context' => ['profile'],
        ],
    ]
];
```

Alternatively call `elgg_register_widget_type()` from the plugin's
`init()`:

```php
elgg_register_widget_type([
    'id' => 'filerepo',
    'name' => elgg_echo('widgets:filerepo:name'),
    'description' => elgg_echo('widgets:filerepo:description'),
    'context' => ['profile'],
]);
```

- Note: the only required attribute is the `id`.

## Multiple widgets per plugin

- Register as many widget ids as needed; each id needs its own views
  directory `views/default/widgets/<id>/` with `edit.php` and
  `content.php`, and each registration can target different contexts
  (`['profile']`, `['dashboard']`, `['profile', 'dashboard']`).

## Magic widget name and description

- Omit `name`/`description` and provide translations instead:
  `widgets:<widget_id>:name` and `widgets:<widget_id>:description`. With
  those keys in a translation file, registration is one line:

```php
elgg_register_widget_type(['id' => 'filerepo']);
```

## Restricting where widgets can be used

- `'context' => ['profile', 'dashboard', 'other_context']` — the contexts
  the widget can be used in.

## Multiple widgets on the same page

- Default: only one widget of the same type per page. Lift it with:

```php
elgg_register_widget_type([
    'id' => 'filerepo',
    'multiple' => true,
]);
```

## Registering widgets in an event

For conditional registration, use the `handlers, widgets` event:

```php
function my_plugin_init() {
    elgg_register_event_handler('handlers', 'widgets', 'my_plugin_conditional_widgets_event');
}

function my_plugin_conditional_widgets_event(\Elgg\Event $event) {
    if (!elgg_is_active_plugin('file')) {
        return;
    }

    $return = $event->getValue();

    $return[] = \Elgg\WidgetDefinition::factory([
        'id' => 'filerepo',
    ]);

    return $return;
}
```

- Returning nothing leaves the widget list unchanged.

## Modifying an existing widget registration

- Re-register the widget with `elgg_register_widget_type()` — it
  overrides an already existing widget definition.
- For more control, use the `handlers, widgets` event and mutate the
  definitions in the value array:

```php
function my_plugin_change_widget_definition_event(\Elgg\Event $event) {
    $return = $event->getValue();

    foreach ($return as $key => $widget) {
        if ($widget->id === 'filerepo') {
            $return[$key]->multiple = false;
        }
    }

    return $return;
}
```

## Default widgets

If your plugin uses the widget canvas, register default widget support
with Elgg core and it handles everything else.

1. Register for the `get_list, default_widgets` event and push an array
   defining the widgets page and when defaults are created:

```php
elgg_register_event_handler('get_list', 'default_widgets', 'my_plugin_default_widgets_event');

function my_plugin_default_widgets_event(\Elgg\Event $event) {
    $return = $event->getValue();

    $return[] = [
        'name' => elgg_echo('my_plugin'),
        'widget_context' => 'my_plugin',
        'widget_columns' => 3,

        'event_name' => 'create',
        'event_type' => 'user',
        'entity_type' => 'user',
        'entity_subtype' => ELGG_ENTITIES_ANY_VALUE,
    ];

    return $return;
}
```

Required keys:

| Key | Meaning |
| :--- | :--- |
| `name` | name of the widgets page; displayed on the tab in the admin interface |
| `widget_context` | context the widgets page is called from (defaults to your plugin's id when not explicitly set) |
| `widget_columns` | how many columns the widgets page uses |
| `event_name` | Elgg event name to create new widgets for (usually `create`) |
| `event_type` | Elgg event type to create new widgets for |
| `entity_type` | entity type to create new widgets for |
| `entity_subtype` | entity subtype, or `ELGG_ENTITIES_ANY_VALUE` for all types |

2. Register the creation handler:

```php
elgg_register_event_handler('create:after', 'object', 'Elgg\Widgets\CreateDefaultWidgetsHandler');
```

When an object triggers an event matching the configured `event_name`,
`event_type`, `entity_type`, and `entity_subtype`, Elgg core looks for
default widgets matching the `widget_context` and copies them to the
object's `owner_guid` and `container_guid` — all widget settings are
copied too.
