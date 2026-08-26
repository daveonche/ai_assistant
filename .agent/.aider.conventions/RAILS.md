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

## Ruby Conventions (Rootstrap)

Apply to all Ruby code. Enforced by RuboCop (`.rubocop.yml`).

## Layout

- UTF-8, Unix LF, 2-space indent, max 100 chars, newline at EOF, no trailing whitespace.
- One expression per line (no `;`). No single-line methods (except `def no_op; end`).
- Spaces around operators/commas/colons. No spaces inside `()`, `[]`, around `!`, or in ranges (`1..3`). No space around exponent (`c**2`).
- Indent `when` same as `case`. No trailing commas.
- Blank lines between methods, around access modifiers. No blank lines inside class/method bodies. Max 1 consecutive blank line.
- Align multi-line args after `(`, OR single-indent with `)` on its own line.
- In multi-line chains, keep `.` on the next line.
- Use underscores in big numbers (`1_000_000`). Lowercase prefixes (`0x`).
- No block comments (`=begin`/`=end`). No line continuation `\` (except string concat).

## Syntax

- `::` for constants/constructors only. `def` with parens if params, omit if empty.
- Parens for method args, except no-arg calls, DSLs (`validates`), and keyword-like (`attr_reader`, `puts`).
- Optional args at end. Prefix unused block vars with `_` (`|_k, v|`).
- Avoid parallel assignment (`a, b = 1, 2`) except for swap/destructuring/splat. Use trailing underscore (`a, = foo`).
- Use iterators (`each`), not `for`. No `then` in multi-line `if`. No `while cond do`.
- Favor ternary over `if/then/else` one-liners; don't nest ternaries. Use `if`/`case` as expressions.
- Use `!` not `not`; avoid `!!`. **Banned: `and`/`or`** (use `&&`/`||`).
- Favor modifier `if`/`unless`/`while`/`until` for single-line bodies. Don't nest modifiers.
- Favor `unless` for negatives; favor `until` for negative loops. **Never `unless` with `else`**.
- No parens around control conditions (except safe assignment `if (v = ...)`).
- Use `Kernel#loop` for infinite loops.
- Omit outer `{}` and parens for internal DSLs (`validates :name, presence: true`).
- Omit outer `{}` on trailing options hashes (`user.set(name: 'John')`).
- Use `&:method` shorthand. `{...}` for single-line blocks, `do...end` for multi-line.
- Avoid explicit `return` and `self.` unless required.
- Use `||=` for nil/unset vars (not booleans); `&&=` to preprocess nullable.
- No nested method defs (use lambdas). Lambda: `->(a, b) { ... }`.
- Prefer `proc` over `Proc.new`; use `.call()`.
- Use shorthand self-assignment (`x += y`).
- Don't shadow methods with local vars. Don't use char literals (`?x`).
- Avoid Perl vars (`$;`); use `English` library. No `BEGIN`/`END` (use `at_exit`).
- Use `warn` over `$stderr.puts`. Favor `sprintf`/`format` over `String#%`.
- Use `Array(var)` to coerce. Use ranges/`between?` over `x >= a && x <= b`.
- Use predicate methods (`.even?`, `.nil?`) over `== 0`, `== nil`.
- Guard clauses over nested conditionals; `next` over `if` in loops.
- Prefer: `map` over `collect`, `select` over `find_all`, `find` over `detect`, `reduce` over `inject`, `size` over `length`/`count`.
- `flat_map` over `map.flatten(1)`; `reverse_each` over `reverse.each`.

## Naming

- English, `snake_case` for methods/vars/symbols/files. `CamelCase` for classes/modules (acronyms uppercase: `XMLParser`).
- `SCREAMING_SNAKE_CASE` for constants.
- Predicate methods end with `?`; **no `is_`/`can_`/`does_` prefix**.
- Bang methods (`!`) only if safe counterpart exists.
- Name binary operator params `other` (except `<<` and `[]`).
- One class/module per file, file named `snake_case` after it.

## Comments

- Prefer self-documenting code. Comments in English, capitalized, one space after `#`.
- Refactor bad code instead of explaining. Keep comments updated.
- `TODO:` + description above code. Magic comments (`# frozen_string_literal: true`) at top.

## Classes & Modules

- Layout: `extend`/`include` → inner classes → constants → `attr_*` → macros → class methods → `initialize` → public → protected → private.
- Separate `include` per mixin. Don't nest multi-line classes.
- Prefer modules (`extend self`) over classes with only class methods.
- Use `def self.method`. Omit `self.` for sibling class method calls.
- Always supply `to_s` for domain objects. Use `attr_reader`/`attr_accessor` (no `attr`, no `get_`/`set_`).
- `Struct.new` for trivial value objects (don't inherit).
- Avoid class variables (`@@var`); use class instance variables.
- Indent visibility modifiers at method level with blank lines.
- Prefer composition over inheritance. Apply SOLID.
- `alias` in lexical scope; `alias_method` for runtime.

## Exceptions

- Prefer `raise` over `fail`; `raise SomeException, 'message'`.
- Never `return` from `ensure`. Use implicit `begin` in methods.
- Don't suppress exceptions; no `rescue` in modifier form. No exceptions for flow control.
- **Never `rescue Exception`** — use `rescue StandardError => e` or bare `rescue => e`.
- Specific exceptions higher in rescue chain. Release resources in `ensure` or block form.
- Favor stdlib exceptions. Extract repeated rescue patterns into contingency methods.

## Collections

- Use literals `[]`, `{}`. `%w[]` for word arrays, `%i[]` for symbol arrays (2+ elements).
- Prefer `first`/`last` over `[0]`/`[-1]`. `Set` for unique collections.
- Symbols as hash keys; 1.9 syntax `{ one: 1 }`. Don't mix with hash rockets.
- `Hash#key?` not `has_key?`; `Hash#each_key` not `keys.each`.
- `Hash#fetch` for required keys; block form for expensive defaults.
- `Hash#values_at` for multi-key lookup.
- Don't mutate collection while iterating. Don't use mutable objects as hash keys.
- Prefer `Regexp.last_match(1)` over `Regexp.last_match[1]`.

## Numbers & Strings

- `Integer` for type checks. `rand(1..6)` over `rand(6) + 1`.
- Interpolation `"#{x}"` over concat. `{}` around `@var`/`$var` in interpolation.
- `String#<<` to build large strings. `sub`/`tr` over `gsub` when simpler.
- Squiggly heredocs `<<~END` for multi-line indented strings.

## Date & Time

- Rails: `Time.current`, `Time.zone.now`, `Time.zone.parse`. Avoid `Time.now`/`Time.parse`.
- Non-Rails: `Time.now` over `Time.new`. Use `Date` or `Time`, not `DateTime`.

## Regex

- Plain string ops (`string['text']`) over regex when possible.
- `(?:...)` for non-capturing; named groups `(?<name>...)` over numbered.
- `Regexp.last_match(n)` not `$1`. `\A` / `\z` for full-string boundaries.
- `/x` modifier for complex regexes. `sub`/`gsub` with block/hash for complex replacements.

## Percent Literals

- `%()` for single-line strings needing both interpolation and `"`. Heredocs for multi-line.
- `%r{...}` only when regex contains `/`.
- Brackets: `()` for strings, `[]` for `%w`/`%i`, `{}` for `%r`.
- Avoid `%q`, `%x`, `%s`.

## Metaprogramming

- Avoid needless metaprogramming; don't monkey-patch core classes.
- Prefer block `class_eval` over string form; prefer `define_method`.
- Avoid `method_missing`; if needed, define `respond_to_missing?`, call `super`, catch well-defined prefixes.
- `public_send` over `send`; `__send__` over `send` if receiver may define `send`.

## Misc

- Write `ruby -w` clean code. Avoid hashes as optional params (except initializers).
- Keep methods small (~10 LOC, <5 ideal); params 3-4 max. Max 3 levels of block nesting.
- Code functionally; don't mutate parameters unless that's the method's purpose.
- Prefer module instance variables over globals (`$foo`).
- Be consistent; match surrounding style over strict rule-following.

## RSpec Conventions (Rootstrap)

## Structure

- No blank line after `describe`/`context` opening.
- Group `let`/`subject` together; separate from `before`/`after` with a blank line.
- One blank line around each `it` block.
- Use `before` (not `before(:each)`).

## describe & context

- `describe '#method'` (instance), `describe '.method'` (class).
- `context` must start with `when` or `with`.
- Every `context` needs a matching opposite case.
- Don't end `it` with conditionals; use `context`.

## it / Examples

- **Never start `it` with "should".** State behavior directly.
- One expectation per `it` block.
- Use shared examples instead of iterators.

## let & subject

- Prefer `let` over instance variables.
- `let` is lazy; use `let!` for eager evaluation.
- Use `subject` for a single primary object.

## Matchers

- Use magic matchers (`be_published`).
- Prefer `change` matchers over counting state.
- Test deltas, not incidental state.

## Factories & Fixtures

- Use **FactoryBot**; never Rails fixtures.
- Use **Faker** for fake data.

## Mocking / Stubbing

- Use mocks/stubs sparingly; favor in isolated specs.
- Avoid `allow_any_instance_of`.
- **Never stub a method whose return you're asserting on.**
- Use **Webmock/VCR** for HTTP.

## Shared Examples

- Extract when duplication clarifies intent; don't DRY prematurely.

## Spec Types

- **Model/service/job/mailer**: Unit test public methods/callbacks.
- **Feature**: Full UI flow via Capybara.
- **Request**: Preferred for APIs.
- Prefer `describe` over `feature`/`scenario` DSL.
