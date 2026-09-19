# Command Suggestions

You are the Command Suggestions prompt. Format suggested CLI commands so an
interactive pager never interrupts the session and so aider can offer to
execute verification commands directly.

## When This Prompt Runs

Apply these rules whenever you suggest CLI commands to the user, after
activation by `$core-command-suggestions`.

## Long-Output Commands

When suggesting CLI commands that may produce long output, prefer
non-interactive forms so an interactive pager does not interrupt the
session:

- For git, prefix with `--no-pager`: suggest
  `git --no-pager status --porcelain` rather than `git status --porcelain`,
  and `git --no-pager show --stat` rather than `git show --stat`.

## Verification Commands

When asking the user to run verification commands:

1. Output each command in a fenced code block tagged with a shell language
   (for example, `bash`), with no prefix such as `/run`, so aider recognizes
   it in the response and offers to execute it directly.
2. Ask the user to reply "done" — do not ask them to paste output manually.

## Gotchas

- The long-output rule applies only to commands that may produce long
  output; do not rewrite short, quiet commands.
- Never ask the user to paste command output into the chat; the "done"
  reply is the handshake.

## Convention Check Reminder

Before creating or editing any file, check the Conventions Reference
Routing table in `.agent/AGENTS.md` and load every matching reference with
`/read-only` before proceeding.
