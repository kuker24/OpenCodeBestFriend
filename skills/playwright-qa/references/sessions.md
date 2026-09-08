# Playwright QA Session Management

## Session Isolation Policy

1. **Workspace / Task Scoping**:
   - Every task must provide `-s=<session-name>` or `--session=<session-name>`.
   - Name format: alphanumeric with hyphens, e.g. `qa-<feature>-<timestamp>`.
   - Never omit `-s=` unless in an interactive one-off debugging session.

2. **No Collisions**:
   - Two concurrent tasks must not use the same session identifier.
   - Profile data and cookies remain segregated per named session.

3. **Cleanup Discipline**:
   - When finishing a QA flow, close only the session you opened:
     ```bash
     playwright-cli -s=<task-session> close
     ```
   - If session data needs explicit deletion:
     ```bash
     playwright-cli -s=<task-session> delete-data
     ```
   - **Banned commands**: `playwright-cli close-all` and `playwright-cli kill-all` are strictly forbidden in shared or multi-agent workspaces because they kill processes belonging to other tasks.

4. **Failure & Interruption Handling**:
   - When a test flow errors or times out, close the active session in the finally/teardown step.
   - Do not leave orphan headless browser processes running.

5. **Artifacts & Data Hygiene**:
   - Keep screenshots and trace files inside `.scratch/` or project-designated test artifact directories.
   - Ensure all generated session artifacts are gitignored.
