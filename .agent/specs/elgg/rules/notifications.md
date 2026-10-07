# Elgg Developer Guide: Notifications

Delta distillation of <https://learn.elgg.org/en/stable/guides/notifications.html>,
distilled from the stable manual on 2026-09-30 (source:
`docs/guides/notifications.rst`, Elgg ref `7.1`). Records only what counters stale
training-data memory: current API names, signatures, defaults, deprecations,
gotchas. Update in place when the stable manual changes.

Two ways to send notifications in Elgg: instant notifications, and
event-based notifications sent using the notifications queue.

## Instant notifications

- `elgg_notify_user()` notifies a single user (e.g. someone liked or commented
  the user's post); normally called from an action file.
- Register an instant handler for the event, then notify:

```php
// register a notification handler
elgg_register_notification_event('annotation', 'rating', 'rate', MyNotificationHandler::class);

// now notify the owner
$owner->notify('rate', $rating, [], $user);
```

- The handler extends `\Elgg\Notifications\InstantNotificationEventHandler`
  and overrides the content builders (each takes the recipient and the
  method):

```php
class MyNotificationHandler extends \Elgg\Notifications\InstantNotificationEventHandler {

    protected function getNotificationSubject(\ElggUser $recipient, string $method): string {
        return elgg_echo('ratings:notification:subject');
    }

    protected function getNotificationSummary(\ElggUser $recipient, string $method): string {
        return elgg_echo('ratings:notification:summary', [
            $this->getEventActor()->getDisplayName(),
        ]);
    }

    protected function getNotificationBody(\ElggUser $recipient, string $method): string {
        $object = $this->event->getObject();

        return elgg_echo('ratings:notification:body', [
            $this->getEventActor()->getDisplayName(),
            $object->getEntity()->getOwnerEntity()->getDisplayName(),
            $object->getValue(), // annotation value, e.g. 1-5
        ]);
    }
}
```

- During notification handling the language is automatically switched to the
  recipient's language.

## Enqueued notifications

- On large sites many users may subscribe to one event; sending immediately
  would slow page loads — leave such notifications to the queue.
- Register events with `elgg_register_notification_event()` or in the
  `elgg-plugin.php` `'notifications'` config; notifications are sent
  automatically to all subscribed users.
- Requires the one-minute CRON interval to be configured.

Workflow of the notifications system:

1. Someone does an action that triggers an event: `create`, `update`, or
   `delete` on any `ElggEntity` (e.g. a blog post).
2. The event is saved into the notifications queue in the database.
3. When the one-minute interval handler triggers, the event is taken from the
   queue and processed.
4. Subscriptions are fetched for the user who triggered the event — by
   default all users who have enabled any notification method for themselves
   at `www.site.com/notifications/personal/<username>`.
5. Plugins may alter the subscriptions with the `[get, subscriptions]` event.
6. Plugins may terminate queue processing with the
   `[send:before, notifications]` event.
7. Plugins may alter the notification parameters with the
   `[prepare, notification]` event.
8. Plugins may alter the subject/message/summary with the
   `[prepare, notification:<action>:<type>:<subtype>]` event.
9. Plugins may format subject/message/summary per delivery method with the
   `[format, notification:<method>]` event.
10. Notifications are sent to each subscriber using their chosen methods;
    plugins can take over or prevent each individual notification with the
    `[send, notification:<method>]` event.
11. The `[send:after, notifications]` event fires after all notifications
    have been sent.

Registration example — notify when a new `object` of subtype `photo` is
created:

```php
// elgg-plugin.php
'notifications' => [
    'object' => [
        'photo' => [
            'create' => [
                Elgg\Notifications\NotificationEventHandler::class => [],
            ],
        ],
    ],
],
```

## Custom notification event handlers

- Extend `\Elgg\Notifications\NotificationEventHandler` and overrule the
  builders you need:

| Method | Default / notes |
| :--- | :--- |
| `getSubscriptions(): array` | modify the subscribers; influences the `'get', 'subscribers'` event |
| `getNotificationSubject(\ElggUser $recipient, string $method)` | magic key `notification:<action>:<type>:<subtype>:subject` |
| `getNotificationBody(\ElggUser $recipient, string $method)` | magic key `notification:<action>:<type>:<subtype>:body` |
| `getNotificationSummary(\ElggUser $recipient, string $method)` | default `''` |
| `getNotificationURL(\ElggUser $recipient, string $method)` | default `$event->object->getURL()` |
| `isConfigurableByUser(): bool` (static) | default `true`; `false` hides the event from the user notification settings page |

```php
// elgg-plugin.php
'notifications' => [
    'object' => [
        'photo' => [
            'create' => PhotoAlbumCreateNotificationHandler::class, // extension of \Elgg\Notifications\NotificationEventHandler
        ],
    ],
],
```

### Multiple handlers on one event

- Multiple notification handlers can listen to the same event — useful for
  sending a different message to different recipients:

```php
// elgg-plugin.php
'notifications' => [
    'user' => [
        'user' => [
            'ban' => [
                UserBanNotification::class => [], // notify the banned user
                AdminBanNotification::class => [], // notify site admins
            ],
        ],
    ],
],
```

## Custom notification content via the `prepare` event

```php
function photos_init() {
    elgg_register_notification_event('object', 'photo');
    elgg_register_event_handler('prepare', 'notification:create:object:photo', 'photos_prepare_notification');
}

function photos_prepare_notification(\Elgg\Event $event) {
    $notification_event = $event->getParam('event');

    $entity = $notification_event->getObject();
    $owner = $notification_event->getActor();
    $recipient = $event->getParam('recipient');
    $language = $event->getParam('language');
    $method = $event->getParam('method');

    /* @var $notification \Elgg\Notification\Notification */
    $notification = $event->getValue();

    $notification->subject = elgg_echo('photos:notify:subject', [$entity->getDisplayName()], $language);
    $notification->body = elgg_echo('photos:notify:body', [
        $owner->getDisplayName(),
        $entity->getDisplayName(),
        $entity->getExcerpt(),
        $entity->getURL()
    ], $language);
    $notification->summary = elgg_echo('photos:notify:summary', [$entity->getDisplayName()], $language);

    return $notification;
}
```

- Gotcha: pass the recipient's language into `elgg_echo()` so the
  notification is in the correct language.

## Salutation and sign-off

- Elgg prepends a salutation and appends a sign-off to all outgoing
  notification bodies — no need for text like "Hi Admin," or "Kind regards".
- Prevent it by setting the notification parameter `add_salutation` to
  `false`: in the parameters of `elgg_notify_user()` or in the
  `prepare, notifications` event.
- Change the texts in the translations; customize the views
  `notifications/elements/salutation` and `notifications/elements/sign-off`.

## Notification methods

Default methods: `email`, `delayed_email`, and the bundled site notifications
plugin.

- **Email** — sends an email to the recipient.
- **Delayed email** — saves the notifications and delivers one bundled email
  at the recipient's interval (daily or weekly). Availability is configurable
  by the site administrator in the Site settings. Layout customizable via the
  views `email/delayed_email/plain_text` (plain text part) and
  `email/delayed_email/html` (HTML part).
- **Site notification** — shows the notification on the site.

### Registering a new method and its sender

```php
function sms_notifications_init() {
    elgg_register_notification_method('sms');
    elgg_register_event_handler('send', 'notification:sms', 'sms_notifications_send');
}

function sms_notifications_send(\Elgg\Event $event) {
    /* @var \Elgg\Notifications\Notification $message */
    $message = $event->getParam('notification');

    $recipient = $message->getRecipient();

    if (!$recipient || !$recipient->mobile) {
        return false;
    }

    // (A pseudo SMS API class)
    $sms = new SmsApi();

    return $sms->send($recipient->mobile, $message->body);
}
```

- After registering, the method appears on the notification settings page at
  `www.example.com/notifications/personal/[username]`.

## Subscriptions

- Core usually takes care of subscriptions; notification plugins rarely need
  to alter them.
- Add with `\ElggEntity::addSubscription()`, remove with
  `\ElggEntity::removeSubscription()`.
- Modify the recipients dynamically with the `'get', 'subscriptions'` event:

```php
function discussion_get_subscriptions(\Elgg\Event $event) {
    $reply = $event->getParam('event')->getObject();

    if (!$reply instanceof \ElggDiscussionReply) {
        return;
    }

    $subscriptions = $event->getValue();

    $group_guid = $reply->getContainerEntity()->container_guid;
    $group_subscribers = elgg_get_subscriptions_for_container($group_guid);

    return ($subscriptions + $group_subscribers);
}
```

## Muted notifications

- Mute with `\ElggEntity::muteNotifications($user_guid)` (`$user_guid`
  defaults to the logged-in user): removes all subscriptions on the entity
  and sets a special muted flag.
- Muting rules are applied after the subscribers of a notification event are
  requested, for these entities of the event: the actor
  (`NotificationEvent::getActor()`), the object (`getObject()`), the object's
  container entity, and the object's owner entity.
- Unmute: `\ElggEntity::unmuteNotifications($user_guid)`; check:
  `\ElggEntity::hasMutedNotifications($user_guid)` (both default to the
  logged-in user).
- Helper page to mute based on a notification (e.g. from an email footer):
  the signed route `notifications:mute`, needing `entity_guid` (the entity
  the notification is about) and `recipient_guid`.

## Temporarily disabling notifications

- Users can disable all notifications for a period by setting a start and end
  date in the Notification settings.

## Notification settings

- Store and retrieve with `\ElggUser::setNotificationSetting()` and
  `\ElggUser::getNotificationSettings()`:

```php
// enable 'mail' for the purpose 'group_join' (omitted purpose = 'default')
$user->setNotificationSetting('mail', true, 'group_join');

$settings = $user->getNotificationSettings('group_join');
// ['mail' => true, 'site' => false, 'sms' => false]
```

- Fallback: with no setting yet for a non-default purpose, the system falls
  back to the `default` notification setting.

## Notification management

- When an entity has the `subscribable` capability, menu items to manage the
  subscription are added automatically to the `title` menu; this requires the
  entity to be provided to the page so it is passed to the `title` menu.
