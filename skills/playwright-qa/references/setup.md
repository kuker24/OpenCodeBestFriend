# Playwright QA Runtime Setup & Boundaries

## Separation of Concerns

1. **Tool vs Application Dependency**:
   - Playwright CLI is an agent verification tool, NOT an application runtime or production dependency.
   - Do NOT add `playwright`, `playwright-cli`, or `@playwright/test` to the user's `package.json` just to run exploratory QA.

2. **Runtime Discovery**:
   - Check if `playwright-cli` is already available on `PATH`:
     ```bash
     command -v playwright-cli
     ```
   - Check if the project has a local CLI binary:
     ```bash
     test -f node_modules/.bin/playwright-cli
     ```
   - Do NOT run `npx @playwright/cli` with unpinned packages or without checking network/sandbox constraints.
   - Do NOT assume Playwright CLI agent interface is available merely because `@playwright/test` is installed in `node_modules`.

3. **Status Reporting**:
   - When Playwright CLI is missing: report `NOT_CONFIGURED` or `OPTIONAL_ABSENT` honestly.
   - Do not claim browser tests passed if the CLI or browser binary was not run.
   - Do not trigger automated downloads during `opencode-bf doctor` or status probes.

4. **Explicit Tool Installation (When Requested by User)**:
   - If the user explicitly asks to install Playwright CLI tool:
     ```bash
     npm install -g @playwright/cli@0.1.0 # or pinned version
     ```
   - Browser installation:
     ```bash
     playwright install chromium
     ```
   - Never download WebKit or Firefox unless the project explicitly targets them.
