# Elgg Conventions

## 1. Core & Plugins
- **Don't Modify Core**: Never modify Elgg core files. Use plugins to customize behavior.
- **Plugin Structure**: Register configurations, events, and actions in `elgg-plugin.php`.
- **Required File**: `composer.json` is required in the plugin root.
- **No Direct File Calls**: Do not directly call files in the `mod` directory.

## 2. Database & Entities
- **Database**: Use `elgg_get_entities()` and `elgg_get_metadata()`. No raw SQL.
- **Entities**: Extend `ElggEntity`, `ElggObject`, or `ElggUser`. Use `elgg_call(ELGG_IGNORE_ACCESS, ...)` for access control.
- **Deletion**: Use hooks to clean up metadata and relationships on deletion.

## 3. Routing & Views
- **Standardized Routing**: Use standard URLs (e.g., `page_handler/all`, `page_handler/view/<guid>`).
- **Page Handlers**: Do not contain HTML. Use `elgg_view_resource()` to render `views/default/resources/...` scripts.
- **Views**: Use `views/default/` for presentation. View names reflect their path (e.g., `hello/world`).
- **Page Structure**: Use the `default` layout. Build pages with `elgg_view_layout('default', $options)` and `elgg_view_page($title, $layout_area)`. Do not override `page/elements/foot`; use `elgg_import_esm()` for scripts. Use `page/elements/footer` for visible footer content.
- **Entity Views**: `object/<subtype>` views must handle `$vars['full_view']` and check `$vars['entity']`. Use `elgg_view_entity()` and `elgg_list_entities()`.
- **Altering Views**: Override by creating files in plugin dir. Extend via `elgg_extend_view()` in `elgg-plugin.php`. Alter input/output via `view_vars` and `view` events.
- **Assets & Simplecache**: Cacheable views (JS/CSS) must have file extensions, no `$vars`, and no global state (except site URL). Register with `elgg_register_simplecache_view()` at init-time and get URLs via `elgg_get_simplecache_url()`.
- **No Side Effects**: Keep logic out of view templates.

## 4. Actions & Forms
- **Actions**: Namespace files in `actions/` (e.g., `actions/plugin/save.php`). Do not boot Elgg core in action files. Actions are time-sensitive; do not use in emails.
- **Forms**: Place form bodies in `forms/` matching the action name. Use `elgg_view_form()` and input views instead of raw HTML to ensure CSRF protection.

## 5. Events & Hooks
- **Events**: Register in `elgg-plugin.php`. Handlers must return `true`/`false` or modified arrays.
- **Shutdown**: Use the `shutdown` system event instead of `register_shutdown_function`.

## 6. Classes & Vendors
- **Classes**: Place in `classes/` (PSR-0 autoloading). Do not use `.class.php` extensions.
- **Vendors**: Place third-party libraries in `vendors/`.

## 7. Security, I18n & Styling
- **I18n**: Use `elgg_echo('plugin:string')` for all text. No hardcoded strings in views.
- **Security**: Escape runtime variables using `elgg_view()` or PHP sanitizers.
- **Strict Types**: Use `declare(strict_types=1);` in all custom class files.
- **CSS**: Use hyphens (not underscores) in classes/ids.

## 8. Performance & Caching
- **Measure First**: Profile to identify bottlenecks before optimizing.
- **Caching**: Enable Simplecache, System cache, and Boot cache in production. Disable during development.
- **Autoloader**: Optimize Composer autoloader (`optimize-autoloader: true`, `apcu-autoloader: true`).
- **File Serving**: Use X-Sendfile or X-Accel headers for direct file serving if supported.
- **Plugin Quality**: Avoid poorly-behaved plugins that cause site-wide slowdowns.

## 9. JavaScript
- **Modules**: Use native ECMAScript modules (`.mjs`). Load with `elgg_import_esm()`.
- **Third-party Assets**: Map in `elgg-plugin.php` `views` config. Manage via Composer (`npm-asset`).
- **Built-in Modules**: Use `elgg`, `elgg/Ajax`, `elgg/hooks`, `elgg/i18n`, etc.
- **Hooks**: Use `elgg/hooks` for JS interactions, similar to PHP events.
