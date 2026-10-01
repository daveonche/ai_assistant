# Elgg Developer Guide: Web Services

Delta distillation of <https://learn.elgg.org/en/stable/guides/web-services.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/web-services.rst`, Elgg ref `7.1`). Records only what counters
stale training-data memory: current API names, signatures, defaults,
deprecations, gotchas. Update in place when the stable manual changes.

Elgg's web services framework builds an HTTP API for the site — a REST/RPC
hybrid similar to the APIs of Flickr and X. Setup takes 4 steps: enable the
web services plugin, expose methods, set up API authentication, set up user
authentication. Subpages `web-services/hmac` and `web-services/result` are
pending (see `index.md`).

## Security

- Consume web services via secure protocols only: do not enable web
  services if the site is not served via HTTPs — especially important when
  API key-only authentication is allowed.
- Third-party tools exposing API methods: run a thorough security audit,
  and require API authentication for ALL methods even when they require
  user authentication — methods without API authentication can easily be
  abused to spam the site.
- Limit the validity of API keys and provide mechanisms for API clients to
  renew their keys.

## Exposing methods

Expose API methods in one of two ways: the `web_services` section in the
plugin's `elgg-plugin.php` (see `plugins.md`), or during the
`'register', 'api_methods'` event.

Example — a function that echoes text back to the caller (requires neither
API nor user authentication):

```php
function my_echo($string) {
    return $string;
}
```

Registered via `elgg-plugin.php`:

```php
// as part of the elgg-plugin.php
'web_services' => [
    'test.echo' => [
        'GET' => [ // the HTTP call method (GET|POST)
            'callback' => 'my_echo', // required
            'description' => 'A testing method which echos back a string', // optional
            'params' => [ // optional, input parameters for the API method
                'string' => ['type' => 'string'],
            ],
            'require_api_auth' => false, // optional (default: false)
            'require_user_auth' => false, // optional (default: false)
            'associative' => false, // optional, input params as one array argument (default: false)
        ],
    ],
],
```

Or via the event:

```php
// as part of the 'register', 'api_methods' event
function my_plugin_event_handler(\Elgg\Event $event) {
    $results = $event->getValue();

    $results['test.echo']['GET'] = [
        'callback' => 'my_echo',
        'description' => 'A testing method which echos back a string',
        'params' => [
            'string' => ['type' => 'string'],
        ],
    ];

    return $results;
}
```

- Note: with no `description` provided, the system checks for the language
  key `web_services:api_methods:<method>:<http call method>:description`.
- Verify: `http://yoursite.com/services/api/rest/json/?method=system.api.list`
  lists the method; `.../?method=test.echo&string=testing` returns
  `{"status":0,"result":"testing"}`.
- Plugins can filter the output of individual API methods by registering a
  handler for the `'rest:output', $method` event.

## Response formats

- JSON is the default format.
- XML and serialized PHP: enable the `data_views` plugin and substitute
  `xml` or `php` for `json` in the URL.
- Additional response formats: define new view types.

## Parameters

Parameters are an associative array: key = parameter name, value = array
with `type`, `default` and `required` fields (plus free-form fields like
`description`). Submitted values must match the declared type — the API
throws an exception when validation fails.

Recognized types:

- `integer` (or `int`)
- `boolean` (or `bool`) — `'false'`, `0` and `'0'` evaluate to `false`,
  everything else to `true`
- `string`
- `float`
- `array`

Unrecognized types throw an API exception.

Example with required and optional parameters:

```php
// as part of the elgg-plugin.php
'web_services' => [
    'test.greet' => [
        'GET' => [
            'callback' => 'my_greeting',
            'description' => 'A testing method which greets the user with a custom greeting',
            'params' => [
                'name' => [
                    'type' => 'string',
                    'required' => true,
                    'description' => 'Name of the person to be greeted by the API',
                ],
                'greeting' => [
                    'type' => 'string',
                    'required' => false,
                    'default' => 'Hello',
                    'description' => 'Greeting to be used, e.g. "Good day" or "Hi"',
                ],
            ],
        ],
    ],
],
```

- Note: a missing parameter with no default value becomes `null`. Before
  Elgg v2.1 a bug shifted later arguments left in this case.

### Receive parameters as associative array

With many parameters, set `'associative' => true` so the callback receives
a single argument: an associative array of parameter => input pairs.

```php
function greet_me($values) {
    $name = elgg_extract('name', $values);
    $greeting = elgg_extract('greeting', $values, 'Hello');
    return "$greeting, $name";
}
```

- Gotcha: the prose says to "set `$assoc` to `true` in
  `elgg_ws_expose_function()`" — a legacy function reference; the current
  mechanisms are the `'associative' => true` config key or the equivalent
  key in the `'register', 'api_methods'` event.
- Note: a missing parameter with no default value gets `null`.

## API authentication

Control access to exposed methods (same-server integrations, limiting
external developers, call quotas). Two built-in methods: key-based and
HMAC signature-based (see `web-services/hmac.md`); custom authentication
methods can be added (PAM, below).

### Key-based authentication

Developers request a key (a random string) and pass it with every call
requiring API authentication — similar to Google, Flickr, or X. Keys are
stored in the database; a missing or bad key denies the call with an error
message.

Example — count users registered since a timestamp:

```php
function count_new_users(int $since) {
    return elgg_count_entities([
        'type' => 'user',
        'created_after' => $since,
    ]);
}
```

Exposed as `users.new` (GET) with a required `since` parameter (type
`int`) and `'require_api_auth' => true`; `system.api.list` then reports it
as requiring API authentication, and a browser hit returns an API
authentication failure.

- As of Elgg 3.2, API keys can be generated by the webservices plugin; it
  returns a public and a private key — use the **public** key for this
  kind of API authentication.
- Test with a GET request passing the key as the `api_key` parameter, e.g.
  `http://yoursite.com/services/api/rest/xml/?method=users.active&api_key=1140321cb56c71710c38feefdf72bc462938f59f`.
- Gotcha: the manual's test URL uses `method=users.active` while the
  registered method is `users.new` — cross-check the method name when
  adapting.

### Signature-based authentication

The HMAC approach (see `web-services/hmac.md`) is similar to OAuth or
Amazon's S3: it involves both the public and the private key, verifying
the caller's identity and that the data was not tampered with in transit.
Much more involved — may put developers off when other sites offer
key-based authentication.

## User authentication

For pushing data into Elgg as a user (e.g. a desktop app posting to the
wire), Elgg provides token-based authentication: the user submits username
and password to the `auth.gettoken` method in exchange for a token, then
passes that token as the `auth_token` parameter on subsequent calls until
it expires. To avoid users trusting their passwords to 3rd-party
applications, extend the capability with an approach like OAuth.

Example — post to the wire:

```php
function my_post_to_wire($text) {

    $text = elgg_substr($text, 0, 140);
    $post = new \ElggWire();

    $post->description = $text;
    $post->method = 'api';
    $post->save();

    // returns guid of wire post
    return $post->guid;
}
```

Exposed as a POST method with both authentications required:

```php
// as part of the elgg-plugin.php
'web_services' => [
    'thewire.post' => [
        'POST' => [
            'callback' => 'my_post_to_wire',
            'description' => 'Post to the wire. 140 characters or less',
            'params' => [
               'text' => [
                    'type' => 'string',
                ],
            ],
            'require_api_auth' => true,
            'require_user_auth' => true,
        ],
    ],
],
```

- Note: cannot be tested with a web browser like the GET methods — client
  code is needed.

## Building out your API

Design step: what data to expose, who or what the API users are, how they
get access keys, how the API is documented. Look at popular Web 2.0 APIs
for inspiration; for 3rd-party developers, provide one or more
language-specific clients.

## Determining the authentication available

Elgg's web services API uses a pluggable authentication module (PAM)
architecture to manage user and developer authentication — modules can be
added and removed (e.g. replace the default user authentication PAM with
OAuth).

Register a callback for the `'rest', 'init'` event:

```php
elgg_register_event_handler('rest', 'init', 'rest_plugin_setup_pams');
```

Then register the PAMs to use:

```php
function rest_plugin_setup_pams() {
    // user token can also be used for user authentication
    elgg_register_pam_handler(\Elgg\WebServices\PAM\UserToken::class);

    // simple API key check
    elgg_register_pam_handler(\Elgg\WebServices\PAM\APIKey::class, 'sufficient', 'api');
}
```
