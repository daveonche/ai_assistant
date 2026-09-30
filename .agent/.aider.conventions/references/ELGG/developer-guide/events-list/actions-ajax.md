# Elgg Developer Guide: Events List — Actions and Ajax

Category table for the events-list distillation: marker legend and the
behavioral traps live in `../events-list.md`. Distilled from the stable
manual on 2026-09-30 (source: `docs/guides/events-list.rst`, Elgg ref
`7.1`); update in place when the stable manual changes.

## Action events

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `action:validate, <action>` | results | triggered before the action script/controller is executed; validate/alter user input before proceeding; throw `\Elgg\Exceptions\Http\ValidationException` or return `false` to terminate further execution; `$params`: `request` (an `\Elgg\Request`) |
| `action_gatekeeper:permissions:check, all` | results | triggered after a CSRF token is validated; return `false` to prevent validation |

## Ajax

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `ajax_results, <event_type>*` | results | when the `elgg/Ajax` module is used, gives access to the results object so it can be altered/extended; the event type depends on the Ajax method called: `action()` → `action:<action_name>`, `path()` → `<route_name>`, `view()` → `view:<view_name>`, `form()` → `form:<action_name>`; `$params`: `request` |
