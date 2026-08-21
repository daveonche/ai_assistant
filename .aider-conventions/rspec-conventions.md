--- 
name: rspec-conventions
description: Rootstrap RSpec conventions. Use when writing, reviewing, or editing RSpec test files.
paths: "spec/**/*_spec.rb,spec/rails_helper.rb,spec/spec_helper.rb,spec/support/**/*.rb,spec/factories/**/*.rb"
--- 

# RSpec Conventions (Rootstrap)

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
