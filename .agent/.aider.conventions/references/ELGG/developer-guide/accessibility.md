# Elgg Developer Guide: Accessibility

Delta distillation of <https://learn.elgg.org/en/stable/guides/accessibility.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/accessibility.rst`, Elgg ref `7.1`). Records only what counters stale
training-data memory: current API names, signatures, defaults, deprecations,
gotchas. Update in place when the stable manual changes.

## Status and references

- The page is a best-practices list, explicitly ongoing work; contributions
  go through <https://github.com/Elgg/Elgg>.
- Authoritative external baselines it points to: the WCAG overview
  <https://www.w3.org/WAI/standards-guidelines/wcag/glance/>, the WCAG
  techniques list
  <https://www.w3.org/TR/WCAG20-TECHS/Overview.html#contents>, and the W3C
  evaluation-tool list <https://www.w3.org/WAI/ER/tools/>.

## Implementation rules

- Generate markup through core views (`output/*`, `input/*`) so a11y
  concerns are baked into the views instead of re-solved per plugin.
- Every image needs a descriptive `alt`; spacer or purely decorative
  graphics get a blank `alt`.
- Every `<a>` needs text or an accessible image inside — otherwise screen
  readers read the URL aloud. Prefer descriptive link text over generic
  text like "Click here".
- Markup must be valid.
- Themes must not reset `outline` to nothing: `:focus` needs distinct
  visual treatment so users can see where they are.

## Testing

- Try different font-size/zoom settings and confirm the theme stays usable.
- Turn off CSS and confirm the page's sequential order makes sense.
- Check with the W3C evaluation tools linked above.

## Process

- Tag accessibility-related tickets `a11y` (short for "accessibility"). The
  source page's ticket reference is to the legacy trac tracker, while its
  note directs contributions to GitHub.
