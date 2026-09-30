# Elgg Developer Guide: Events List — System

Category table for the events-list distillation: marker legend and the
behavioral traps live in `../events-list.md`. Distilled from the stable
manual on 2026-09-30 (source: `docs/guides/events-list.rst`, Elgg ref
`7.1`); update in place when the stable manual changes.

## System events

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `activate, plugin` | | return `false` to prevent plugin activation |
| `cache:clear, system` | seq | clears internal and external caches |
| `cache:generate, <view>` | results | filters `/cache` view output when simplecache is *disabled*; fires for every `/cache` request — no Expires headers are used then |
| `cache:invalidate, system` | seq | invalidates internal and external caches |
| `cache:purge, system` | seq | purges old/stale cache content |
| `commands, cli` | results | register `elgg-cli` commands: return an array of command class names; commands must extend `\Elgg\Cli\Command` to be executable |
| `cron, <period>` | results | per-period cron; params: `time` (start timestamp), `dt` (`\DateTimeImmutable` of the start), `logger` (`\Elgg\Logger\Cron` for the cron log) |
| `cron:intervals, system` | results | register custom cron intervals |
| `deactivate, plugin` | | return `false` to prevent plugin deactivation |
| `diagnostics:report, system` | results | filters the diagnostics report download output |
| `elgg.data, page` | results | filters uncached, page-specific configuration data passed to the client (manual's JavaScript guide) |
| `format, friendly:title` | results | filters the "friendly" title used for URL generation |
| `format, friendly:time` | results | filters friendly time for `$params['time']` |
| `format, strip_tags` | results | strips tags; params: `original_string`, `allowed_tags` (optional) |
| `gc, system` | results | plugin garbage collection for `$params['period']` |
| `generate, password` | results | generate new random cleartext passwords |
| `init:cookie, <name>` | | return `false` to override setting that cookie |
| `init, system` | seq | plugin initialization: extend views, register callbacks, etc. |
| `languages, translations` | results | add/remove languages from the configurable set |
| `log, systemlog` | | fires for every triggered event via the `system_log` plugin; `Elgg\SystemLog\Logger::log()` uses it to populate the `system_log` table |
| `login_url, site` | results | filters the login URL; params carry the query elements added by the invoking script; must return an absolute URL |
| `output:before, page` | results | filters `$vars` before the page shell view (`page/<page_shell>`) in `elgg_view_page()`; to stop sending `X-Frame-Options`, unregister `Elgg\Page\SetXFrameOptionsHeaderHandler::class` from this event |
| `output, page` | results | filters the `elgg_view_page()` return value |
| `parameters, menu:<menu_name>` | results | `elgg_view_menu()`; change menu variables (e.g. sort order) before rendering; params: `name`, `sort_by`, plus caller params |
| `plugins_load, system` | seq | before plugins load; rarely used (prefer `init, system`); can load additional libraries |
| `plugins_boot, system` | seq | just after plugins load; rarely used (prefer `init, system`) |
| `prepare, html` | results | `elgg_format_html()`; prepares untrusted HTML; `$return` is an array: `html`, `options` |
| `prepare, menu:<menu_name>` | results | filters menu sections before display; sort/add/remove items; triggered by `elgg_view_menu()` and `elgg()->menus->prepareMenu()`; params: `selected_item`; returns `\Elgg\Menu\PreparedMenu` (collection of `\Elgg\Menu\MenuSection` of `\ElggMenuItem`) |
| `prepare, menu:<menu_name>:<type>:<subtype>` | results | granular variant fired before the general prepare event; only when params contain `entity` (`\ElggEntity`), `annotation` (`\ElggAnnotation`), or `relationship` (`\ElggRelationship`) — `<type>`/`<subtype>` derive from the object's type/subtype |
| `ready, system` | seq | after `init, system`; all plugins loaded, engine ready to serve pages |
| `regenerate_site_secret:before, system` | | `false` cancels regeneration; also message the user |
| `regenerate_site_secret:after, system` | | after the site secret is regenerated |
| `register, menu:<menu_name>` | results | filters the initial menu items from config before sectioning; triggered by `elgg_view_menu()` and `elgg()->menus->getMenu()`; params as returned by `parameters, menu:<menu_name>`; returns `\Elgg\Menu\MenuItems` (collection API and array access) |
| `register, menu:<menu_name>:<type>:<subtype>` | results | granular variant fired before the general register event; same conditions as the granular prepare event |
| `register, menu:filter:<filter_id>` | results | layout filter tabs for layouts passing `<filter_id>`; params/return as `register, menu:<menu_name>`; for the default `filter` id, `all`/`mine`/`friends` tabs derive from routes (`collection:<type>:<subtype>:all`/`:owner`/`:friends`) based on `entity_type`/`entity_subtype` (route-detected when absent); `all_link`/`mine_link`/`friend_link` params are deprecated; unregistered routes mean the tabs do not appear |
| `registration_url, site` | results | filters the registration URL (invite/referrer codes); params carry the added query elements; must return an absolute URL |
| `reload:after, translations` | | after translations are (re)loaded |
| `sanitize, input` | results | filters GET/POST input used by `get_input()` |
| `seeds, database` | results | register DB seeds extending `\Elgg\Database\Seeds\Seed` (executable via `elgg-cli database:seed`) |
| `send:before, http_response` | | handler receives the `\Symfony\Component\HttpFoundation\Response` to be sent; return `false` to prevent sending |
| `send:after, http_response` | | handler receives the `\Symfony\Component\HttpFoundation\Response` that was sent |
| `shutdown, system` | | after the page is sent; expensive operations belong here; see the traps in `../events-list.md` |
| `simplecache:generate, <view>` | results | filters `/cache` view output when simplecache is *enabled* |
| `upgrade, system` | | after a system upgrade finishes; upgrade scripts have run, caches are not cleared |
| `upgrade:execute, system` | seq + results | while executing an `\ElggUpgrade` (`$object` is the upgrade) |
