---
name: rails-conventions 
description: Rootstrap Rails conventions. Use when writing, reviewing, or editing any Rails code.
paths: "app/**/*.rb,config/**/*.rb,config/**/*.yml,db/**/*.rb,lib/**/*.rb,**/routes.rb" 
---

# Rails Conventions (Rootstrap)

Apply these whenever producing or modifying Rails-specific code.

## Configuration

- Custom init in `config/initializers`; one file per gem.
- Env-specific settings in `config/environments/`; shared in `config/application.rb`.
- Create a `staging` env mirroring production.
- Extra YAML config under `config/`, loaded via `Rails::Application.config_for`.
- Append non-default assets to `config.assets.precompile` in `production.rb`.

## Routing

- Prefer `resources` over custom routes; use `:only`/`:except`.
- `member`/`collection` for extra RESTful actions.
- Use nested routes with `shallow: true` beyond 1 level.
- `namespace` to group related actions.
- Never use wildcard `match ':controller(/:action(/:id(.:format)))'`.
- Avoid `match` unless mapping multiple HTTP verbs via `:via`.

## Controllers

- Keep controllers skinny; no business logic.
- Each action should ideally call only one method beyond an initial `find`/`new`.
- Share at most two instance variables between controller and view.

## Rendering

- Prefer templates/partials over `render inline:`.
- `render plain:` over `render text:`.
- Use HTTP status symbols, not numbers (`:forbidden`).

## Models

- Introduce non-AR model classes freely; short, meaningful names.
- Use ActiveAttr for non-persisted models needing AR-like behavior.
- Keep models for business logic/persistence; move formatting to decorators.

## ActiveRecord

- Don't alter AR defaults without strong reason.
- Group macros at top: `default_scope`, constants, `attr_*`, `enum`, associations, validations, callbacks, other macros.
- Prefer `has_many :through` over `has_and_belongs_to_many`.
- Prefer `self[:attr]` over `read_attribute`/`write_attribute`.
- Use "sexy" validation syntax: `validates :email, presence: true`.
- Extract reused/regex validators into `app/validators` as `EachValidator` subclasses.
- Use named scopes; convert complex parameterized scopes into class methods.
- Beware validation-skipping methods: `update_attribute`, `update_columns`, `update_all`, `increment!`, `toggle`, `touch`, counter methods.
- User-friendly URLs: override `to_param` or use `friendly_id`.
- Use `find_each` for iterating AR collections, not `all.each`.
- Always add `prepend: true` on `before_destroy` callbacks that perform validation.
- Always set `dependent:` on `has_many`/`has_one`.
- Use bang methods (`save!`, `create!`, `update!`) or handle returned status.

## ActiveRecord Queries

- **Never interpolate params into SQL strings.** Use `?` or named placeholders.
- `find(id)` over `where(id: id).take`; `find_by(attrs)` for attribute lookups.
- `where.not(id: id)` over `where("id != ?", id)`.
- Heredocs with `.squish` for explicit SQL in `find_by_sql`.

## Migrations

- Keep `schema.rb` in version control; use `rake db:schema:load` for new DBs.
- Enforce defaults and foreign-key constraints at DB level.
- Use `change` for constructive migrations; `up`/`down` for non-reversible ones.
- If using a model inside a migration, redefine it with explicit `table_name`.
- Name foreign keys explicitly (e.g. `name: :articles_author_id_fk`).
- Avoid `FLOAT` for rational numbers; use `DECIMAL` or base-unit integer.

## Views

- Never call models directly from views.
- Complex formatting → decorators.
- Use partials and layouts to deduplicate.

## Internationalization

- No user-facing strings in views/models/controllers; move to `config/locales`.
- `activerecord` scope for model/attribute translations.
- Organize locales into `locales/models` and `locales/views`.
- Short forms `I18n.t` / `I18n.l`.
- Lazy lookup (`t '.title'`) in views; dot-separated keys elsewhere.

## Assets

- `app/assets` → app-specific.
- `lib/assets` → in-house libs.
- `vendor/assets` → third-party.
- Prefer gemified assets.

## Mailers

- Name classes `SomethingMailer`; provide HTML and plain-text templates.
- `config.action_mailer.raise_delivery_errors = true` in development.
- Local SMTP (Mailcatcher/Letter Opener) in development.
- Set `default_url_options[:host]` per environment. 
- Always use `_url` helpers (not `_path`) in email bodies.
- Format `default from:` as `'Your Name <info@your_site.com>'`.
- Test env: `delivery_method = :test`; dev/prod: `:smtp`.
- Inline CSS for HTML emails (use `premailer-rails` or `roadie`).
- Send emails in background jobs; never inline during request.

## Active Support Core Extensions

- Prefer `&.` over `try!`.
- Prefer stdlib (`start_with?`, `end_with?`, `include?`) over AS aliases.
- Prefer plain comparisons over `inquiry`, `Numeric#positive?`/`negative?`.

## Time

- Set `config.time_zone` in `application.rb`.
- **Never use `Time.parse` or `Time.now`.** Use `Time.zone.parse`, `Time.zone.now`, or `Time.current`.

## Bundler

- Dev/test gems in proper Gemfile groups.
- Prefer well-established gems.
- Group OS-specific gems under `darwin` / `linux` and use `Bundler.require(platform)`.
- **Never remove `Gemfile.lock` from version control.**

## Managing Processes

- Use `foreman` to manage multiple external processes.

## Logging

- Pass a block to `Rails.logger.debug` when interpolating to avoid string-building at suppressed levels.
