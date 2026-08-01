# AIDER.md

Rails API + ActiveAdmin (Ruby 3.3, Rails 6.1).

## Commands

- `bin/dev`: Start server. 
- `bin/rspec`: Run tests.
- `bin/rails` / `bin/bundle`: Wrappers.
- `bundle exec rails code:analysis`: Lint.

## Architecture

- API: `/api/v1/*` (devise_token_auth, Pundit, Jbuilder). Base: `API::V1::APIController`.
- Admin: `/admin/*` (ActiveAdmin, Devise). Base: `ApplicationController`.
- Policies: Pundit (`app/policies/`). `verify_authorized` enforced.
- Jobs: GoodJob.

## Conventions

- Read `.aider-conventions/` (ruby, rails, rspec).
- Use `Time.current`, not `Time.now`.
- Use bang methods (`save!`) or handle boolean.
- HTTP statuses as symbols (`:forbidden`).
- No user-facing strings inline; use locales.

## Debugging

- Do not change test expectations. Fix app logic.
- Wait for user confirmation if hallucinating. 

## Edits

Use strict format:

  ```text
  <<<<<<< ORIGINAL
  old_code
  =======
  new_code
  >>>>>>> UPDATED
