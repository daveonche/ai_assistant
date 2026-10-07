# Rule: Build hygiene

- Sort multi-line arguments alphanumerically to ease maintenance, avoid
  duplicated packages, and make PRs easier to review. Add a space before
  each line-continuation backslash.
- Exclude build-irrelevant files with `.dockerignore` (pattern syntax
  similar to `.gitignore`).
