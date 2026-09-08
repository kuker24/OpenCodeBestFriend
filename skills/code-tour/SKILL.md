---
name: code-tour
description: Create CodeTour `.tour` files — persona-targeted walkthroughs with verified file and line anchors under `.tours/`. Use for onboarding, architecture, PR, RCA, or "explain how this works" when a reusable guided artifact is wanted. Not for chat-only explanations, prose docs (technical-writing), or implementation work.
compatibility: opencode
license: MIT
---

# Code Tour

Write CodeTour JSON under `.tours/`. Tours open real files and line ranges. Do not modify source as part of this skill.

## Boundaries & Handoffs

| Need | Route |
|---|---|
| One-off explanation in chat | answer directly; no tour |
| Prose documentation structure | `/technical-writing` |
| Implementation or refactor | do the work; do not start a tour |
| **Reusable `.tour` walkthrough with file anchors** | **`code-tour`** |

## Procedure

Consult [references/format.md](references/format.md) for step types and `ref`.

1. **Discover.** README, entry points, layout, and (for PR tours) changed files. Do not write steps before the shape is known.
2. **Infer the reader.** New joiner 9–13 steps; quick tour 5–8; architecture 14–18; PR/RCA/security/feature 7–11.
3. **Verify every anchor.** File exists, line in range, selection exact. Prefer a pattern when lines drift. Never guess line numbers.
4. **Write** `.tours/<persona>-<focus>.tour`.
5. **Validate.** First step is a real file or directory. `ref` points at a revision that actually contains every referenced file. PR tours use the PR branch, never the base.

Each description answers situation, mechanism, implication, gotcha. Narrative: orientation → module map → core path → gotcha → next move.

## Output

A valid `.tour` file plus a one-line confirmation that every path and line was checked against the chosen `ref` (or against the working tree when `ref` is omitted).
