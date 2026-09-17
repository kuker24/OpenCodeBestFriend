---
name: grill-with-docs
description: Relentless interview to sharpen a plan with design-tree frontier rounds. Writes CONTEXT.md, a glossary, and ADRs as you go. Use when a feature still needs a plan, the user wants a deep planning interview, or they ask for /grill-with-docs.
compatibility: opencode
---

<!-- opencode-bestfriend-overlay:grill-with-docs -->

# Grill with docs

Run the interview in this session. Compose owned domain-modeling discipline (glossary, CONTEXT.md, ADRs) with relentless design-tree frontier rounds.

Map the decisions as a **design tree**: every decision branches into the decisions that hang off it.
Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled — the questions you can ask now without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for the user's answers before the next round.

Each frontier question should follow this format:

```markdown
❓ **Q1** - **<question title>**: <question body, options, trade-offs>

➡️ <your recommended answer>
```

Use `codebase-design` only when the conversation reaches a module, interface, or seam. Architecture DAGs still use the OpenCode plan agent, not this skill.

## Goal

Leave the repo with:

- `CONTEXT.md` — problem, decisions, open questions, glossary
- ADRs under `docs/adr/` (or `adr/` if that already exists) for hard-to-reverse choices

## Rules

- You gather facts. The user makes decisions.
- Finding facts is your job: when a frontier question needs a fact from the environment (filesystem, git, config), inspect it directly or dispatch a subagent; do not ask the user for facts you can look up.
- One question at a time when the answer branches. Batch only independent frontier questions.
- Use the project's words. When a term is overloaded, resolve it and write it into the glossary.
- Do not implement code in this skill.
- If Codebase Memory has no project for cwd, skip it and use repo files.
- Architecture DAGs use the OpenCode plan agent, not this skill.
- Ordinary writes stay in-session after the interview.
- Stop when the frontier is empty: every branch visited, nothing silently assumed, and you can implement or write `to-spec` without inventing decisions.

## Loop

1. Read `CONTEXT.md`, existing ADRs, and enough of the repo to speak the domain.
2. State the frontier: what you believe, what is undecided, what would change the design.
3. Ask the next question (or independent frontier) that most reduces that frontier.
4. After each answered decision, update `CONTEXT.md`. If the decision is hard to reverse, write an ADR.
5. Repeat until the stop condition.

## CONTEXT.md shape

```markdown
# <feature or system>

## Problem

## Decisions

## Open questions

## Glossary

## Sources
```

## ADR shape

```markdown
# ADR <nnn>: <title>

Status: accepted
Date: <ISO date>

## Context

## Decision

## Consequences
```

## After

Tell the user the paths you wrote. If the work is multi-session or they asked for tickets, offer `/to-spec` then `/to-tickets`. Otherwise implementation stays in this session; there is no user `/implement` skill.
