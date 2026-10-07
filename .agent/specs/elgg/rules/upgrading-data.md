# Elgg Developer Guide: Upgrading Data

Delta distillation of <https://learn.elgg.org/en/stable/guides/upgrading-data.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/upgrading-data.rst`, Elgg ref `7.1`). Records only what counters
stale training-data memory: current API names, signatures, defaults,
deprecations, gotchas. Update in place when the stable manual changes.

The page (titled "Writing a plugin upgrade" in the manual) covers plugin
data upgrades: a plugin needs to change the contents or structure of data
it has stored in the database or the dataroot — e.g. converting to a more
efficient or flexible structure, or fixing data saved invalidly due to a
bug. Migrations can take a long time with much data, so Elgg provides the
`Elgg\Upgrade\AsynchronousUpgrade` class for implementing long-running
upgrades.

## Declaring a plugin upgrade

- A plugin communicates the need for an upgrade under the `upgrades` key
  in `elgg-plugin.php`. Each value must be the fully qualified name of an
  upgrade class extending `Elgg\Upgrade\AsynchronousUpgrade`.
- Example from `mod/blog/elgg-plugin.php`:

```php
return [
   'upgrades' => [
      Blog\Upgrades\AccessLevelFix::class,
      Blog\Upgrades\DraftStatusUpgrade::class,
   ]
];
```

- The class names refer to `mod/blog/classes/Blog/Upgrades/AccessLevelFix`
  and `mod/blog/classes/Blog/Upgrades/DraftStatusUpgrade`.
- Note: Elgg core upgrade classes can be declared in
  `engine/lib/upgrades/async-upgrades.php`.
- Gotcha: the `upgrades` key is documented on this page; it is not among
  the `elgg-plugin.php` sections listed in `plugins.md`.

## The upgrade class

A class extending `Elgg\Upgrade\AsynchronousUpgrade` has a lot of freedom
in how it processes the data, but must declare some constant variables and
mark whether each processed item was upgraded successfully:

```php
<?php

namespace Blog\Upgrades;

use Elgg\Upgrade\AsynchronousUpgrade;
use Elgg\Upgrade\Result;

/**
 * Fixes invalid blog access values
 */
class AccessLevelFix extends AsynchronousUpgrade {

   /**
    * Version of the upgrade
    *
    * @return int
    */
   public function getVersion() {
      return 2016120300;
   }

   /**
    * Should the run() method receive an offset representing all processed items?
    *
    * @return bool
    */
   public function needsIncrementOffset() {
      return true;
   }

   /**
    * Should this upgrade be skipped?
    *
    * @return bool
    */
   public function shouldBeSkipped() {
      return false;
   }

   /**
    * The total number of items to process in the upgrade
    *
    * @return int
    */
   public function countItems() {
      // return count of all blogs
   }

   /**
    * Runs upgrade on a single batch of items
    *
    * @param Result $result Result of the batch (this must be returned)
    * @param int    $offset Number to skip when processing
    *
    * @return Result Instance of \Elgg\Upgrade\Result
    */
   public function run(Result $result, $offset) {
      // fix 50 blogs skipping the first $offset
   }
}
```

- Warning: do not assume when your class will be instantiated or when/how
  often its public methods will be called.

## Class methods

### getVersion()

Must return an integer representing the date the upgrade was added, in
format `yyyymmddnn`:

- `yyyy` — year; `mm` — month (leading zero); `dd` — day (leading zero);
  `nn` — incrementing number (starting from `00`) used when two separate
  upgrades are added during the same day.
- Gotcha: the prose says "eight digits" but the format `yyyymmddnn` (and
  the example `2016120300`) is ten digits.

### shouldBeSkipped()

Should return `false` unless the upgrade won't be needed.

- Warning: if `true` is returned the upgrade cannot be run later.

### needsIncrementOffset()

- `true`: `run()` receives as `$offset` the number of items already
  processed — useful when only modifying data and `$offset` is needed in
  e.g. `elgg_get_entities()` to know how many have been handled.
- `false`: `run()` receives as `$offset` the total number of failures —
  use when the process deletes or moves data out of the way of the process
  (e.g. deleting 50 objects on each `run()` needs no `$offset`).

### countItems()

Total number of items to process during the upgrade. If unknown,
`Batch::UNKNOWN_COUNT` can be returned, but then `run()` must manually
mark the upgrade complete.

### run()

Performs a portion of the actual upgrade; depending on how long it takes,
it may be called multiple times during a single request. Receives:

- `$result` — an `Elgg\Upgrade\Result` instance.
- `$offset` — where the next upgrade portion should start (or the total
  number of failures, per `needsIncrementOffset()`).

For each item processed, call exactly one of:

- `$result->addSuccesses()` — the item was upgraded successfully.
- `$result->addFailures()` — it failed to upgrade the item.

Both default to one item, but you can optionally pass in the number of
items. Additionally, set as many error messages as necessary:
`$result->addError("Error message goes here")`.

If `countItems()` returned `Batch::UNKNOWN_COUNT`, then at some point
`run()` must call `$result->markComplete()` to finish the upgrade.

In most cases `run()` passes `$offset` to one of the `elgg_get_entities()`
functions:

```php
public function run(Result $result, $offset) {
   $blogs = elgg_get_entitites([
      'type' => 'object'
      'subtype' => 'blog'
      'offset' => $offset,
   ]);

   foreach ($blogs as $blog) {
      if ($this->fixBlogPost($blog)) {
         $result->addSuccesses();
      } else {
         $result->addFailures();
         $result->addError("Failed to fix the blog {$blog->guid}.");
      }
   }

   return $result;
}
```

- Gotchas in the source example: the function is misspelled
  `elgg_get_entitites` (correct: `elgg_get_entities`), and the options
  array is missing commas after `'object'` and `'blog'`.

### getUpgrade()

Use this function to get the related `ElggUpgrade` entity that is related
to this upgrade.

## Administration interface

Each upgrade extending `Elgg\Upgrade\AsynchronousUpgrade` is listed in the
admin panel after triggering the site upgrade from the Administration
dashboard. While running the upgrades, Elgg provides:

- Estimated duration of the upgrade
- Count of processed items
- Number of errors
- Possible error messages
