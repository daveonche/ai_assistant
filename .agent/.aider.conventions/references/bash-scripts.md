# When writing bash scripts, you MUST follow these principles

- Executables must start with a plain `#!/usr/bin/env bash` shebang.\
  Do not put flags on the shebang line; they are unreliable across platforms.

- Use `set` to enable shell options inside the script so that calling it as\
  `bash script_name` does not break its functionality.

- Start every script with `set -euo pipefail` as the baseline option set;\
  add options beyond it only when needed.

- Shell should only be used for small utilities or simple wrapper scripts.

- If you are writing a script that is more than 100 lines long, or that uses\
  non-straightforward control flow logic, suggest a rewrite in a more\
  structured language now.

- Executables should have a `.sh` extension or no extension.

- Libraries must have a `.sh` extension and should not be executable.

- SUID and SGID are forbidden on shell scripts.

- All error messages should go to `STDERR`.

- Every file must start with a top-level comment that briefly describes its contents.

- A copyright notice and author information are optional.

- Any function that is not both obvious and short must have a function header comment.\
  Any function in a library must have a function header comment regardless of\
  length or complexity.

- It should be possible for someone else to learn how to use your program or\
  to use a function in your library by reading the comments (and self-help,\
  if provided) without reading the code.

- All function header comments should describe the intended API behaviour.

- Description of a function includes\
  `Globals: List of global variables used and modified`\
  `Arguments: Arguments taken`,`Outputs: Output to STDOUT or STDERR`\
  `Returns: Returned values other than the default exit status of last command`.

- Indent 2 spaces. No tabs.

- Maximum line length is 80 characters.

- If you have to write literal strings that are longer than 80 characters,\
  this should be done with a here document or an embedded newline if possible.

- Pipelines should be split one per line if they don’t all fit on one line.\
  If a pipeline all fits on one line, it should be on one line.

- Put `; then` and `; do` on the same line as the `if`, `for`, or `while`.

- `else` should be on its own line and closing statements (`fi` and `done`) should be\
  on their own line vertically aligned with the opening statement.

- Although it is possible to omit `in "$@"` in for loops, we recommend\
  consistently including it for clarity.

- In case statements, indent alternatives by 2 spaces.\
  One-line alternatives need a space after the close parenthesis of the pattern\
  and before the `;;`\
  Long or multi-command alternatives should be split over \
  multiple lines with the pattern, actions, \
  and `;;` on separate lines.

- In order of precedence: Stay consistent with what you find;\
  quote your variables; prefer `"${var}"` over `"$var"`.

- Use `"$@"` unless you have a specific reason to use `"$*"`, such as simply\
  appending the arguments to a string in a message or log.

- Use `$(command)` instead of backticks.

- `[[…]]` is preferred over `[ … ]`, `test`, and `/usr/bin/[`.

- Use quotes rather than filler characters where possible.

- Use an explicit path when doing wildcard expansion of filenames.

- `eval` should be avoided.

- Bash arrays should be used to store lists of elements, to avoid quoting\
  complications. This particularly applies to argument lists.

- Given the choice between invoking a shell builtin and invoking a separate process,\
  choose the builtin.

- Always check return values and give informative return values.

- A function called `main` is required for scripts long enough to contain\
  at least one other function.

- Put all functions together in the file just below constants.\
  Don’t hide executable code between functions.\
  Doing so makes the code difficult to follow and results in nasty surprises \
  when debugging.

- If you’ve got functions, put them all together near the top of the file.\
  Only includes, set statements and setting constants may be done\
  before declaring functions.

- Declare function-specific variables with `local`. Remember that Bash uses\
  dynamic scoping: local variables can be accessed by functions called from\
  the declaring function's body.

- File names should be lowercase, with underscores to separate words if desired.

- Constants and anything exported to the environment should be capitalized,\
  separated with underscores, and declared at the top of the file.

- For the sake of clarity, `readonly` and `export` are recommended\
  over the equivalent `declare` commands.

- Aliases should be avoided in scripts. Use functions instead.

- Always use `(( … ))` or `$(( … ))` rather than `let`, `$[ … ]`, or `expr`.

- Use process substitution or the `readarray` builtin (Bash 4+)\
  in preference to piping to `while`.\
  Pipes create a subshell, so any variables modified within a pipeline\
  do not propagate to the parent shell.

- Function names should be lower-case, with underscores to separate words.\
  Separate libraries with `::`.\
  Parentheses are required after the function name.\
  The `function` keyword is optional, but must be used consistently\
  throughout a project.

- Avoid modifying the values of the following Bash variables in a script:\
  `BASH_VERSION`, `BASH_VERSINFO`, `EUID`, `UID`, `PPID`, `PID`, `PGID`, `SID`,\
  `SHLVL`, `RANDOM`, `LINENO`, `FUNCNAME`, `BASH_SOURCE`, `BASH_LINENO`, `OSTYPE`,\
  `MACHTYPE`, `HOSTTYPE`, `HOSTNAME`, `LINES`, `COLUMNS`, `GROUPS`, `HOME`,\
  `OPTARG`, `OPTIND`, `REPLY`, `SECONDS`, `TERM`, `DEBUG`.

- It's worth noting that Bash variables starting with an underscore \
  (e.g., `_`, `__`, etc.) are generally reserved for internal use and should not\
  be modified.

- When you have a function `main` in the script, wrap the call to `main` as below:

  ```bash
  if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
  fi
  ```

- Every script must have a debug mode that can be enabled from the command line. It can be as simple as `set -x`.

- For a script that uses complex logic, it is a good practice to provide a dry-run \
  mode with the option enabled from the command line.

- Complex scripts must provide a verbose mode enabled using `-v` and `--verbose`\
  from the command line. When verbose mode is enabled, the script must provide\
  detailed information about its execution, including any errors or warnings.

- When sourcing a file (say `include.sh`) for a script that may be executed from anywhere, use the following template:

  ```bash
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  source "$SCRIPT_DIR/include.sh"
  ```

- A script's usage must also include examples.

- Run ShellCheck on every `*.sh` file before committing; treat its warnings\
  as review findings.
