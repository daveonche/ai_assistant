# Elgg Developer Guide: Actions

Delta distillation of <https://learn.elgg.org/en/stable/guides/actions.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/actions.rst`, Elgg ref `7.1`). Records only what counters stale
training-data memory: current API names, signatures, defaults, deprecations,
gotchas. Update in place when the stable manual changes.

## Registration

- Register during boot with `elgg_register_action("example", __DIR__ .
  "/actions/example.php")`; the script runs for submissions to
  `action/example` URLs.
- Plugin config alternative (`elgg-plugin.php`): an `'actions'` section;
  per action: `access` (logged-in default | `public` | `admin` |
  `logged_out`), `filename` (custom script path), or `controller`
  (invokable class). Files default to the plugin's `/actions/` dir.
- URL gotcha: action URLs always use `/action/` (singular); script files
  live under `/actions/` (plural) with an extension. Prefer
  `elgg_generate_action_url()` to avoid the mismatch.
- All action URLs are served through the routing service; the default
  middleware performs the CSRF check.

## Writing action files

- Read request parameters with `get_input('name', 'default')`.
- Success: `return elgg_ok_response($data, $message, $forward_url);` —
  `$data` reaches XHR clients only; ignored on non-XHR.
- Error: `return elgg_error_response($message, $forward_url, $status_code);`
  — forward `REFERRER` to go back; send `ELGG_HTTP_NOT_FOUND` /
  `ELGG_HTTP_FORBIDDEN` on XHR as appropriate.

## Action controllers

- Extend `\Elgg\Controllers\GenericAction`; lifecycle order: `sanitize()`,
  `validate()`, `executeBefore()`, `execute()`, `executeAfter()`,
  `success()`; exceptions from any step are handled by `error()` (system
  message + forward to `REFERER`).
- Entity save/edit: `\Elgg\Controllers\EntityEditAction` does the generic
  checks from the entity's fields configuration and creates a river item on
  create; register it with `'options' => ['entity_type' => ...,
  'entity_subtype' => ...]` and configure type/subtype at registration.

## Customizing actions

- `elgg_trigger_event_results('action:validate', $action, [], true)` fires
  before every action; a handler returning `false` blocks execution.
  Return nothing when validation passes (captcha-style interception).

## Core action: entity/delete

- Use for plain deletes: `elgg_generate_action_url('entity/delete', ['guid'
  => $guid, 'forward_url' => $forward_url])` in `output/url` with
  `'confirm' => true`.
- Custom success messages via translation keys
  `entity:delete:$type:$subtype:success` and `entity:delete:$type:success`.

## Fields service

- `$entity->getFields()` and `elgg()->fields->get($type, $subtype)` return
  field configs directly usable with `elgg_view_field()`.
- Defaults: static `getDefaultFields(): array` on the entity class, or an
  event handler on `'fields', '<type>:<subtype>'` that appends to the value.

## Forms

- `elgg_view_form('example')` sets the action URL, injects CSRF tokens
  (`__elgg_ts`, `__elgg_token`), and renders the body from the
  `forms/example` view.
- Defer the footer with `elgg_set_form_footer(elgg_view('input/submit'))`
  so other plugins can extend `forms/example`.
- Render inputs via `elgg_view_field([...])` with `#type`, `#label`,
  `#help` plus the input's own params; bundled inputs include `input/text`,
  `input/longtext`, `input/select`, `input/checkbox(es)`, `input/radio`,
  `input/file`, `input/hidden`, `input/access`, `input/tags`, and more.

## Default entity form

- `elgg_view_entity_form($type, $subtype, $entity)` uses the configured
  fields; view fallback order `<type>/<subtype>/edit` → `<subtype>/edit` →
  `entity/edit`; action fallback `<type>/<subtype>/edit` →
  `<subtype>/edit`, else `\Elgg\Exceptions\DomainException` is thrown.

## File uploads

- `input/file` view; the enctype of POST forms defaults to
  `multipart/form-data`.
- Fetch uploads in the action with `elgg_get_uploaded_file('icon')`.
- Icon helper view `entity/edit/icon` (vars: `entity`, `entity_type`,
  `entity_subtype`, `icon_type`, `name`, `remove_name`, `required`,
  `cropper_enabled`, `show_remove`, `show_thumb`, `thumb_size`); save with
  `$entity->saveIconFromUploadedFile('icon')`, remove with
  `$entity->deleteIcon()` when `get_input('icon_remove')` is set.

## Sticky forms

- Helpers: `elgg_make_sticky_form($name, $ignored_field_names = [])`,
  `elgg_get_sticky_values($name)`, `elgg_is_sticky_form($name)`,
  `elgg_clear_sticky_form($name)`.
- Flow: make sticky at the top of the action; load sticky values when
  rendering; clear after success or after loading.
- Elgg 5.0+: `$form_vars['sticky_enabled'] = true` on `elgg_view_form()`
  auto-fills `$body_vars` after an error; optional `sticky_form_name`
  (defaults to the action name) and `sticky_ignored_fields` (e.g.
  passwords).
- Ignore sensitive fields (passwords) via the second argument of
  `elgg_make_sticky_form()`.
- Prepare defaults/edits with an event handler on
  `'form:prepare:fields', '<action name>'` (see Bookmarks'
  `PrepareFields`).

## Security

- All actions require CSRF tokens; token-less calls are ignored with a
  warning. Tokens are auto-added by `elgg_view_form()`,
  `elgg_view('output/url', ['is_action' => true])`,
  `elgg_add_action_tokens_to_url($url)`, `elgg_generate_action_url()`.
- Manual tokens: `elgg()->csrf->getCurrentTime()->getTimestamp()` +
  `elgg()->csrf->generateActionToken($ts)`; from JS:
  `elgg.security.token.__elgg_ts` / `__elgg_token` (refreshed
  periodically).
- HMAC for untrusted channels: `elgg_build_hmac([$a, $b])->getToken()` /
  `->matchesToken($mac)`; types must match exactly between generate and
  validate (`123` ≠ `"123"`).
- Signed URLs (`elgg_http_get_signed_url($url)`, SHA-256 HMAC): for cases
  where action tokens are unsuitable, e.g. email confirmation links.
  Warning: they give no CSRF protection and never replace action tokens.
