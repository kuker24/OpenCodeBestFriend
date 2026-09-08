# Playwright QA Workflow Guide

## Exploratory QA Loop

1. **Plan expected flow**: Identify the target URL, required initial state, test data, and pass/fail criteria before launching.
2. **Launch session**: Open the local application using a task-scoped session:
   ```bash
   playwright-cli -s=<task-session> open http://127.0.0.1:3000
   ```
3. **Capture snapshot**: Inspect rendered elements:
   ```bash
   playwright-cli -s=<task-session> snapshot
   ```
   Snapshot outputs elements with stable numeric or ID refs (e.g. `e3`, `e12`).
4. **Interact**: Use semantic locators or refs:
   - Click: `playwright-cli -s=<task-session> click e3`
   - Fill form: `playwright-cli -s=<task-session> fill e5 "example@domain.test"`
   - Key press: `playwright-cli -s=<task-session> press Enter`
   - Select option: `playwright-cli -s=<task-session> select e8 "OptionValue"`
5. **Assert condition**: Never rely on a single screenshot to prove functionality. Verify:
   - Elements are visible and enabled.
   - Text content changes after action.
   - Error messages appear appropriately for invalid input.
   - Fresh snapshot confirms new DOM state.
6. **Capture visual evidence**: When visual confirmation is needed:
   ```bash
   playwright-cli -s=<task-session> screenshot --filename=artifacts/evidence.png
   ```
   For mobile emulation:
   ```bash
   playwright-cli -s=<task-session> open http://127.0.0.1:3000 --mobile
   ```
7. **Clean up**:
   ```bash
   playwright-cli -s=<task-session> close
   ```

## Best Practices & Anti-Patterns

- **No fixed sleep**: Avoid arbitrary `sleep 5` or polling loops. Use snapshot auto-wait and element presence checks.
- **Reference freshness**: Snapshot refs are ephemeral to the session and DOM generation. After significant page changes or navigation, capture a fresh snapshot.
- **Don't touch project configs**: Do not inject Playwright Test runner configuration files into projects that do not have them unless explicitly asked.
