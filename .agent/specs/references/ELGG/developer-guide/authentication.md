# Elgg Developer Guide: Authentication

Delta distillation of <https://learn.elgg.org/en/stable/guides/authentication.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/authentication.rst`, Elgg ref `7.1`). Records only what counters
stale training-data memory: current API names, signatures, defaults,
deprecations, gotchas. Update in place when the stable manual changes.

## Out of the box

Elgg ships complete username/email + password authentication: remember-me
cookies for persistent login, password reset logic, secure password storage,
logout, and UIs for all of the above. Developers only need to secure pages and
actions with the built-in functions.

## Working with the logged-in user

- `elgg_is_logged_in()` — boolean check for any logged-in user.
- `elgg_is_admin_logged_in()` — boolean check for logged-in admins.
- `elgg_get_logged_in_user_entity()` — returns the current user as an
  `ElggUser` (all its methods and properties available), or `null` when not
  logged in. Gotcha: check for `null` before using the return value.

## Gatekeepers

Gatekeepers manage how code gets executed by applying access control rules;
on failure they forward the user to the front page.

- `elgg_gatekeeper();` — forward to the front page unless logged in; place at
  the top of code meant for logged-in users only.
- `elgg_admin_gatekeeper();` — forward to the front page unless the user is
  an admin.

## Pluggable Authentication Modules (PAM)

- PAM lets plugins supply their own authentication handlers. Whenever a
  request needs authentication the system calls `elgg_pam_authenticate()`,
  which probes the registered PAM handlers until one returns success.
- Preferred approach: a separate plugin whose one simple task is processing
  an authentication request, with the handler set up in the plugin's
  `Bootstrap` class and registered via `elgg_register_pam_handler()`.
- `elgg_register_pam_handler()` takes the handler name, the importance, and
  the policy as parameters; it is advised to register the handler in the
  plugin's init function.
- The handler is a function taking a single parameter, the credentials:

```php
// classes/Your/Plugin/Bootstrap.php

function init() {
   // Register the authentication handler
   elgg_register_pam_handler('your_plugin_auth_handler');
}

// your_plugin/lib/functions.php

function your_plugin_auth_handler($credentials) {
   // do things ...
}
```

## Importance

- Default importance: **sufficient**. In a list of authentication modules, if
  any one marked *sufficient* returns `true`, `elgg_pam_authenticate()`
  returns `true`.
- Exception: modules registered as **required** must all return `true` for
  `elgg_pam_authenticate()` to return `true`, regardless of whether all
  sufficient modules return `true`.

## Passed credentials

- The credentials format varies with the originating request.
- Regular login via the login form: a named array with keys `username` and
  `password`.
- Requests such as XML-RPC: credentials are set in the HTTP header, so
  nothing is passed to the handler — it must perform its own steps to
  authenticate the request.

## Return value

- The handler should return a `boolean` indicating whether the request could
  be authenticated.
- Caveat: for a regular user login where credentials are available as
  username and password, the user gets logged in automatically. In the
  XML-RPC-style case the handler must perform the login itself, since the
  rest of the system knows nothing about the possible credential formats or
  contents. Logging in a user is done with `elgg_login()`, which expects an
  `ElggUser` object.
