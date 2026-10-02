# Elgg Developer Guide: HMAC Authentication

Delta distillation of
<https://learn.elgg.org/en/stable/guides/web-services/hmac.html>,
distilled from the stable manual on 2026-10-01 (source:
`docs/guides/web-services/hmac.rst`, Elgg ref `7.1`). Records only what
counters stale training-data memory: current API names, signatures,
defaults, deprecations, gotchas. Update in place when the stable manual
changes.

HMAC signature scheme for API authentication in Elgg's RESTful API
framework: the client sends the HMAC signature plus a set of special HTTP
headers on every call that requires API authentication. This ensures the
call is made from the stated client and the data has not been tampered
with.

## Data the HMAC is constructed over

- The public API key identifying you to the Elgg API server, as provided
  by the APIAdmin plugin;
- the private API key provided by Elgg (companion to the public key);
- the current unix time in seconds;
- a nonce, so two requests in the same second get different signatures;
- the URL-encoded string representation of any GET variable parameters,
  e.g. `method=test.test&foo=bar`;
- when sending POST data, the hash of that data.

## Required HTTP headers

- `X-Elgg-apikey` — the public API key;
- `X-Elgg-time` — unix time used in the HMAC calculation;
- `X-Elgg-nonce` — a random string;
- `X-Elgg-hmac` — the HMAC, base64 encoded;
- `X-Elgg-hmac-algo` — the algorithm used in the HMAC calculation.

When sending POST data, also send:

- `X-Elgg-posthash` — the hash of the POST data;
- `X-Elgg-posthash-algo` — the algorithm used to produce the POST data
  hash;
- `Content-type` — the content type of the data being sent
  (`application/x-www-form-urlencoded` or `multipart/form-data`);
- `Content-Length` — the length in bytes of the POST data.

Reference client: `\Elgg\WebServices\ElggApiClient` implements this HMAC
signature and serves as a good reference on how to implement it.

## Supported hashing algorithms

- `sha256` — recommended;
- `sha1` — fast, however less secure;
- `md5` — weak; will be removed in the future.

## POST hash calculation

- `Content-Type: application/x-www-form-urlencoded;` — the post hash is
  calculated over all the POST data using one of the supported
  algorithms.
- `Content-Type: multipart/form-data;` — the post hash is calculated over
  an empty string.

Report the result in `X-Elgg-posthash` and the used algorithm in
`X-Elgg-posthash-algo`.

Gotcha: since the POST hash isn't calculated when using
`multipart/form-data`, only use that content type when calling APIs that
need a file input.

## HMAC hash calculation

Calculate the overall HMAC over the following data, in order, using the
API secret as the HMAC secret and one of the supported algorithms:

1. a UNIX timestamp — report it in `X-Elgg-time`;
2. a random string — report it in `X-Elgg-nonce`;
3. the public API key — report it in `X-Elgg-apikey`;
4. the URL query string (for example `method=test.test&foo=bar`);
5. when the request is a POST, the `posthash` reported in
   `X-Elgg-posthash`.

Base64-encode the result, then URL-encode it, and report it in
`X-Elgg-hmac`; report the used algorithm in `X-Elgg-hmac-algo`.

## Hashing cache

For security reasons each HMAC hash needs to be unique: all submitted
hashes are stored for 25 hours to prevent reuse.
