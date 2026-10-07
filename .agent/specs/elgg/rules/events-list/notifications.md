# Elgg Developer Guide: Events List — Notifications

Category table for the events-list distillation: marker legend and the
behavioral traps live in `../events-list.md`. Distilled from the stable
manual on 2026-09-30 (source: `docs/guides/events-list.rst`, Elgg ref
`7.1`); update in place when the stable manual changes.

## Queue events

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `dequeue, notifications` | | called when an `ElggData` object is removed from the notifications queue to be processed |
| `enqueue, notifications` | | called when an `ElggData` object is being added to the notifications queue |

## Notification event lifetime

Listed chronologically below; all apply to both subscription and instant
notifications except `enqueue, notification`, which concerns subscription
notifications only.

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `enqueue, notification` | results | return `false` to prevent a subscription notification event from being enqueued; `$params`: `object` (object of the notification event), `action` (action that triggered it, e.g. `publish` for `elgg_trigger_event('publish', 'object', $object)`) |
| `get, subscriptions` | results | filters the subscribers of the notification event; default subscribers are the users subscribed to the event object's container (subscription events) or the recipient passed to `elgg_notify_user()` (instant notifications); handlers must return an array mapping user GUIDs to delivery methods, e.g. `<guid> => ['sms']` or `<guid> => ['email', 'sms', 'ajax']`; always validate the event, object, and action before adding recipients — see traps in `../events-list.md`; `$params`: `event` (`\Elgg\Notifications\NotificationEvent`), `origin` (`subscriptions_service` or `instant_notifications`), `methods_override` (delivery-method preference for instant notifications), `handler` (`\Elgg\Notifications\NotificationEventHandler`) |
| `send:before, notifications` | results | triggered before the notification event queue is processed; can be used to terminate the notification event; `$params`: `event`, `subscriptions` (see `get, subscriptions`), `handler` |
| `prepare, notification` | results | high-level filter for the `\Elgg\Notifications\Notification` before it is sent; fires after `send:before, notifications` and before the granular `prepare, notification:<action>:<entity_type>:<entity_subtype>`; return the altered notification object; `$params` vary by notification type and may include `event`, `object` (can be `null` for instant notifications), `action` (defaults to `notify_user` for instant notifications), `method`, `sender`, `recipient`, `language`, `origin`, `handler` |
| `prepare, notification:<action>:<entity_type>:<entity_subtype>` | results | granular filter for the notification before delivery; for instant notifications without an object the event fires as `prepare, notification:<action>`; a missing action name defaults to `notify_user`; same `$params` as `prepare, notification` |
| `format, notification:<method>` | results | formats the notification before it is passed to `send, notification:<method>`; return the `\Elgg\Notifications\Notification`; receives no `$params`; use cases: strip tags for plaintext email, inline HTML styles for HTML email, wrap in a template or add a signature |
| `send, notification:<method>` | results | delivers the notification; the handler must return `true` or `false` indicating delivery success; `$params`: `notification` (`\Elgg\Notifications\Notification`) |
| `send:after, notifications` | results | triggered after all notifications in the queue for the notification event have been processed; `$params`: `event`, `subscriptions`, `deliveries` (delivery-status matrix by user and method), `handler` |

## Email events

| Event | Marker | Notes |
| :--- | :--- | :--- |
| `prepare, system:email` | results | triggered by `elgg_send_email()`; alter the `\Elgg\Email` (sender, recipient, subject, body, and/or headers) before it is passed to the email transport; `$params` are empty; return the `\Elgg\Email` |
| `transport, system:email` | results | implement a custom transport (e.g. a third-party proxy service such as SendGrid or Mailgun); return `true` to indicate the email was transported; `$params`: `email` (`\Elgg\Email`) |
| `validate, system:email` | results | suppress or whitelist outgoing emails (e.g. while the site is in development mode); return `false` to suppress delivery; `$params`: `email` (`\Elgg\Email`) |
| `message, system:email` | results | triggered by the default email transport (Elgg uses `symfony/mailer`); alter the `\Symfony\Component\Mime\Email` before it is passed to the Symfony transport; applies only to emails not transported via `transport, system:email`; `$params`: `email` (`\Elgg\Email`) |
