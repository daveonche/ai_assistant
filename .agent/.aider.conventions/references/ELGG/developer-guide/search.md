# Elgg Developer Guide: Search

Delta distillation of <https://learn.elgg.org/en/stable/guides/search.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/search.rst`, Elgg ref `7.1`). Records only what counters
stale training-data memory: current API names, signatures, defaults,
deprecations, gotchas. Update in place when the stable manual changes.

Core search centers on `elgg_search()`, which prepares custom search
clauses and utilizes `elgg_get_entities()` to fetch results. The search
plugin exposes it; entity searchability is governed by the `searchable`
entity capability (see `capabilities.md`).

## elgg_search() parameters

In addition to all parameters accepted by `elgg_get_entities()`,
`elgg_search()` accepts:

| Parameter | Meaning |
| :--- | :--- |
| `query` | search query |
| `fields` | array of field names by property type to search in |
| `sort_by` | sorting options array: `property`, `property_type`, `direction` |
| `type` | entity type to search |
| `subtype` | optional entity subtype to search |
| `search_type` | custom search type (required if no `type` is provided) |
| `partial_match` | allow partial matches (default: allowed) |
| `tokenize` | break the query into tokens (default: tokenized) |

Defaults and gotchas:

- `partial_match`: by default partial matches are allowed — `elgg` matches
  when searching for `el`. Exact matches help when matching tag values,
  e.g. finding objects that are `red` and not `darkred`.
- `tokenize`: by default queries are tokenized — `elgg released` matches
  `elgg has been released`.

Example — list all users who list United States as their address or
mention it in their description:

```php
$options = [
   'type' => 'user',
   'query' => 'us',
   'fields' => [
      'metadata' => ['description'],
      'annotations' => ['location'],
   ],
   'sort_by' => [
      'property' => 'zipcode',
      'property_type' => 'annotation',
      'direction' => 'asc',
   ],
];

echo elgg_list_entities($options, 'elgg_search');
```

## Search fields

Customize search fields per entity type/subtype with the `search:fields`
event (typed by entity type, e.g. `user`):

```php
elgg_register_event_handler('search:fields', 'user', 'my_plugin_search_user_fields');
```

The handler receives an `\Elgg\Event` whose value is the fields array
keyed by property type (`metadata`, `annotations`, ...); modify and return
it (e.g. remove `location` from annotations, add `address` to metadata).

- Gotcha: the manual's example unsets
  `unset($fields[$location_key]['annotations'])` after
  `array_search('location', $fields['annotations'])` — as written it does
  not remove the field; the intent is
  `unset($fields['annotations'][$location_key])`.

## Searchable types

Register an entity type for search with
`elgg_entity_enable_capability($type, $subtype, 'searchable')`, or via the
`capabilities` key when defining the entity type in `elgg-plugin.php`.

- Note: the search plugin uses the `searchable` entity capability; it
  defines whether an entity is searchable.

To combine search results or filter how they are presented in the search
plugin:

- `'search:options', 'object:<subtype>'` — extend the search options when
  that subtype is searched (e.g. include `place_review` results whenever
  `place` is searched: append the subtype to `subtypes`, unset the
  singular `subtype` key, return the options; return early when `place` is
  not among the requested subtypes).
- `'search:config', 'type_subtype_pairs'` — filter the presented sections
  (e.g. remove `place_review` from the `object` type/subtype pairs so it
  does not appear as a separate search section).

```php
elgg_entity_enable_capability('object', 'place', 'searchable');
elgg_entity_enable_capability('object', 'place_review', 'searchable');

elgg_register_event_handler('search:options', 'object:place', 'my_plugin_place_search_options');
elgg_register_event_handler('search:config', 'type_subtype_pairs', 'my_plugin_place_search_config');
```

## Custom search types

Elgg core only supports entity search; custom searches (e.g. proximity)
are built from two events:

- `'search:config', 'search_types'` — append the custom type name to the
  value array.
- `'search:options', '<search_type>'` — return the options for that type;
  the query arrives as the `query` event param.

Proximity pattern (query string geocoded, entities ordered by distance):

```php
elgg_register_event_handler('search:options', 'proximity', function (\Elgg\Event $event) {

   $query = $event->getParam('query');
   $options = $event->getValue();

   // Let's presume we have a geocoding API
   $coords = geocode($query);

   // We are not using standard 'selects' options here, because counting
   // queries do not use custom selects
   $options['wheres']['proximity'] = function (QueryBuilder $qb, $alias) use ($lat, $long) {
      $dblat = $qb->joinMetadataTable($alias, 'guid', 'geo:lat');
      $dblong = $qb->joinMetadataTable($alias, 'guid', 'geo:long');

      $qb->addSelect("(((acos(sin(($lat*pi()/180))
                  *sin(($dblat.value*pi()/180)) + cos(($lat*pi()/180))
                  *cos(($dblat.value*pi()/180))
                  *cos((($long-$dblong.value)*pi()/180)))))*180/pi())
                  *60*1.1515*1.60934
                  AS proximity");

      $qb->orderBy('proximity', 'asc');

      return $qb->merge([
         $qb->compare("$dblat.value", 'is not null'),
         $qb->compare("$dblong.value", 'is not null'),
      ]);
   };

   return $options;
});
```

- Distance is computed in SQL over joined `geo:lat`/`geo:long` metadata
  tables and selected as `proximity`; the where clause also requires both
  values to be non-null.
- Gotcha: distance goes through `wheres` + `addSelect`, not the standard
  `selects` option — counting queries do not use custom selects.
- Gotchas in the source example: the `search_types` handler appends
  `'promimity'` (typo — the options handler registers for `proximity`),
  and the closure `use`s `$lat`/`$long` while the geocode result was
  assigned to `$coords`; wire those variables up when adapting the
  example.

## Autocomplete and livesearch endpoint

Core provides JSON endpoints for searching users and groups, used by the
`input/autocomplete` and `input/entitypicker` views:

```php
// Get JSON results of a group search for 'class'
$json = file_get_contents('http://example.com/livesearch/groups?view=json&q=class');
```

Add custom search types by adding a corresponding resource view. Pass a
`handler` (and extra `options`, sent as URL query elements) to
`input/userpicker`:

```php
echo elgg_view('input/userpicker', [
   'handler' => 'livesearch/non_members',
   'options' => [
      'group_guid' => $group_guid,
   ],
]);
```

Enable `/livesearch/non_members` with a view at
`views/json/resources/livesearch/non_members.php`. Pattern:

- Inputs: `limit` (default `elgg_get_config('default_limit')`), `term`
  (fallback `q`), `name`, plus the custom `group_guid`.
- HMAC-protect values passed from the input view so external scripts
  cannot mine data: build the data array, `ksort()` it, then

```php
$hmac = elgg_build_hmac($data);
if (!$hmac->matchesToken(get_input('mac'))) {
   // request does not originate from our input view
   throw new \Elgg\Exceptions\Http\EntityPermissionsException();
}
```

- Set the response header:
  `elgg_set_http_header("Content-Type: application/json;charset=utf-8")`.
- Search options: `query`, `type`, `limit`, `sort` => `name`,
  `order` => `ASC`, `fields` (metadata `name`, `username`),
  `item_view` => `search/entity`, `input_name`, and a `wheres` closure —
  here a `NOT EXISTS` subquery on `entity_relationships` excluding users
  with the `member` relationship to the group:

```php
'wheres' => function (QueryBuilder $qb) use ($group_guid) {
   $subquery = $qb->subquery('entity_relationships', 'er');
   $subquery->select('1')
      ->where($qb->compare('er.guid_one', '=', 'e.guid'))
      ->andWhere($qb->compare('er.relationship', '=', 'member', ELGG_VALUE_STRING))
      ->andWhere($qb->compare('er.guid_two', '=', $group_guid, ELGG_VALUE_INTEGER));

   return "NOT EXISTS ({$subquery->getSQL()})";
},
```

- Output with `echo elgg_list_entities($options, 'elgg_search')`.
