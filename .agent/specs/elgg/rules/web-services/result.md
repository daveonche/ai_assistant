# Elgg Developer Guide: API Results

Delta distillation of
<https://learn.elgg.org/en/stable/guides/web-services/result.html>,
distilled from the stable manual on 2026-10-01 (source:
`docs/guides/web-services/result.rst`, Elgg ref `7.1`). Records only what
counters stale training-data memory: current API names, signatures,
defaults, deprecations, gotchas. Update in place when the stable manual
changes.

Every API call returns a JSON object with a `status` field plus either a
`result` (success) or a `message` (error).

## Success result structure

```json
{
    "status": 0,
    "result": "API result"
}
```

Depending on the API call, `result` can contain any type of content
(string, number, array, object, etc.):

```json
{
    "status": 0,
    "result": 10
}
```

```json
{
    "status": 0,
    "result": {
        "name": "Some user",
        "username": "apiexample",
        "email": "user@example.com"
    }
}
```

## Error result structure

```json
{
    "status": -1,
    "message": "The reason the API call failed"
}
```

## Default status codes

The `status` field always contains a number representing the result. Any
value other than `0` is considered an error.

- `0`: success result
- `-1`: generic error result
- `-20`: the user authentication token is missing, is invalid or has
  expired
- `-30`: the api key has been disabled
- `-31`: the api key is inactive
- `-32`: the api key is invalid

Developers can implement their own status codes to represent different
error states, so the request doesn't have to rely on the error message to
know what went wrong.

Gotcha: `result` and `message` can contain messages in different
languages — the user language for user-authenticated API calls, the site
language for other calls. The language can change, either by the user or
by a site administrator, so don't treat message text as a stable
identifier.
