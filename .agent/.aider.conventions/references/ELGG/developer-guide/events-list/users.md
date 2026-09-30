# Elgg Developer Guide: Events List — Users

Category table for the events-list distillation: marker legend and the
behavioral traps live in `../events-list.md`. Distilled from the stable
manual on 2026-09-30 (source: `docs/guides/events-list.rst`, Elgg ref
`7.1`); update in place when the stable manual changes.

## User events

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `ban, user` | | before a user is banned; return `false` to prevent |
| `change:email, user` | results | before the user email is changed; add logic such as extra validation; return `false` to prevent the change right away; params: `user` (`\ElggUser`), `email` (address that passed sanity checks), `request` (`\Elgg\Request`) |
| `invalidate:after, user` | | the account validation has been revoked |
| `login, user` | seq | while a user is being logged in |
| `login:forward, user` | results | filters the URL the user is forwarded to after login |
| `login:first, user` | | after a successful login; only when there is no previous login |
| `logout:after, user` | | after the user logs out |
| `logout:before, user` | | during logout; return `false` to prevent logout |
| `make_admin, user` | | before a user is promoted to admin; return `false` to prevent |
| `profileiconupdate, user` | | user has changed the profile icon |
| `profileupdate, user` | | user has changed the profile |
| `register, user` | results | fired by the `register` action after registration; `register_user()` does *not* trigger it (see traps in `../events-list.md`); return `false` to delete the user; throw `\Elgg\Exceptions\Configuration\RegistrationException` to show a message; params: `user` (newly registered entity) plus all action parameters (`password`, `friend_guid`, `invitecode`, ...) |
| `registeruser:validate:email, all` | results | is `$params['email']` a valid email address; throw `\Elgg\Exceptions\Configuration\RegistrationException` to show a message |
| `registeruser:validate:password, all` | results | is `$params['password']` a valid password; throw `\Elgg\Exceptions\Configuration\RegistrationException` to show a message |
| `registeruser:validate:username, all` | results | is `$params['username']` a valid username; throw `\Elgg\Exceptions\Configuration\RegistrationException` to show a message |
| `remove_admin, user` | | before a user is demoted from admin; return `false` to prevent |
| `unban, user` | | before a user is unbanned; return `false` to prevent |
| `username:character_blacklist, user` | results | filters the blacklisted characters for username validation; return the disallowed characters as a string; default from `$params['blacklist']` |
| `usersettings:save, user` | results | aggregate action saving user settings; return `false` to keep sticky forms (values not saved), `null` on success — never `true` (see traps in `../events-list.md`); params: `user` (`\ElggUser`), `request` (`\Elgg\Request`) |
| `validate, user` | | new accounts start disabled at registration; decide how the user is validated (e.g. email with a validation link) |
| `validate:after, user` | | the account has been validated |
