# Rule: Log capture

- `.log/` is gitignored. Create the directory once as the invoking user
  (`mkdir -p .log`); per-service files are created on demand by the
  capture commands below. Do not rely on Compose to auto-create `.log/`:
  a missing short-syntax bind-mount host path is created as root on
  Linux, which can block non-root container users from writing.
- Capture a service's output (errors included) into its log file:

  ```bash
  docker compose logs -f --tail=0 <service> >> .log/<service>.log 2>&1
  ```

- Error-only capture, appending into the same per-service log file:

  ```bash
  docker compose logs <service> 2>&1 | grep -iE 'error|fatal|exception' >> .log/<service>.log
  ```

  Use a distinct `.log/<service>.errors.log` instead if error-only lines
  must not interleave with the full log.
- Apps that write their own log files write them into the mounted `.log/`
  directory as `/app/logs/<service>.log` — one file per service, matching
  the host layout.

Never bind-mount a single log file
(`./.log/web.log:/app/logs/web.log`): if the host file does not exist
yet, Docker creates a *directory* at that path, and editors that
save-by-rename break single-file mounts. Mount `.log/` as a whole.
Forgetting `2>&1` drops stderr from the captured log file.
