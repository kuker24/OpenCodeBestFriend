---
name: click-path-audit
description: Trace each user-facing control through its handler and shared-store writes to find sequential undo, async races, stale closures, and missing transitions. Use when buttons look wired but do nothing, or after a refactor of shared UI state. Not for exploratory browser QA (playwright-qa), ordinary red-green bugs (diagnosing-bugs), or visual layout (impeccable).
compatibility: opencode
license: MIT
---

# Click-Path Audit

Find interaction bugs that unit-shaped checks miss: handlers whose later calls undo earlier writes, races, and labels that promise a state the store never reaches.

## Boundaries & Handoffs

| Need | Route |
|---|---|
| Exploratory browser click-through | `playwright-qa` |
| Unknown defect with a red reproduction | `diagnosing-bugs` |
| Visual hierarchy or layout | `impeccable` |
| Chrome motion after the state is correct | `emil-design-eng` |
| **Handler vs shared-store sequential undo and final-state mismatch** | **`click-path-audit`** |

## Procedure

Consult [references/patterns.md](references/patterns.md) for the six conflict patterns.

1. **Map stores first.** For each action: fields set, fields reset as side effects. Flag actions that clear state they do not own.
2. **Audit each touchpoint in scope.** Identify the handler. Trace every call in order. Record reads, writes, resets. Check whether a later call undoes an earlier write. Check whether the final state matches the control's label. Check async order.
3. **Report** with file:line, pattern name, expected vs actual, and a specific fix.

Scope tightly. Full-app audits split by page only after the store map exists. Store-focused audits cover every consumer of a changed action.

Do not treat "handler exists and does not throw" as proof the button works.

## Output

```text
CLICK-PATH-NNN: [CRITICAL|HIGH|MEDIUM|LOW]
  Touchpoint / Pattern / Handler / Trace / Expected / Actual / Fix
```
