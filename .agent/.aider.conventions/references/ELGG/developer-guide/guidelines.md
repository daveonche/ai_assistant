# Elgg Developer Guide: Plugin Coding Guidelines

Delta distillation of <https://learn.elgg.org/en/stable/guides/guidelines.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/guidelines.rst`, Elgg ref `7.1`). Records only what counters stale
training-data memory: current API names, signatures, defaults, deprecations,
gotchas. Update in place when the stable manual changes.

In addition to the Elgg Coding Standards, these are the plugin guidelines; core
plugins are being updated to this format, and all plugin authors should follow
them. Follow the plugin skeleton guide for your plugin's layout, and never
modify core (see `dont-modify-core.md`).

## Standardized routing with page handlers

- Example plugin: Bookmarks. Page handlers accept these standard URLs:

| Purpose | URL |
| :--- | :--- |
| All | `page_handler/all` |
| User | `page_handler/owner/<username>` |
| User friends' | `page_handler/friends/<username>` |
| Single entity | `page_handler/view/<guid>/<title>` |
| Add | `page_handler/add/<container_guid>` |
| Edit | `page_handler/edit/<guid>` |
| Group list | `page_handler/group/<guid>/owner` |

- Include page handler scripts from the page handler; almost every page
  handler should have one (e.g. `bookmarks/all` =>
  `mod/bookmarks/views/default/resources/bookmarks/all.php`).
- Pass arguments like entity GUIDs to the resource view via `$vars` in
  `elgg_view_resource()`.
- Call `elgg_gatekeeper()` and `elgg_admin_gatekeeper()` in the page handler
  function if required.
- Group URLs should use views like `resources/groups/*.php` to render pages.
- Page handlers should not contain HTML.

## Standardized page handlers and scripts

- Store page functionality in
  `mod/<plugin>/views/default/resources/<page_handler>/<page_name>.php` and
  render it with `elgg_view_resource('<page_handler>/<page_name>')`.
- Use the default page layout in page handler scripts:
  `$content = elgg_view_layout('default', $options);`
- Page handler scripts should not contain HTML.
- Call `elgg_push_entity_breadcrumbs()` or
  `elgg_push_collection_breadcrumbs()` in the page handler scripts.
- With standardized URLs there is no need to worry about setting the page
  owner.
- For group content, check the `container_guid` via
  `elgg_get_page_owner_entity()`.

## The `object/<subtype>` view

- Provide views for both `$vars['full_view'] == true` and
  `$vars['full_view'] == false`.
- Check for the object in `$vars['entity']`; use `elgg_instance_of()` to make
  sure it is the expected type, and return `true` to short-circuit the view if
  the entity is missing or wrong.
- Use the list body and list metadata views to help format; these views should
  contain almost no markup.

## Actions

- Namespace action files and action names (e.g. `mod/blog/actions/blog/save.php`
  => `action/blog/save`) and use these action URLs:

| Purpose | URL |
| :--- | :--- |
| Add | `action/plugin/save` |
| Edit | `action/plugin/save` |
| Delete | `action/plugin/delete` |

- Make the delete action accept `action/<handler>/delete?guid=<guid>` so the
  metadata entity menu has the correct URL by default.
- Actions are transient states that perform an action such as updating the
  database or sending a notification; used correctly they provide a level of
  access control and protect against CSRF attacks. Actions require action
  (CSRF) tokens on GET/POST submission, added automatically by
  `elgg_view_form()` and by the `is_action` argument of the `output/url` view.

### Action best practices

- Action files are included within Elgg's action system; like views, they are
  not regular scripts executable by users. Do not boot Elgg core in the file
  and direct users to load it directly.
- Actions are time-sensitive and unsuitable for links in emails or other
  delayed notifications (e.g. group invitations). The clean way: create a page
  handler for invitations and email that link; the page handler then creates
  the action links for the user to join or ignore the request.
- Consider that actions may be submitted via XHR requests, not just links or
  form submissions.

## Directly calling a file

- Don't do it. With the exception of 3rd-party application integration, there
  is no reason to directly call a file in the mods directory.

## Recommended (not yet official guidelines)

Good ideas that keep a plugin consistent with Elgg core:

- Update the widget views (see the blog or file widgets).
- Update the group profile 'widget' using the blog or file plugins as
  examples.
- Update the forms:
  - Move form bodies to `/forms/<handler>/<action>` to use `elgg_view_form()`.
  - Use input views in form bodies rather than HTML.
  - Add a function that prepares the form (see `mod/file/lib/file.php`).
  - Integrate sticky forms (see the file plugin's upload action and form
    prepare function).
- Clean up CSS/HTML: you should be able to remove almost all CSS (look for
  patterns that can be moved into core if you need CSS).
- Use hyphens rather than underscores in classes/ids.
- Do not use the `bundled` category with your plugins; that is for plugins
  distributed with Elgg.
- Don't use `register_shutdown_function` — you may not have access to certain
  Elgg parts anymore (e.g. the database). Instead use the `shutdown` `system`
  event.
