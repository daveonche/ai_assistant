# Elgg Developer Guide: Plugin Skeleton

Delta distillation of
<https://learn.elgg.org/en/stable/guides/plugins/plugin-skeleton.html>,
distilled from the stable manual on 2026-10-01 (source:
`docs/guides/plugins/plugin-skeleton.rst`, Elgg ref `7.1`). Records only
what counters stale training-data memory: current API names, signatures,
defaults, deprecations, gotchas. Update in place when the stable manual
changes.

The standard for plugin structure in Elgg as of Elgg 2.0.

## Example structure

Files for plugin `example` go in `/mod/example/`:

```text
actions/
    example/
        action.php
        other_action.php
classes/
    VendorNamespace/
        PluginNamespace/
            ExampleClass.php
languages/
    en.php
vendors/
    example_3rd_party_lib/
views/
    default/
        example/
            component.css
            component.js
            component.png
        forms/
            example/
                action.php
                other_action.php
        object/
            example.php
            example/
                context1.php
                context2.php
        plugins/
            example/
                settings.php
                usersettings.php
        resources/
            example/
                all.css
                all.js
                all.php
                owner.css
                owner.js
                owner.php
        widgets/
            example_widget/
                content.php
                edit.php
elgg-plugin.php
CHANGES.txt
COPYRIGHT.txt
INSTALL.txt
LICENSE.txt
README.txt
composer.json
```

## Required files

Plugins **must** provide a `composer.json` in the plugin root to be
recognized by Elgg. Minimally compliant structure:

```text
mod/example/
    composer.json
```

## Actions

Action scripts go in `actions/`, located by action name: action
`my/example/action` → `my_plugin/actions/my/example/action.php`. The form
body submitting to it goes in `forms/my/example/action.php` — this makes
the action/form connection obvious and enables `elgg_view_form()`.

## Text files

`*.txt` files **must** be Markdown syntax; they generate links in the
plugin management sections.

- `README.txt` — *should* provide additional unspecified plugin info.
- `COPYRIGHT.txt` — if included, **must** explain the plugin's copyright.
- `LICENSE.txt` — if included, **must** provide the license text.
- `INSTALL.txt` — if included, **must** provide install instructions when
  the process is sufficiently complicated (third-party libraries, API
  keys).
- `CHANGES.txt` — if included, **must** list changes grouped by version,
  most recent version at the top.

Additional `*.txt` files are allowed but get no reading interface.

## Pages

Render full pages with **resource views** (names beginning with
`resources/`) so other plugins can replace functionality via the view
system. Rationale: a logical URL-to-script relationship, and a clean
plugin root.

## Classes

Elgg provides [PSR-0](http://www.php-fig.org/psr/psr-0/) autoloading from
every active plugin's `classes/` directory; follow
[PHP-FIG](http://www.php-fig.org/) standards.

Gotcha: files with a `.class.php` extension will **not** be recognized.

No required class layout — keep it readable and findable; splitting
functions across classes improves maintainability and testability.

## Vendors

Third-party libraries *should* go in `vendors/` in the plugin root. The
folder has no special meaning to the Elgg engine; it mirrors core's
historical layout for consistency.

## Views

To override core views, place views in `views/`, or use `elgg-plugin.php`
for detailed file/path mapping (see the views guide). JavaScript and CSS
live in the views system (see the JavaScript guide).
