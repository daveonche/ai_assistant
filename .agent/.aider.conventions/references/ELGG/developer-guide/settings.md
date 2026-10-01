# Elgg Developer Guide: Settings

Delta distillation of <https://learn.elgg.org/en/stable/guides/settings.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/settings.rst`, Elgg ref `7.1`). Records only what counters
stale training-data memory: current API names, signatures, defaults,
deprecations, gotchas. Update in place when the stable manual changes.

Plugins can expose settings at three levels, each with its own view file
and input-name format: site-wide plugin settings (admin panel), per-user
settings (user settings page), and per-group settings (group creation and
edit). Values are read and written with the `elgg_get_plugin_*` getters
and `setSetting()`/`setPluginSetting()` methods; defaults come from getter
arguments or the `elgg-plugin.php` config (see `plugins.md`).

## Plugin settings (admin panel)

- Create the settings view file `/plugins/your_plugin/settings.php` and
  build the form with `elgg_view_field()`; the plugin entity is passed to
  the view as `$vars['entity']`.
- Name inputs `params[<setting>]` — the example's `params[limit]` pairs
  with `'value' => $vars['entity']->limit`:

```php
echo elgg_view_field([
   '#type' => 'select',
   '#label' => elgg_echo('myplugin:settings:limit'),
   'name' => 'params[limit]',
   'value' => $vars['entity']->limit,
   'options' => [5,8,12,15],
]);
```

- No save button or form wrapper needed — the framework handles them.
- Gotcha: form components that send no value when "off" cannot be used —
  this includes radio inputs and check boxes.
- If a settings change requires a cache flush, add a hidden input named
  `flush_cache` with value `1`:

```php
elgg_view_field([
   '#type' => 'hidden',
   'name' => 'flush_cache',
   'value' => 1,
]);
```

## User settings

- Same pattern as plugin settings, but the file is `usersettings` instead
  of `settings`: the user edit view lives at
  `plugins/<your_plugin>/usersettings.php`.
- The usersettings form title defaults to the plugin name; change it by
  adding a translation for `<plugin_id>:usersettings:title`.

## Group settings

- Extend the view `groups/edit/settings` to show the settings; they are
  shown during group creation and edit.
- To be saved correctly, input names must use the format
  `settings[<plugin id>][<setting name>]`.

## Retrieving settings in code

```php
$setting = elgg_get_plugin_setting($name, $plugin_id);
```

User settings:

```php
$user_setting = elgg_get_plugin_user_setting($name, $user_guid, $plugin_id);

// or
$user = get_user($user_guid);
$user_setting = $user->getPluginSetting($plugin_id, $name);
```

- `$name`: the setting to retrieve; `$user_guid`: the user to retrieve the
  settings for (defaults to the currently logged-in user); `$plugin_name`:
  the name of the plugin (detected if run from within a plugin).
- Gotchas in the source's parameter list: it names the third parameter
  `$plugin_name` while the code signatures use `$plugin_id`, and it
  describes `$name` as "the value you want to retrieve" — it is the
  setting name.

Group settings:

```php
$group = get_entity($group_guid);
$value = $group->getPluginSetting('<plugin id>', '<setting name>');
```

## Setting values in code

```php
$plugin = elgg_get_plugin_from_id($plugin_id);
$plugin->setSetting($name, $value);
```

User settings:

```php
$user = elgg_get_logged_in_user_entity();
$user->setPluginSetting($plugin_id, $name, $value);
```

Group settings:

```php
$group = get_entity($group_guid);
$group->setPluginSetting($plugin_id, $name, $value);
```

- Warning (from the source): the `$plugin_id` needs to be provided when
  setting plugin (user) settings.

## Default plugin (group|user) settings

When no setting is stored in the database, pass a default to the getter
functions:

```php
$user_setting = elgg_get_plugin_user_setting($name, $user_guid, $plugin_id, $default);

$plugin_setting = elgg_get_plugin_setting($name, $plugin_id, $default);

$group_setting = $group->getPluginSetting($plugin_id, $name, $default);
```

Alternatively, provide default plugin and user settings in the
`elgg-plugin.php` file:

```php
<?php

return [
   'settings' => [
      'key' => 'value',
   ],
   'user_settings' => [
      'key' => 'value',
   ],
];
```

- Note: group settings don't have a default value available in the
  `elgg-plugin.php` file.
