# Elgg Developer Guide: Database

Delta distillation of <https://learn.elgg.org/en/stable/guides/database.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/database.rst`, Elgg ref `7.1`). Records only what counters stale
training-data memory: current API names, signatures, defaults, deprecations,
gotchas. Update in place when the stable manual changes.

## Creating an object

Instantiate an `ElggObject` (or a registered subclass) and set properties.
Built-in properties:

- `guid` — the entity's GUID; set automatically
- `owner_guid` — the owning user's GUID
- `subtype` — a single-word arbitrary string defining the kind of object,
  e.g. `blog`; make it unique so other plugins don't accidentally use the
  same subtype
- `access_id` — an integer representing the access level
- `title` — the object's title
- `description` — the object's description

It is recommended to register a custom extension of an `\ElggObject` for the
subtype: it makes it easy to set default values (like the subtype), add
custom helper functions, register default form fields, etc. Register the
class in the plugin Bootstrap:

```php
// register a custom class in your plugin Bootstrap
function init() {
    elgg_set_entity_class('object', 'forum', \MyForumObject::class);
}
```

or in the `elgg-plugin.php` entity definition:

```php
'entities' => [
    [
        'type' => 'object',
        'subtype' => 'forum',
        'class' => \MyForumObject::class,
    ],
],
```

The custom class is placed in `/mod/<your_plugin>/classes` (e.g.
`MyForumObject.php`) and overrides `initializeAttributes()`:

```php
class MyForumObject extends \ElggObject {

    /**
      * {@inheritdoc}
      */
    protected function initializeAttributes() {
        parent::initializeAttributes();

        $this->attributes['subtype'] = 'forum';
    }
}
```

Create and save:

```php
$object = new \MyForumObject();
$object->access_id = 2;
$object->save();
```

`access_id` constants (if unset, the object is private and only the creator
can see it):

- `ACCESS_PRIVATE` — only the owner can see it
- `ACCESS_LOGGED_IN` — any logged-in user can see it
- `ACCESS_PUBLIC` — even visitors not logged in can see it

Saving populates `$object->guid` on success. After changing more base
properties, call `$object->save()` again and it updates the database.

Metadata is set like a standard property; assigning an array sets all values
for that metadata (this is how tags are set). Metadata cannot be persisted
until the entity has been saved, but for convenience `ElggEntity` caches it
internally and saves it when saving the entity:

```php
$object->SKU = 62784;
```

## Loading an object

By GUID:

```php
$entity = get_entity($guid);
if (!$entity) {
    // The entity does not exist or you're not allowed to access it.
}
```

By user, subtype or site — the easiest option is `elgg_get_entities()`:

```php
$entities = elgg_get_entities([
    'type' => $entity_type,
    'subtype' => $subtype,
    'owner_guid' => $owner_guid,
]);
```

- Returns an array of `ElggEntity` objects to iterate through.
- Paginates by default: limit `10`, offset `0`.
- Leave out `owner_guid` to get all objects; leave out `subtype` or `type`
  to get objects of all types/subtypes.

With an `ElggUser` in hand (e.g. `elgg_get_logged_in_user_entity()`, which
always has the current user's object when logged in):

```php
$objects = $user->getObjects($subtype, $limit, $offset)
```

By properties — fetch entities by their attributes, metadata, annotations
and relationships using specific parameters in the `$options` array passed
to `elgg_get_entities()`.

## Displaying entities

To display entities in listing functions, provide a view
`EntityType/subtype`, where `EntityType` is one of:

- `object` — entities derived from `ElggObject`
- `user` — entities derived from `ElggUser`
- `site` — entities derived from `ElggSite`
- `group` — entities derived from `ElggGroup`

A default view for all entities already exists: `EntityType/default`.

## Entity icons

Icons can be saved from uploaded files, existing local files, or existing
`ElggFile` objects. These methods save the `master` size defined in the
system; the other defined sizes are generated when requested:

```php
$object = new \ElggBlog();
$object->title = 'Example entity';
$object->description = 'An example object with an icon.';

// from an uploaded file
$object->saveIconFromUploadedFile('file_upload_input');

// from a local file
$object->saveIconFromLocalFile('/var/data/generic_icon.png');

// from a saved ElggFile object
$file = get_entity(123);
if ($file instanceof ElggFile) {
    $object->saveIconFromElggFile($file);
}

$object->save();
```

Default sizes:

- `master` — 10240px at longer edge (not upscaled)
- `large` — 200px at longer edge (not upscaled)
- `medium` — 100px square
- `small` — 40px square
- `tiny` — 25px square
- `topbar` — 16px square

- `elgg_get_icon_sizes()` returns all possible icon sizes for a specific
  entity type and subtype; triggers the `entity:icon:sizes` event.
- `$object->hasIcon($size)` checks whether an icon is set.
- `ElggEntity::getIconURL($params)` retrieves the URL of the generated icon;
  `$params` specifies the size, type, and additional context for the event;
  triggers the `entity:icon:url` event.
- `elgg_view_entity_icon($entity, $size, $vars)` renders an icon; scans in
  order: `views/$viewtype/icon/$type/$subtype.php`,
  `views/$viewtype/icon/$type/default.php`,
  `views/$viewtype/icon/default.php`.

Fallback icon scan when no uploaded icon is found (in this specific order):

1. `views/$viewtype/$icon_type/$entity_type/$entity_subtype.svg`
2. `views/$viewtype/$icon_type/$entity_type/$entity_subtype/$size.gif`
3. `views/$viewtype/$icon_type/$entity_type/$entity_subtype/$size.png`
4. `views/$viewtype/$icon_type/$entity_type/$entity_subtype/$size.jpg`

Where `$viewtype` is the type of view (e.g. `default` or `json`),
`$icon_type` the icon type (e.g. `icon` or `cover_image`), `$entity_type`
the entity type (e.g. `group` or `user`), `$entity_subtype` the entity
subtype (e.g. `blog` or `page`, or `default` if the entity has no subtype),
and `$size` the icon size (not used with svg icons).

Icon methods support passing an icon type when an entity has more than one
icon (e.g. an avatar and a cover photo) — pass `'cover_photo'` as the icon
type:

```php
$object->saveIconFromUploadedFile('uploaded_photo', 'cover_photo');

$object->getIconUrl([
    'size' => 'medium',
    'type' => 'cover_photo'
]);
```

Custom icon types (e.g. cover photos) only have a preset for the `master`
size; to add custom sizes use the `entity:<icon_type>:url` event.

By default icons are stored in `/icons/<icon_type>/<size>.jpg` relative to
the entity's directory on filestore; to provide an alternative location use
the `entity:<icon_type>:file` event.

## Annotations

Annotations can be used, for example, to track ratings:

```php
$blog_post->annotate('rating', 5);
```

- Retrieve the ratings: `$blogpost->getAnnotations('rating')`.
- Delete: operate on the `ElggAnnotation` class, e.g. `$annotation->delete()`.
- Retrieve a single annotation by its ID: `get_annotation()`.
- Deleting an `ElggEntity` of any kind automatically deletes all its
  metadata, annotations, and relationships as well.

## Extending ElggEntity

Deriving from one of the Elgg core classes requires telling Elgg how to
properly instantiate the new type of object so `get_entity()` et al. return
the appropriate PHP class:

```php
// Class source
class Committee extends ElggGroup {

    protected function initializeAttributes() {
        parent::initializeAttributes();
        $this->attributes['subtype'] = 'committee';
    }

    // more customizations here
}
```

In the plugin's `elgg-plugin.php` file add the `entities` section:

```php
<?php // mod/example/elgg-plugin.php
return [
    // entities registration
    'entities' => [
        [
            'type' => 'group',
            'subtype' => 'committee',
            'class' => 'Committee',
            'capabilities' => [
                'searchable' => true,
            ],
        ],
    ],
];
```

The entities are registered upon activation of the plugin; invoking
`get_entity()` with the GUID of a committee object returns an object of type
`Committee`.

## Advanced features

### Entity URLs

Entity URLs are provided by the `getURL()` interface and give the Elgg
framework a common way of directing users to the appropriate display handler
for any given object (e.g. a profile page for users). The URL is set with
`elgg_register_entity_url_handler()`; the registered function must return
the appropriate URL for the given type — itself possibly an address set up
by a page handler. The default handler uses the default export interface.

### Entity loading performance

`elgg_get_entities()` options that can sometimes be useful to improve
performance:

- `preload_owners` — if the fetched entities will be displayed in a list
  with owner information, set to `true` to efficiently load the owner users.
- `preload_containers` — if the fetched entities will be displayed in a list
  using container info, set to `true` to efficiently load them.
- `distinct` — by default Elgg includes a `DISTINCT` modifier on the GUID
  column to guarantee each entity row appears only once in the result set;
  some queries naturally return unique entities, so setting `false` removes
  the modifier and relies on the query to enforce uniqueness. Warning: the
  internals of Elgg entity queries are complex — seek help on the Elgg
  Community site before using the `distinct` option.

## Custom database functionality

It is strongly recommended to use entities wherever possible. However, Elgg
supports custom SQL queries using the database API.

## Systemlog

Note: the manual itself flags this section as needing attention and
containing outdated information.

- The default Elgg system log records what happens within an Elgg system;
  it is viewable and searchable directly from the administration panel.
- A system log row is stored whenever an event concerning an object whose
  class implements the `Loggable` interface is triggered; `ElggEntity` and
  `ElggExtender` implement `Loggable`, so rows are created for all objects,
  users, groups, sites, metadata and annotations.
- Common events: `create`, `update`, `delete`, `login`.
- Reasons for a custom system log: store a full copy of entities when they
  are updated or deleted (auditing), or notify an administrator when certain
  event types occur.
- Gotcha: the manual's example registers the handler with the legacy
  `register_elgg_event_handler('all','all','your_function_name');` — the
  current API is
  `elgg_register_event_handler('all', 'all', 'your_function_name')`.
- The handler receives the object and the event:

```php
function your_function_name($object, $event) {
    if ($object instanceof Loggable) {
        ...
    }
}
```

- Use the extra methods defined by the `Loggable` interface (see
  `/design/loggable`) to extract the information needed.
