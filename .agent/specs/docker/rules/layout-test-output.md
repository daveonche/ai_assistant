# Rule: Test output discipline

Failed-test output is pasted into the chat for debugging, so it must
stay small enough to paste directly. Run tests quiet, colorless, and
with short tracebacks; save the full run to `.log/` and surface only
the failure summary:

```bash
docker compose run --rm -e NO_COLOR=1 <service> \
    python -m pytest -q --tb=short --no-header \
    > .log/<service>.test.log 2>&1
grep -E '^(FAILED|ERROR)' .log/<service>.test.log
```

- Prefer quiet flags and short tracebacks (`-q --tb=short --no-header`
  for pytest; the framework's equivalents elsewhere). When iterating on
  a single failure, add `-x --maxfail=1`; use `--tb=line` when even
  short tracebacks are more than needed.
- Always disable color (`NO_COLOR=1` or the framework's flag): ANSI
  escape sequences bloat pasted output and add noise.
- Full output belongs in `.log/<service>.test.log` (same flat,
  gitignored `.log/` rule). Paste only the failure lines into the chat:
  failing test IDs plus their assertion messages — the few lines the
  LLM needs to start debugging.
- Need more context? Slice the saved log (`grep -n`, `tail -n 40`) and
  paste the slice. Never re-run the suite verbose to "see more", and
  never paste whole logs.
- The same discipline applies to any verbose in-container command
  (builds, migrations): redirect full output to `.log/` and paste only
  the error lines.
