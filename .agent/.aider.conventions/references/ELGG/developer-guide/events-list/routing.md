# Elgg Developer Guide: Events List — Routing

Category table for the events-list distillation: marker legend and the
behavioral traps live in `../events-list.md`. Distilled from the stable
manual on 2026-09-30 (source: `docs/guides/events-list.rst`, Elgg ref
`7.1`); update in place when the stable manual changes.

## Response filters

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `response, <route_name>` | results | filter the `\Elgg\Http\ResponseBuilder` before it is sent to the client; only used when the request path did not start with `action/` or `ajax/`; modify response content, status code, forward URL, or add response headers; `$params`: `request` |
| `response, form:<form_name>` | results | filter the `\Elgg\Http\ResponseBuilder` before it is sent to the client; applies to requests to `/ajax/form/<form_name>`; modify response content, status code, forward URL, or add response headers; `$params`: `request` |
| `response, view:<view_name>` | results | filter the `\Elgg\Http\ResponseBuilder` before it is sent to the client; applies to requests to `/ajax/view/<view_name>`; modify response content, status code, forward URL, or add response headers; `$params`: `request` |

## Route configuration and matching

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `route:config, <route_name>` | results | alter the route configuration before it is registered: path, default values, requirements, and middleware; register the handler outside the `init, system` handler — core routes register during `plugins_boot` (see traps in `../events-list.md`) |
| `route:rewrite, <identifier>` | results | alter the site-relative URL path for an incoming request (see the manual's routing guide); register the handler outside the `init, system` handler — rewrites run after `plugins_boot` completes (see traps in `../events-list.md`) |
| `route:match, system` | results | triggered when no route is registered for a given URL path, so generic URLs can be handled without registering every individual route; return an array with a route definition (see the manual's routing guide) that must contain a `route` key holding the route name; `$params`: `pathinfo` (the URL path to be matched) |
