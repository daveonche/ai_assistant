# Elgg Developer Guide: Access Control Lists

Delta distillation of <https://learn.elgg.org/en/stable/guides/access.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/access.rst`, Elgg ref `7.1`). Records only what counters stale
training-data memory: current API names, signatures, defaults, deprecations,
gotchas. Update in place when the stable manual changes.

## Creating an ACL

- Create with `elgg_create_access_collection()`; it returns an
  `ElggAccessCollection`:

```php
$owner_guid = elgg_get_logged_in_user_guid();

$acl = elgg_create_access_collection("Sample name", $owner_guid, 'collection_subtype');
```

## ACL subtypes

- Always set a subtype: it differentiates the ACL's usage and is highly
  recommended.

| Subtype | Owner | Grants |
| :--- | :--- | :--- |
| `group_acl` | `ElggGroup` | group members access content shared with the group |
| `friends` | `ElggUser` | friends access content shared with friends |
| `friends_collection` | `ElggUser` | specific friends access content shared with the ACL |

## Membership

- An ACL grants nothing until users are added: members gain access to content
  whose `access_id` is the ACL's `id`.

```php
// add a member to a created ACL
$acl->addMember($some_other_user_guid);

// remove a member from a fetched ACL
$acl = elgg_get_access_collection($acl_id);
$acl->removeMember($user_guid);
```

## Retrieving an ACL

```php
// by known id
$acl = elgg_get_access_collection($acl_id);

// all ACLs of an owner (procedural / object-oriented)
$acls = elgg_get_access_collections(['owner_guid' => $some_owner_guid]);
$acls = $some_owner_entity->getOwnedAccessCollections();

// filter either form by subtype
$acls = elgg_get_access_collections([
    'owner_guid' => $some_owner_guid,
    'subtype' => 'some_subtype',
]);

// first ACL of an owner with a given subtype (e.g. a group's group_acl)
$acl = $group_entity->getOwnedAccessCollection('group_acl');
```

## Read access

- Elgg automatically adds every ACL a user is a member of to access checks
  when retrieving entities (e.g. listing blogs) — group and friends ACLs
  included.

## Ignoring access

- Wrap code in `elgg_call()` to bypass or adjust access rules. Flags:
  `ELGG_IGNORE_ACCESS` (no access rules applied), `ELGG_ENFORCE_ACCESS`
  (rules forced), `ELGG_SHOW_DISABLED_ENTITIES` (retrieve disabled
  entities), `ELGG_HIDE_DISABLED_ENTITIES` (never retrieve disabled
  entities). Combine flags with `|`:

```php
$entities = elgg_call(ELGG_IGNORE_ACCESS | ELGG_SHOW_DISABLED_ENTITIES, function () {
    return elgg_get_entities([
        'type' => 'user',
    ]);
});
```

## See also

- The manual's Database Access Control reference covers how `access_id` is
  enforced at the database layer.
