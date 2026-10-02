# Elgg Developer Guide: Don't Modify Core

Delta distillation of <https://learn.elgg.org/en/stable/guides/dont-modify-core.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/dont-modify-core.rst`, Elgg ref `7.1`). Records only what counters
stale training-data memory: current API names, signatures, defaults,
deprecations, gotchas. Update in place when the stable manual changes.

## The rule

In general, don't modify non-config files that come with third-party software
like Elgg.

## The sanctioned customization path

- Install Elgg as a composer dependency.
- Store application-specific modifications in a plugin.
- Alter behavior through the Elgg plugin API.
- To share customizations between sites or publish them as a reusable package
  for the community, create a plugin using the same plugin APIs and file
  structure.

## Why: it makes it hard to get help

When you don't share the same codebase as everyone else, it's impossible for
others to know what is going on in your system and whether your changes are
to blame. This frustrates those who offer help and adds considerable noise
to the support process.

## Why: it makes upgrading tricky and potentially disastrous

Upgrades are wanted and needed for security patches, new features, new plugin
APIs, stability improvements, and performance improvements. With modified
core files you must be very careful that your changes are not overwritten and
that they are compatible with the new Elgg code; lost or incompatible changes
can remove features you've added and even completely break your site.

It is also a slippery slope: many modifications lead to an upgrade process so
complex it is practically impossible — many sites are stuck running old
versions of software for taking this path.

## Why: it may break plugins

You may not realize until much later that your "quick fix" broke seemingly
unrelated functionality that plugins depended on.

## Summary

- Resist the temptation: editing existing files is quick and easy, but doing
  so heavily risks the maintainability, security, and stability of your site.
- When receiving advice, consider whether the person telling you to modify
  core will be around to rescue you if you run into trouble later.
- Apply the principle to software in general: if you can avoid it, don't
  modify third-party plugins either, for the same reasons — plugin authors
  release new versions too, and you will want those updates.
