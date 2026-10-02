# Removed JavaScript, Actions and Page Handlers: 2.x to 3.0

Exhaustive enumeration of the JavaScript APIs, page handlers, actions, and
forms/actions removed in Elgg 3.0 — 50 entries across four groups.
Distilled from the official upgrade notes at
<https://learn.elgg.org/en/stable/appendix/upgrade-notes/2.x-to-3.0.html>.
Companion detail file for the canonical note `2.x-to-3.0.md`, which carries
the surrounding narrative and breaking-change guidance.

## Removed page handlers

All core page handlers were removed as part of the routing rework; their
logic moved to resource views (see the Routing section of the canonical
note).

- `file/download`
- `file/search`
- `groupicon`
- `twitterservice`
- `collections/pickercallback`
- `discussion/reply`: see the "Discussion replies moved to comments"
  section of the canonical note
- `expages`
- `invitefriends`: use `friends/{username}/invite`
- `messages/compose`: use `messages/add`
- `reportedcontent`

## Removed actions

- `file/download`: use `elgg_get_inline_url()` or `elgg_get_download_url()`
- `file/delete`: use the `entity/delete` action
- `import/opendd`
- `discussion/reply/save`: see the "Discussion replies moved to comments"
  section of the canonical note
- `discussion/reply/delete`: see the "Discussion replies moved to comments"
  section of the canonical note
- `comment/delete`: use the `entity/delete` action
- `uservalidationbyemail/bulk_action`: use `admin/user/bulk/validate` or
  `admin/user/bulk/delete`
- `uservalidationbyemail/delete`: use `admin/user/bulk/delete`
- `uservalidationbyemail/validate`: use `admin/user/bulk/validate`
- `invitefriends/invite`: use `friends/invite`

## Removed forms and actions

- `notificationsettings/save` form and action
- `notificationsettings/groupsave` form and action
- `discussion/reply/save` form and action

## Removed JavaScript APIs

- `admin.js`
- `elgg.widgets`: use the `elgg/widgets` module — the "widgets" layouts
  load this module automatically
- `lightbox.js`: use the `elgg/lightbox` module as needed
- `lightbox/settings.js`: use the `getOptions, ui.lightbox` JS hook or the
  `data-colorbox-opts` attribute
- `elgg.ui.popupClose`: use the `elgg/popup` module
- `elgg.ui.popupOpen`: use the `elgg/popup` module
- `elgg.ui.initAccessInputs`
- `elgg.ui.river`
- `elgg.ui.initDatePicker`: use the `input/date` module
- `elgg.ui.likesPopupHandler`
- `elgg.embed`: use the `elgg/embed` module
- `elgg.discussion`: use the `elgg/discussion` module
- `embed/custom_insert_js`: use the `embed, editor` JS hook
- `elgg/ckeditor.js`: replaced by `elgg-ckeditor.js`
- `elgg/ckeditor/set-basepath.js`
- `elgg/ckeditor/insert.js`
- `jQuery.cookie`: use `elgg.session.cookie`
- `jquery.jeditable`
- `likes.js`: the `elgg/likes` module is loaded automatically
- `messageboard.js`
- `elgg.autocomplete`: no longer defined
- `elgg.messageboard`: no longer defined
- `jQuery.fn.friendsPicker`
- `elgg.ui.toggleMenu`: no longer defined
- `elgg.ui.toggleMenuItems`: use the `data-toggle` attribute when
  registering toggleable menu items
- `uservalidationbyemail/js.php`: use the `elgg/uservalidationbyemail`
  module
- `discussion.js`: see the "Discussion replies moved to comments" section
  of the canonical note
