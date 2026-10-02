# Elgg Developer Guide: Routing

Delta distillation of <https://learn.elgg.org/en/stable/guides/routing.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/routing.rst`, Elgg ref `7.1`). Records only what counters
stale training-data memory: current API names, signatures, defaults,
deprecations, gotchas. Update in place when the stable manual changes.

Routing maps request URLs to resource views or controllers (bypassing the
actions and simplecache systems). Routes are registered with
`elgg_register_route()` or the `routes` section of `elgg-plugin.php`
(see `plugins.md`).

## URL identifier and segments

- After removing the site URL, the path is split by `/`: the first element
  is the **identifier** (shifted off), the rest are the **segments**.
  `http://example.com/elgg/blog/owner/jane?foo=123` (site URL
  `http://example.com/elgg/`) → identifier `'blog'`, segments
  `['owner', 'jane']`; query-string parameters via `get_input()`.
- Home page special case: empty-string identifier, empty segments array.
- Warning: identifier/segments are potentially dangerous user input; Elgg
  escapes HTML entities in them with `htmlspecialchars`.

## Registering a route

```php
// in your 'init', 'system' handler
elgg_register_route('my_plugin:section', [
   'path' => '/my_plugin/section/{guid}/{subsection?}',
   'resource' => 'my_plugin/section',
   'requirements' => [
      'guid' => '\d+',
      'subsection' => '\w+',
   ],
]);
```

- The matching resource view
  (`views/default/resources/my_plugin/section.php`) receives the URL
  parameters in `$vars` (`elgg_extract('guid', $vars)`, etc.).
- Gotcha: the manual's example omits the comma after the route name
  (`elgg_register_route('my_plugin:section' [`) — a source typo; the call
  needs the comma as above.

## Route names

- Names are unique across all plugins and core; another plugin can
  override a route by registering different parameters to the same name.
- Generate URLs with `elgg_generate_url('my_plugin:section',
  ['guid' => $entity->guid, 'subsection' => 'assets'])`.

Conventions used in core and recommended for plugins:

| Pattern | Maps to | Path requirement |
| :--- | :--- | :--- |
| `view:<type>:<subtype>` | entity profile page | `guid` (or `username` for users) |
| `edit:<type>:<subtype>` | entity edit form | `guid` (or `username`); subresources as suffixes, e.g. `edit:object:blog:images`, keeping at least one default without suffix |
| `add:<type>:<subtype>` | entity add form | as a rule `container_guid` |
| `collection:<type>:<subtype>:<collection_type>` | listing pages | core uses `:all`, `:owner`, `:friends`, `:group` |
| `default:<type>:<subtype>` | default page for a resource (e.g. `/blog`) | Elgg uses the "all" collection for these |

- Omitting `<subtype>` registers a global route for all entities of the
  type; the URL generator tries the subtype-specific name first, then
  falls back to the subtype-less name (user profiles work this way).
- `elgg_generate_entity_url($entity, 'view', 'attachments')` resolves the
  subtype-specific route when one exists (`/blog/view/<guid>/attachments`
  for a blog) and the generic one otherwise (`/attachments/<guid>`).

## Route configuration

- Wildcard segments: `profile/{username}`; optional with `?`:
  `{section?}`; constrained with regex `requirements`; preset via
  `defaults`.
- Requirements Elgg sets by default for named segments: `guid`,
  `group_guid`, `container_guid`, `owner_guid` → `\d+`; `username` →
  `[\p{L}\p{Nd}._-]+`.
- Gotcha: add the flag `'use_logged_in' => true` to have the route params
  `username` and/or `guid` filled with the logged-in user by default.

## Plugin dependent routes

- `'required_plugins' => ['friends']` in the route config allows the route
  only while that plugin is active.

## Route middleware

Middleware prevents access or runs business logic before the route is
rendered; core handlers live in `\Elgg\Router\Middleware`:

| Middleware | Blocks access when... |
| :--- | :--- |
| `Gatekeeper` | user is not authenticated |
| `AdminGatekeeper` | user is not an admin |
| `LoggedOutGatekeeper` | user IS authenticated |
| `AjaxGatekeeper` | request is not xhr |
| `PageOwnerGatekeeper` | there is no page owner entity |
| `GroupPageOwnerGatekeeper` | page owner is not an `ElggGroup` (extends PageOwner) |
| `GroupToolGatekeeper` | configured group tool is not enabled (extends GroupPageOwner) |
| `UserPageOwnerGatekeeper` | page owner is not an `ElggUser` (extends PageOwner) |
| `PageOwnerCanEditGatekeeper` | no page owner or page owner can't edit |
| `GroupPageOwnerCanEditGatekeeper` | page owner is not an `ElggGroup` (extends PageOwnerCanEdit) |
| `UserPageOwnerCanEditGatekeeper` | page owner is not an `ElggUser` (extends PageOwnerCanEdit) |
| `CsrfFirewall` | CSRF tokens missing/incorrect — auto-applied to actions |
| `ActionMiddleware` | — action-related logic, auto-applied to actions |
| `SignedRequestGatekeeper` | URL has been tampered with (sign via `elgg_http_get_signed_url`) |
| `UpgradeGatekeeper` | upgrade URL is secured and invalid |
| `WalledGarden` | site is walled-garden configured and no user is logged in — auto-enabled for ALL routes; disable per route via a route config option (see `walled-garden.md`) |

- `GroupToolGatekeeper` reads the tool from the route option
  `'options' => ['group_tool' => 'news']`; it is then added automatically
  and `GroupPageOwnerGatekeeper` becomes unnecessary.
- Custom middleware: any callable receiving `\Elgg\Request`; throw
  `\Elgg\Exceptions\HttpException` to block access, or return an
  `\Elgg\Http\ResponseBuilder` (e.g. a redirect) to end the routing
  sequence.

## Route controllers

Any callable receiving `\Elgg\Request`; e.g. set
`elgg_set_http_header('Content-Type: application/json')` and return
`elgg_ok_response($data)`.

### Listing controller — `\Elgg\Controllers\GenericContentListing`

Renders a full page (title, breadcrumb, default filter tabs, add-new-
content button if available, content list) from `collection:`/`default:`
route names. Title language key:
`collection:<type>:<subtype>:<collection_type>`; for a `default:` route it
is `collection:<type>:<subtype>:all`.

- Extend with a `list<CollectionType>()` method, camel-cased from the
  route name: `collection:object:my_content:my_listing` →
  `listMyListing()`.
- Helper functions on the controller are extensible for parameter tweaks.
- Route option `'sidebar_view' => 'my_content/sidebar'` is rendered with
  the page.
- Typical middleware pairing: `UserPageOwnerGatekeeper` for `:friends` /
  `:owner`, `GroupPageOwnerGatekeeper` for `:group` (unneeded when
  `group_tool` is set); `:all` and `default:` need none.

### Entity controller — `\Elgg\Controllers\GenericEntity`

Renders a full page (title, breadcrumb, entity view or add/edit form) from
`add:`/`edit:`/`view:` route names. Title: the `add:`/`edit:` language
key, or `$entity->getDisplayName()` for `view:`.

- `add:`: checks the logged-in user may create `<type>:<subtype>` in the
  provided container (pair with `Gatekeeper` + `PageOwnerGatekeeper`).
- `edit:`: checks the user may edit the entity and that it matches the
  route name's `<type>:<subtype>` (pair with `Gatekeeper`).
- `view:`: checks the visitor may view the entity and that it matches the
  route name's `<type>:<subtype>`.

## The `route:rewrite` event

Triggered very early (arguments like the `route` event); modifies the
request URL path relative to the Elgg site — e.g. rewrite `news/*` to
`blog/*`:

```php
function myplugin_rewrite_handler(\Elgg\Event $event) {
   $value = $event->getValue();
   $value['identifier'] = 'blog';
   return $value;
}

elgg_register_event_handler('route:rewrite', 'news', 'myplugin_rewrite_handler');
```

- Warning: register directly in the plugin Bootstrap `boot` function —
  `init` is too late.

## Routing overview

Request → plugins initialized → URL parsed to identifier + segments →
`route:rewrite, <identifier>` event → matching route found → resource view
rendered via `elgg_view_resource('blog/owner', $vars)` → the resource view
reads `$vars['username']` and builds the page with `elgg_view_layout()` /
`elgg_view_page()` → shutdown sequence → fully rendered page.

Elgg's coding standards suggest a particular URL layout, but no syntax is
enforced.
