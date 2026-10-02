# Removed Views: 2.x to 3.0

Exhaustive enumeration of the 99 views removed in Elgg 3.0, grouped
thematically. Distilled from the official upgrade notes at
<https://learn.elgg.org/en/stable/appendix/upgrade-notes/2.x-to-3.0.html>.
Companion detail file for the canonical note `2.x-to-3.0.md`, which carries
the surrounding narrative and breaking-change guidance.

## Forms and input views

- `forms/account/settings`: usersettings extension can now extend the view
  `forms/usersettings/save`
- `forms/admin/site/advanced/system`
- `forms/admin/site/advanced/security`: the site secret information has been
  moved to `forms/admin/security/settings`
- `forms/invitefriends/invite`: use `forms/friends/invite`
- `invitefriends/form`
- `input/write_access`: mod/pages now uses the **access:collections:write**
  plugin hook

## Page layouts and layout elements

- `page/layouts/content`: use `page/layouts/default`
- `page/layouts/one_column`: use `page/layouts/default`
- `page/layouts/one_sidebar`: use `page/layouts/default`
- `page/layouts/two_sidebar`: use `page/layouts/default`
- `page/layouts/walled_garden`: use `page/layouts/default`
- `page/layouts/walled_garden/cancel_button`
- `page/layouts/two_column_left_sidebar`
- `page/layouts/widgets/add_panel`
- `page/elements/topbar_wrapper`: update your use of `page/elements/topbar`
  to include a check for a logged in user
- `page/elements/by_line`: use `object/elements/imprint`

## Resource views

- `resources/file/download`
- `resources/members/index`
- `resources/avatar/view`: use the entity icon API
- `resources/invitefriends/invite`: use `resources/friends/invite`
- `resources/reportedcontent/add`
- `resources/reportedcontent/add_form`
- `resources/site_notifications/view`: use
  `resources/site_notifications/owner`
- `resources/site_notifications/everyone`: use
  `resources/site_notifications/all`

## River views

Rendering approach is documented in the river guide
(<https://learn.elgg.org/en/stable/guides/river.html>).

- `river/item`: use `elgg_view_river_item()` to render river items
- `river/user/default/profileupdate`
- `river/object/file/create`: see the river guide
- `river/object/page/create`: see the river guide
- `river/object/page_top/create`: see the river guide
- `river/relationship/member`: see the river guide
- `river/object/discussion/create`

## Discussion replies (migrated to comments)

All removed because discussion replies were migrated to comments; see the
"Discussion replies moved to comments" section of the official page and the
canonical note.

- `ajax/discussion/reply/edit`
- `discussion/replies`
- `object/discussion_reply`
- `resources/discussion/reply/edit`
- `resources/elements/discussion_replies`
- `river/elements/discussion_replies`
- `river/object/discussion_reply/create`
- `search/object/discussion_reply/entity`
- `rss/discussion/replies`

## Search views

- `search/header`
- `search/layout`: removed in both `default` and `rss` viewtypes
- `search/no_results`
- `search/object/comment/entity`
- `search/css`: moved to `search/search.css`
- `search/startblurb`

## Notification and subscription views

- `subscriptions/form/additions`: extend `notifications/settings/other`
  instead
- `notifications/subscriptions/personal`
- `notifications/subscriptions/collections`
- `notifications/subscriptions/form`
- `notifications/subscriptions/jsfuncs`
- `notifications/subscriptions/forminternals`
- `notifications/css`

## Group, friend and collection views

- `groups/group_sort_menu`: use the `register, filter:menu:groups/all` plugin
  hook
- `groups/my_status`
- `groups/profile/stats`
- `core/friends/collection`
- `core/friends/collections`
- `core/friends/collectiontabs`
- `core/friends/tablelist`
- `core/friends/talbelistcountupdate`

## Navigation menu views

- `navigation/menu/page`: now uses `navigation/menu/default` and a prepare
  hook
- `navigation/menu/site`: now uses the default view

## Object, output and plugin views

- `object/page_top`: use `object/page`
- `output/checkboxes`: use `output/tags` if you want the same behaviour
- `pages/icon`
- `pages/input/parent`
- `likes/count`: modifications can now be done to the `likes_count` menu item
- `likes/css`: likes now uses `elgg/likes.css`
- `messageboard/css`
- `blog_get_page_content_list`
- `blog_get_page_content_archive`
- `blog_get_page_content_edit`
- `bookmarks/bookmarklet.gif`

## Static assets and graphics

Several removed graphics were re-mapped into the `graphics/` directory.

- `admin.js`
- `aalborg_theme/homepage.png`
- `aalborg_theme/css`
- `ajax_loader.gif`
- `button_background.gif`
- `button_graduation.png`
- `elgg_toolbar_logo.gif`
- `header_shadow.png`
- `powered_by_elgg_badge_drk_bckgnd.gif`
- `powered_by_elgg_badge_light_bckgnd.gif`
- `sidebar_background.gif`
- `spacer.gif`
- `toptoolbar_background.gif`
- `two_sidebar_background.gif`
- `lightbox/elgg-colorbox-theme/colorbox-images/*`
- `ajax_loader_bw.gif`: use `graphics/ajax_loader_bw.gif`
- `elgg_logo.png`: use `graphics/elgg_logo.png`
- `favicon-128.png`: use `graphics/favicon-128.png`
- `favicon-16.png`: use `graphics/favicon-16.png`
- `favicon-32.png`: use `graphics/favicon-32.png`
- `favicon-64.png`: use `graphics/favicon-64.png`
- `favicon.ico`: use `graphics/favicon.ico`
- `favicon.svg`: use `graphics/favicon.svg`
- `friendspicker.png`: use `graphics/friendspicker.png`
- `walled_garden.jpg`: use `graphics/walled_garden.jpg`
