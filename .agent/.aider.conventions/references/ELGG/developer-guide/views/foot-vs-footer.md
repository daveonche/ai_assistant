# Elgg Developer Guide: Foot vs Footer

Delta distillation of
<https://learn.elgg.org/en/stable/guides/views/foot-vs-footer.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/views/foot-vs-footer.rst`, Elgg ref `7.1`). Records only what
counters stale training-data memory: current API names, signatures,
defaults, deprecations, gotchas. Update in place when the stable manual
changes.

Two similarly named page elements with very different roles.

## `page/elements/footer`

The content of this view is placed inside the page footer wrapper:

```html
<div class="elgg-page-footer">
    <div class="elgg-inner">
        <!-- page/elements/footer goes here -->
    </div>
</div>
```

- Visible to end users; the usual place for a sitemap or other secondary
  global navigation, copyright info, "powered by elgg", etc.

## `page/elements/foot`

- Inserted just before the closing `</body>` tag.
- Meant as a place for scripts that don't already work with
  `elgg_import_esm('my/module');`.
- Gotcha: never override this view, and you probably don't need to extend
  it either — use the `elgg_*_esm` functions instead.
