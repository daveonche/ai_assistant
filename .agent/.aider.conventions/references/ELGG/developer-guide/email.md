# Elgg Developer Guide: Email

Delta distillation of <https://learn.elgg.org/en/stable/guides/email.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/email.rst`, Elgg ref `7.1`). Records only what counters stale
training-data memory: current API names, signatures, defaults, deprecations,
gotchas. Update in place when the stable manual changes.

## HTML mail

- Configurable per site by an admin: all outgoing emails as HTML or plain
  text; HTML emails are enabled by default.
- When enabled, the email contents are wrapped in HTML elements and some CSS
  is applied; this allows theme developers to style the emails.
- The appropriate views to format and style the emails live in
  `views/default/email`.
- The CSS is inlined automatically so it works in most email clients.
- Images in an email can be converted to inline base64 encoded images
  (default) or attachments; converted images are the best way to have images
  show consistently in various clients.
- Instead of having the message converted automatically to HTML, provide
  your own `html_message` in the `params` of a notification; it must be a
  `string`. Elgg automatically tries to inline CSS provided in the `css`
  param; to skip CSS inlining set the `convert_css` param to `false`:

```php
elgg_send_email([
    'from' => 'from@elgg.org',
    'to' => 'to@elgg.org',
    'subject' => 'Test Email',
    'body' => 'Welcome to the site',
    'params' => [
        'html_message' => '
            <p>Welcome to the site</p>
            <img src="site_logo.png"/>
        ',
        'convert_css' => true,
        'css' => 'p { padding: 10px;}'
    ],
]);
```

## Attachments

`elgg_notify_user()` and enqueued notifications support attachments for
e-mail notifications when provided in `$params`: add an `attachments` key to
`$params` holding an array of the attachments. Each attachment is one of:

- An `ElggFile` which points to an existing file
- An array with the file contents
- An array with a filepath

```php
// this example is for elgg_notify_user()
$params['attachments'] = [];

// Example of an ElggFile attachment
$file = new \ElggFile();
$file->owner_guid = <some owner_guid>;
$file->setFilename('<some filename>');

$params['attachments'][] = $file;

// Example of array with content
$params['attachments'][] = [
    'content' => 'The file content',
    'filename' => 'test_file.txt',
    'type' => 'text/plain',
];

// Example of array with filepath
// 'filename' can be provided; if not, basename() of filepath is used
// 'type' can be provided; if not, a best guess is attempted
$params['attachments'][] = [
    'filepath' => '<path to a valid file>',
];

$recipient->notify('some_action', $on_some_object, $params);
// or
elgg_notify_user($recipient, 'some_action', $on_some_object, $params);
```

## E-mail address formatting

Elgg uses the Symfony library for e-mail address formatting:
`\Symfony\Component\Mime\Address`.

```php
// the constructor takes two variables
// first is the email address, this is REQUIRED
// second is the name, this is optional
$address = new \Symfony\Component\Mime\Address('example@elgg.org', 'Example');

// this will result in 'Example <example@elgg.org>'
echo $address->toString();
```

Helper functions:

- `\Symfony\Component\Mime\Address::create($string)` — returns an
  `\Symfony\Component\Mime\Address` with e-mail and name set, given a
  formatted string (e.g. `Example <example@elgg.org>`).
