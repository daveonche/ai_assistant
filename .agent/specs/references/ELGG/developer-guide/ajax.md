# Elgg Developer Guide: Ajax

Delta distillation of <https://learn.elgg.org/en/stable/guides/ajax.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/ajax.rst`, Elgg ref `7.1`). Records only what counters stale
training-data memory: current API names, signatures, defaults, deprecations,
gotchas. Update in place when the stable manual changes.

## Module and methods

- AMD module `elgg/Ajax` (since Elgg 2.1): instantiate with
  `var ajax = new Ajax();` after `require('elgg/Ajax')`.
- Methods: `ajax.action('<action_name>', options)`,
  `ajax.path('<url_path>', options)`, `ajax.view('<view_name>', options)`,
  `ajax.form('<action_name>', options)`, `ajax.forward('<path>')`, plus the
  form helper `ajax.objectify($form)`.
- Every method returns a `jqXHR` usable as a Promise (`.done()`/`.fail()`).
- All methods accept a query string in the first argument; it is passed to
  the fetch URL but does not appear in hook types.
- An absolute URL can be given in place of the action or path name.

## Request/response lifecycle

1. Client-side, the `data` option (if given as an object) is filtered by
   the hook `ajax_request_data`.
2. The request is made to the server (render a view or form, call an
   action, or load a path).
3. The method returns a `jqXHR` object.
4. Server-echoed content is turned into an object.
5. The object is filtered by the server-side event `ajax_results`.
6. The object is used to create the HTTP response.
7. Client-side, the response data is filtered by the hook
   `ajax_response_data`.
8. The `jqXHR` promise is resolved and any `success` callbacks are called.

## Options and defaults

- `elgg/spinner` is used automatically during requests.
- Default HTTP method: `POST` for actions, otherwise `GET`; override with
  `options.method`. A non-empty `options.data` forces `POST`.
- Client caching: set `options.method` to `"GET"` and
  `options.data.elgg_response_ttl` to the max-age in seconds.
- `options.data.elgg_fetch_messages = 0` saves system messages for the next
  page load (use when redirecting based on the response).
- `options.data.elgg_fetch_deps = 0` stops the client from requiring ES
  modules pulled in server-side with `elgg_import_esm()`.
- Messages from `elgg_register_success_message()` /
  `elgg_register_error_message()` are collected and displayed client-side;
  a default error handler shows a generic message when output fails.
- PHP exceptions or denied resources return HTTP error codes, which trigger
  the client-side error handler.

## Actions

- Server side: `elgg_ajax_gatekeeper();` at the top of the action;
  `elgg_register_success_message('...')` renders client-side;
  `echo json_encode([...])` supplies the response value.
- Hook type `action:<action_name>` — three hooks fire: client
  `ajax_request_data` (filters request data before sending), server
  `ajax_results` (filters the response after the action runs), client
  `ajax_response_data` (filters response data before the caller receives
  it).
- CSRF tokens are added to the request data; the default method is `POST`.
- Gotcha: when setting `data` from a form, use `ajax.objectify($form)`
  instead of `$form.serialize()` — only objectified data triggers the
  `ajax_request_data` hooks so other plugins can piggyback.

## Paths

- Register the route in `elgg-plugin.php` (`'routes'` section); the
  resource view calls `elgg_ajax_gatekeeper()`, echoes JSON, and ends with
  `return true;`.
- Hook type `path:<url_path>`.
- If the page handler echoes a regular web page, `output` is a string
  containing the HTML.

## Views

- PHP views must be registered first, during boot:
  `elgg_register_ajax_view('myplugin/get_link');`.
- Hook type `view:<view_name>`; `output` is the rendered view as a string.
- Request data are injected into `$vars` in the view; a `guid` in the
  request data sets `$vars['entity']` to the corresponding entity, or
  `false` if it cannot be loaded.
- Warning: in ajax views and forms, `$vars` can be populated by client
  input — filtered like `get_input()`, but the type may not be what you
  expect and keys may be unexpected.

## Forms

- Register the form view with
  `elgg_register_ajax_view('forms/myplugin/add');` and fetch it with
  `ajax.form('myplugin/add')`.
- Hook type `form:<action_name>`; `output` is the rendered form view as a
  string; same `$vars` / `guid` injection as views.
- Only the request data reach the form view (the third parameter accepted
  by `elgg_view_form()`). To pass form-element attributes (normally the
  second `elgg_view_form()` parameter), use the server-side event
  `view_vars, input/form`.
- Submit a form over Ajax by rendering it with
  `echo elgg_view_form('login', ['ajax' => true]);`.

## Redirects

- `ajax.forward('/activity')` starts a spinner and redirects the user to
  the new destination.

## Piggybacking on requests

- Client-side hook `Ajax.REQUEST_DATA_HOOK` (e.g. type `view:foo`): handler
  signature `(name, type, params, data)`; append or filter `data` and
  return it — added keys are read server-side with `get_input()`.
- If data was given as a string (e.g. `$form.serialize()`), the request
  hooks are not triggered.
- Forms are objectified as `FormData`, and the request content type is
  determined accordingly.

## Piggybacking on responses

- Server-side event `ajax_results` (e.g. type `view:foo`), registered with
  `elgg_register_event_handler()`: the handler receives an `\Elgg\Event`;
  mutate the returned value (`$data->value`) and add metadata keys (e.g.
  `$data->myplugin_alert`), then return it.
- Client-side hook `Ajax.RESPONSE_DATA_HOOK`: same handler signature; only
  `data.value` reaches the `success` function or the `Deferred` interface —
  the rest is metadata.
- Elgg itself uses these same hooks to deliver system messages over
  `elgg/Ajax` responses.

## Errors

- HTTP 200 with status `0`: success; no `elgg_register_error_message()`
  calls were made server-side.
- HTTP 200 with status `-1`: `elgg_register_error_message()` was called
  server-side.
- HTTP 4xx/5xx (e.g. stale tokens, server exception): the `done` callbacks
  are not called.
- Differentiate behaviour with `.done()` and `.fail()` callbacks.

## ES modules

- Every Ajax response lists ES modules required server-side with
  `elgg_import_esm()`; they load asynchronously when the response data is
  unwrapped.
- Plugins must not expect these modules to be loaded inside `.done()` /
  `.then()` handlers — `import` any modules they depend on.
- Modules must not expect the DOM to have been altered by an Ajax request
  when they load: delegate DOM events and delay DOM manipulations until all
  Ajax requests have resolved.
