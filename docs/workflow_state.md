# Workflow Session State

Last updated: 2026-09-29

## Active Workflow

- Command: `$workflows-post-scaffolding-chain` — chain active, paused at Phase 2; sentinel/de-introspection pass complete
- Last completed: sentinel/de-introspection pass finished — testing/unit-test gotchas.md verified in sync with its SKILL.md (no changes needed); all pass targets across code, documentation, learning, planning, requirements, workflows done
- Next action: run `$planning-sprint-story` to resume the chain at Phase 2
- Reload to resume: `/read-only .agent/AGENTS.md`, `/read-only .agent/.aider.prompt/planning/sprint-story/SKILL.md` — everything else recoverable via `/read-only` on demand.

## Pending Side Task

- Elgg upgrade notes: all 24 official transitions as `references/ELGG/upgrade-notes/<from>-to-<to>.md`, one per round in ascending order; `1.7-to-1.8.md` through `3.0-to-3.1.md` committed (10 of 24); next: `3.1-to-3.2.md`; if a source page is too massive for one file, follow the `2.x-to-3.0.md` pattern — main file keeps highlights plus a "Detail references" section pointing to a `<from>-to-<to>/` detail directory of thematic sub-files (`removed-views.md`, `removed-functions-methods.md`, `removed-classes-globals.md`, `removed-js-actions-pagehandlers.md`, `deprecated-changed-apis.md`) loaded on demand via `/read-only`
- Per-round recipe (learn.elgg.org is Cloudflare-gated — use GitHub raw): locate `docs/appendix/upgrade-notes/<from>-to-<to>.rst` via `https://api.github.com/repos/Elgg/Elgg/git/trees/<ref>?recursive=1` (ref = target minor, next round `3.2`; if it 404s try `master` or a later minor), fetch `curl -sL "https://raw.githubusercontent.com/Elgg/Elgg/<ref>/<path>" -o <from>-to-<to>.rst` into the repo root (`/tmp` is not mounted — cwd only), verify with `head -20` that it is RST (title line, not a Cloudflare challenge), `/add` it, distill per the `2.2-to-2.3.md` pattern (load it via `/read-only` first), `/add` the target `.agent/.aider.conventions/references/ELGG/upgrade-notes/<from>-to-<to>.md`, apply as an empty-SEARCH edit via `/code proceed`, then delete the `.rst` scratch file
