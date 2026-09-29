# Plugin Upgrade Notes: 3.x to 4.0 — Exceptions and Traits

Exhaustive enumeration of the reworked exceptions and relocated traits in
the 3.x to 4.0 transition, distilled from
<https://learn.elgg.org/en/stable/appendix/upgrade-notes/3.x-to-4.0.html>.
Load this file on demand from the main `3.x-to-4.0.md` notes when updating
`catch` blocks, `use` imports, or trait references after an upgrade.

## Exceptions

All exceptions in the Elgg system now extend `Elgg\Exceptions\Exception`
and live in the `Elgg\Exceptions` namespace.

### Moved exceptions

- `ClassException` — use `Elgg\Exceptions\ClassException`
- `ConfigurationException` — use `Elgg\Exceptions\ConfigurationException`
- `CronException` — use `Elgg\Exceptions\CronException`
- `DatabaseException` — use `Elgg\Exceptions\DatabaseException`
- `DataFormatException` — use `Elgg\Exceptions\DataFormatException`
- `InstallationException` — use
  `Elgg\Exceptions\Configuration\InstallationException`
- `InvalidParameterException` — use
  `Elgg\Exceptions\InvalidParameterException`
- `IOException` — use `Elgg\Exceptions\FileSystem\IOException`
- `LoginException` — use `Elgg\Exceptions\LoginException`
- `PluginException` — use `Elgg\Exceptions\PluginException`
- `SecurityException` — use `Elgg\Exceptions\SecurityException`
- `Elgg\Database\EntityTable\UserFetchFailureException` — use
  `Elgg\Exceptions\Database\UserFetchFailureException`
- `Elgg\Di\FactoryUncallableException` — use
  `Elgg\Exceptions\Di\FactoryUncallableException`
- `Elgg\Di\MissingValueException` — use
  `Elgg\Exceptions\Di\MissingValueException`
- `Elgg\Http\Exception\AdminGatekeeperException` — use
  `Elgg\Exceptions\Http\Gatekeeper\AdminGatekeeperException`
- `Elgg\Http\Exception\AjaxGatekeeperException` — use
  `Elgg\Exceptions\Http\Gatekeeper\AjaxGatekeeperException`
- `Elgg\Http\Exception\GroupToolGatekeeperException` — use
  `Elgg\Exceptions\Http\Gatekeeper\GroupToolGatekeeperException`
- `Elgg\Http\Exception\GatekeeperException` — use
  `Elgg\Exceptions\Http\Gatekeeper\GatekeeperException`
- `Elgg\Http\Exception\LoggedInGatekeeperException` — use
  `Elgg\Exceptions\Http\Gatekeeper\LoggedInGatekeeperException`
- `Elgg\Http\Exception\LoggedOutGatekeeperException` — use
  `Elgg\Exceptions\Http\Gatekeeper\LoggedOutGatekeeperException`
- `Elgg\Http\Exception\UpgradeGatekeeperException` — use
  `Elgg\Exceptions\Http\Gatekeeper\UpgradeGatekeeperException`
- `Elgg\I18n\InvalidLocaleException` — use
  `Elgg\Exceptions\I18n\InvalidLocaleException`
- `Elgg\BadRequestException` — use
  `Elgg\Exceptions\Http\BadRequestException`
- `Elgg\CsrfException` — use `Elgg\Exceptions\Http\CsrfException`
- `Elgg\EntityNotFoundException` — use
  `Elgg\Exceptions\Http\EntityNotFoundException`
- `Elgg\EntityPermissionsException` — use
  `Elgg\Exceptions\Http\EntityPermissionsException`
- `Elgg\GatekeeperException` — use
  `Elgg\Exceptions\Http\Gatekeeper\GatekeeperException`
- `Elgg\GroupGatekeeperException` — use
  `Elgg\Exceptions\Http\Gatekeeper\GroupGatekeeperException`
- `Elgg\HttpException` — use `Elgg\Exceptions\HttpException`
- `Elgg\PageNotFoundException` — use
  `Elgg\Exceptions\Http\PageNotFoundException`
- `Elgg\ValidationException` — use
  `Elgg\Exceptions\Http\ValidationException`
- `Elgg\WalledGardenException` — use
  `Elgg\Exceptions\Http\Gatekeeper\WalledGardenException`

### Removed exceptions

- `CallException`
- `ClassNotFoundException`
- `IncompleteEntityException`
- `InvalidClassException`
- `NotificationException`
- `NotImplementedException` — from the Web Services plugin

## Traits

In order to better organize the Elgg namespace all traits have been moved to
the `Elgg\Traits` namespace:

- `Elgg\Cacheable` moved to `Elgg\Traits\Cacheable`
- `Elgg\Cli\PluginsHelper` moved to `Elgg\Traits\Cli\PluginsHelper`
- `Elgg\Cli\Progressing` moved to `Elgg\Traits\Cli\Progressing`
- `Elgg\Database\Seeds\Seeding\GroupHelpers` moved to
  `Elgg\Traits\Seeding\GroupHelpers`
- `Elgg\Database\Seeds\Seeding\TimeHelpers` moved to
  `Elgg\Traits\Seeding\TimeHelpers`
- `Elgg\Database\Seeds\Seeding` moved to `Elgg\Traits\Seeding`
- `Elgg\Database\LegacyQueryOptionsAdapter` moved to
  `Elgg\Traits\Database\LegacyQueryOptionsAdapter`
- `Elgg\Debug\Profilable` moved to `Elgg\Traits\Debug\Profilable`
- `Elgg\Di\ServiceFacade` moved to `Elgg\Traits\Di\ServiceFacade`
- `Elgg\Entity\ProfileData` moved to `Elgg\Traits\Entity\ProfileData`
- `Elgg\Loggable` moved to `Elgg\Traits\Loggable`
- `Elgg\Notifications\EventSerialization` moved to
  `Elgg\Traits\Notifications\EventSerialization`
- `Elgg\TimeUsing` moved to `Elgg\Traits\TimeUsing`
