# SKILL: elgg-conventions (Engine Production Guardrails)

## 1. FILE & ARCHITECTURE LAYOUT

- Plugin configurations and registrations MUST live inside the root `elgg-plugin.php` manifest file.
- DO NOT write custom raw SQL wrappers or call PHP native raw data queries. Always route through the database layer via `elgg_get_entities()` or `elgg_get_metadata()`.
- Explicitly declare strict type paradigms (`declare(strict_types=1);`) at the head of every custom class file.

## 2. ENTITIES & RELATIONSHIPS

- Interrogate states safely via custom typed entity classes extending `ElggEntity`, `ElggObject`, or `ElggUser`.
- Secure access states by using the built-in system security contexts (`elgg_call(ELGG_IGNORE_ACCESS, ...)`), rather than disabling global system visibility configurations manually.
- Use explicit deletion hooks to clean up metadata states and relationships, preventing database corruption when removing content elements.

## 3. EVENT DRIVEN PARADIGM (HOOKS)

- Register user activities and system event listeners exclusively through `elgg-plugin.php` using correct event keys.
- Event handlers MUST return a boolean value (`true`/`false`) or modified context arrays cleanly to prevent blocking downstream callbacks.
- DO NOT create structural runtime side effects directly inside view templates; use dedicated event controllers.

## 4. ROUTING, CONTROLLERS, & UI

- Define clean paths via the `actions` array wrapper in your plugin configuration. Include `access: 'public'` or `access: 'logged_in'` strictly.
- Format all presentation assets into modular view files under the `views/default/` folder hierarchy.
- Use `elgg_view_field()` components for form building instead of raw HTML input fields to natively enforce system token anti-CSRF protection.

## 5. INTERNATIONALIZATION & SECURITY

- DO NOT leave text strings hardcoded inside views. Register localization objects in your plugin language module (`languages/en.php`) and parse them via `elgg_echo('plugin:string')`.
- Prevent execution layer vulnerabilities by escaping all runtime variables processed in layout strings using `elgg_view()` escaping properties or PHP sanitizers.
