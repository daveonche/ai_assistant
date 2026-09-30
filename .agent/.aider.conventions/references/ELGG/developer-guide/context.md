# Elgg Developer Guide: Context

Delta distillation of <https://learn.elgg.org/en/stable/guides/context.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/context.rst`, Elgg ref `7.1`). Records only what counters stale
training-data memory: current API names, signatures, defaults, deprecations,
gotchas. Update in place when the stable manual changes.

## Purpose and status warning

- Context lets plugin callbacks decide whether to run — e.g. for generic
  events, so a callback fires only when the plugin itself caused the event.
- The source page carries an explicit warning: the functionality still works,
  but using global context to drive business logic is bad practice — it makes
  code less testable and more bug-prone. Do not build new business logic on
  context checks.

## API

- Legacy pair: `set_context()` (string, typically the plugin name) and
  `get_context()`.
- Preferred stack API: `elgg_push_context($string)` adds a context,
  `elgg_in_context($context)` tests the stack, `elgg_pop_context()` removes
  the context once it is no longer needed — always pop what you push.

## Default context

- Unset context is guessed: for pages called through the router it is the
  first segment of the current route (e.g. `profile` in `profile/username`).

## Context-dependent views

- A view may return different HTML depending on context: set the context
  before `elgg_view()`, then restore it afterwards. The search context is the
  frequent example.
