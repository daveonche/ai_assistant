# Elgg Developer Guide: Group Tools

Delta distillation of <https://learn.elgg.org/en/stable/guides/group-tools.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/group-tools.rst`, Elgg ref `7.1`). Records only what counters stale
training-data memory: current API names, signatures, defaults, deprecations,
gotchas. Update in place when the stable manual changes.

## Registering a tool

- Group tools let group administrators enable/disable per-group features; the
  tools themselves are provided by plugins (e.g. blog, file). Register via the
  `group_tools` service:

```php
elgg()->group_tools->register('my-tool', [
    'default_on' => false, // default is true
    'label' => elgg_echo('my-tool:checkbox:label'),
    'priority' => 300, // display this earlier than other modules/tools
]);
```

| Option | Meaning |
| :--- | :--- |
| `default_on` | initial tool state; defaults to `true` |
| `label` | checkbox label on the group edit form |
| `priority` | ordering among tools/modules; e.g. `300` displays earlier |

- A registered tool gets a toggle on the group edit form and can have a
  profile view module associated with it.

## Profile modules

- To give a tool a profile module, add the view
  `groups/profile/module/<tool_name>` — it is only called when the tool is
  enabled for that group.
- To simply list content in the group, use the generic
  `groups/profile/module` view with:

| Param | Meaning |
| :--- | :--- |
| `entity_type` | with `entity_subtype`, generates the module content |
| `entity_subtype` | with `entity_type`, generates the module content |
| `no_results` | custom no-results-found text |

- Generated automatically: `title` from the language key
  `collection:<entity_type>:<entity_subtype>:group`; `content` via
  `elgg_list_entities()`; `all_link` from route
  `collection:<entity_type>:<entity_subtype>:group`; `add_link` from route
  `add:<entity_type>:<entity_subtype>:group` with a permissions check for the
  type/subtype.

```php
// file: groups/profile/module/my-tool.php

// list some content (eg. files) in the group
$params = [
    'entity_type' => 'object',
    'entity_subtype' => 'file',
    'no_results' => elgg_echo('file:none'),
];
$params = $params + $vars;

echo elgg_view('groups/profile/module', $params);
```

- Alternatively, generate your own title and content:

```php
echo elgg_view('groups/profile/module', [
    'title' => elgg_echo('my-tool'),
    'content' => 'Hello, world!',
]);
```

## Enabling, disabling and checking tools

```php
$group = get_entity($group_guid);

// enables the file tool for the group
$group->enableTool('file');

// disables the file tool for the group
$group->disableTool('file');
```

- Feature code can branch on `\ElggGroup::isToolEnabled($tool_option)`.
- To prevent access to a group page based on an enabled tool, use the
  gatekeeper (see the authentication gatekeepers docs):

```php
elgg_group_tool_gatekeeper('file', $group);
```

- The configured group tool options for a specific group:
  `elgg()->group_tools->group($group)`.
