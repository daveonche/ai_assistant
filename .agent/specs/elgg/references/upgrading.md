# Elgg Upgrade Reference

Delta guidance for upgrading Elgg sites, distilled from the official Upgrading
Elgg documentation at <https://learn.elgg.org/en/stable/admin/upgrading.html>.
Load this file via `/read-only` before advising on an Elgg upgrade or planning
work that crosses an Elgg version boundary. General upgrade discipline
(backups, staging validation, rollback planning, plugin compatibility checks)
is assumed from general knowledge; this file records only what that knowledge
does not supply. For plugin code, load the per-transition plugin upgrade
notes from `.agent/specs/elgg/references/upgrade-notes/` — one
`<from>-to-<to>.md` file per documented transition (for example
`1.7-to-1.8.md`, `2.x-to-3.0.md`), matching the official page slugs at
<https://learn.elgg.org/en/stable/appendix/upgrade-notes.html>. Load every
file covering the hops being crossed; if the file for a hop is not present
yet, fall back to the official page for that transition.

The stable page is the single upgrade reference for every site on Elgg
`2.3.*` or later: one procedure, applied one major hop at a time. Only
installations below `2.3.*` use the Manual Upgrade (legacy approach).

## Upgrade path rules

| Starting version | Target | Rule |
| :--- | :--- | :--- |
| Below 2.0 | Next minor | One minor at a time only; manual (legacy) path |
| Same major (2.0) | Higher minor (2.3) | Allowed across any higher minor; manual (legacy) path |
| Previous major, older minor (2.2) | Next major (3.x) | Not allowed; reach the latest minor first |
| `2.3.*` or later | Next major, any minor | Direct hop, no intermediate minors; standard procedure |
| `2.3.*` or later | Several majors ahead | Not allowed in one step; hop one major at a time |

Chain hops major-by-major up to the latest stable version, for example
2.3.17 → 3.3.25 → 4.2.10 → and so on — never 2.3.17 → 7.1.0 in a single
upgrade.

## Standard upgrade procedure (one major hop, from `2.3.*`)

The source page documents this as "From 2.3 to 3.0"; the same steps apply to
every hop. Substitute the target version's constraint wherever `~3.0.0` is
pinned below (same pattern as the patch policy).

### 1. Update `composer.json` (starter-project installs of 2.3)

- Platform requirement: PHP >= 7.0.
- Optionally set autoloader optimization parameters.
- Optionally disable the fxp-asset plugin in favor of asset-packagist.

```json
{
    "config": {
        "platform": { "php": "7.0" },
        "fxp-asset": { "enabled": false },
        "optimize-autoloader": true,
        "apcu-autoloader": true
    },
    "repositories": [
        { "type": "composer", "url": "https://asset-packagist.org" }
    ]
}
```

### 2. Update `.htaccess`

```apache
# find
RewriteRule ^(.*)$ index.php?__elgg_uri=$1 [QSA,L]
# replace with
RewriteRule ^(.*)$ index.php [QSA,L]
```

### 3a. Composer upgrade (recommended)

```bash
composer self-update
composer require elgg/elgg:~3.0.0
composer update
vendor/bin/elgg-cli upgrade async -v
```

If the CLI upgrade fails because database schema changes must be applied
first, execute the Phinx migrations manually
(<https://learn.elgg.org/en/stable/contribute/database.html#contribute-database-execute-migration>).

### 3b. Manual upgrade (legacy approach; below `2.3.*`)

- Major-version hops: overwrite all core files and delete every file removed
  from core — leftovers interfere with proper functioning. Minor or patch:
  overwrite all core files.
- Merge rewrite rules from `install/config/htaccess.dist` into `.htaccess`
  (Apache) or from `install/config/nginx.dist` into the server configuration,
  usually `/etc/nginx/sites-enabled` (Nginx).
- Run `http://your-elgg-site.com/upgrade.php`, then the asynchronous upgrades
  at `http://your-elgg-site.com/admin/upgrades`.
- If `upgrade.php` is unreachable, add
  `$CONFIG->security_protect_upgrade = false;` to `settings.php` and remove it
  after all upgrade steps complete.
- If plugins block the upgrade, add an empty file named `disabled` in `/mod/`
  to disable them, finish the core upgrade, then handle plugins one by one.
- Core modifications must live in plugins to survive the overwrite.

Migrating a dist-package install to composer:

1. Upgrade the current installation using the manual method.
2. Move the codebase to a temporary location.
3. Create a starter-project composer installation in the old root.
4. Copy third-party plugins into `/mod`.
5. Run the installer (browser or `elgg-cli`); at the database step supply the
   same credentials as the manual installation — Elgg detects the existing
   installation and overrides no database values.
6. Optionally commit the new project to version control.

## Applying a patch using Composer

Pin `elgg/elgg` to `~3.y.0`, where `y` is the installed minor version, so
patches install without jumping to the next minor release. Patch definitions
live in the release policy
(<https://learn.elgg.org/en/stable/appendix/releases.html>).

```bash
composer update elgg/elgg --dry-run
composer update elgg/elgg
```
