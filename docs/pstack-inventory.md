# OpenCodeBestFriend — pstack inventory

Upstream: [cursor/plugins](https://github.com/cursor/plugins) `pstack/` (MIT © 2026 Lauren Tan).
Studied tree: plugins `e31650e`. Vendored skill pin remains `60c641e` unless a row says UPDATE.
Full Cursor plugin, agents, automations/benny, and model-panel setup are **not** installed.

Contract: `NEW | MERGE | REJECT | DEFER | DONE`.
Zero catalog twins. A procedure the current model already performs unprompted stays `DEFER` or `REJECT`.
Capability drift updates the existing specialist or rule. It does not add a sibling skill.

## Summary

| Decision | Count |
| :--- | :---: |
| `DONE` | 12 |
| `MERGE` | 27 |
| `REJECT` | 8 |
| `DEFER` | 0 |
| `NEW` | 0 |
| **TOTAL** | **47** |

Counts are pstack `skills/*` directories only (23 `principle-*` + 24 named skills). Benny automations and Cursor agents stay out of the catalog.

## Named skills

| Upstream | Decision | BestFriend target | Reason |
| :--- | :---: | :--- | :--- |
| `architect` | **DONE** | `manual-skills/architect` | Already adapted. Multi-sketch bake-off stays manual. |
| `arena` | **DONE** | `manual-skills/arena` | Protocol lives in `rules/arena-protocol.md`. |
| `blast-radius` | **DONE** | `manual-skills/blast-radius` | Impact beyond the diff. Manual only. |
| `create-verification-skill` | **DONE** | `manual-skills/create-verification-skill` | Project-local control skill authoring. |
| `maintain-verification-skill` | **DONE** | `manual-skills/maintain-verification-skill` | Periodic honesty pass on that control skill. |
| `figure-it-out` | **DONE** | `manual-skills/figure-it-out` | Playbook when no narrower specialist fits. |
| `interrogate` | **DONE** | `manual-skills/interrogate` | Claim interrogation. Manual only. |
| `reflect` | **DONE** | `manual-skills/reflect` | Learnings with explicit approval. Never auto-edit skills. |
| `technical-writing` | **DONE** | `manual-skills/technical-writing` | Doc structure. Prose tells stay `humanizer`. |
| `unslop` | **DONE** | `manual-skills/unslop` | Manual alias of `humanizer`. |
| `why` | **DONE** | `manual-skills/why` | Repo rationale. Library facts stay Context7 / `research`. |
| `decision-log` (upstream `show-me-your-work`) | **DONE** | `manual-skills/decision-log` | TSV operational trail. Protocol in `rules/decision-log-protocol.md`. |
| `tdd` | **MERGE** | `skills/tdd` | Keep Matt Pocock model-invoked TDD. Do not swap in pstack's disable-model-invocation twin. |
| `how` | **MERGE** | Codebase Memory, then `/code-tour` or `/why` | Mechanism vs motivation. Default path already explains current shape from repo evidence. Durable walkthrough is `code-tour`. Rationale is `/why`. No `/how` twin. |
| `show-me-your-work` | **MERGE** | `/decision-log` | Same TSV contract. Already ported under the OpenCode name. |
| `recall` | **MERGE** | Codebase Memory MCP | Project memory is the owned store. Do not add a Cursor transcript crawler. |
| `teach` | **MERGE** | `/technical-writing`, `writing-for-agents` | Teaching artifacts are docs or skill bodies. |
| `no-comments` | **MERGE** | `rules/03-prose-discipline.md`, `rules/02-engineering-principles.md` | Comment-sicko agent and Cursor Task types stay out. Encode constraints in tests/lint, do not narrate them. |
| `typescript-best-practices` | **MERGE** | Context7 + repo evidence | Language patterns are not a BestFriend specialist. |
| `automate-me` | **MERGE** | `automation-audit-ops` | Inventory keep/merge/cut of live automation. Cursor Automations UI is foreign. |
| `poteto-mode` | **MERGE** | `templates/AGENTS.md`, `rules/00-routing.md` | Playbooks map onto existing specialists. The Cursor mode skill, model panel, and 23 bundled playbook files are not copied. |
| `setup-pstack` | **REJECT** | — | Cursor plugin install + Fable/Sol/Grok panel. OpenCode providers stay user-owned. |
| `bro` | **REJECT** | — | Personality overlay. Not a capability. |
| `make-bot-ui` | **REJECT** | — | Product-specific bot chrome. Product UI stays `found-this-design` / `impeccable`. |
| `swarm` | **REJECT** | — | Cursor multi-agent fleet. OpenCode agents are host-owned. Do not vendor a second orchestrator. |
| `principle-*` (23) | **MERGE** | `rules/02-engineering-principles.md` | Working rules, Read on demand. Not 23 skills. |

## poteto-mode playbooks → existing routes

| Playbook | Route |
| :--- | :--- |
| investigation | Codebase Memory, then `/why` or `/code-tour` |
| bug fix | `diagnosing-bugs` |
| perf | `full-performance-audit` |
| hillclimb | `full-performance-audit` + `eval-harness` when a metric loop is named |
| runtime / trace forensics | `diagnosing-bugs`; observed Chromium cause → `chrome-devtools-axi` |
| feature | `grill-with-docs` when interview/ADR is needed; else in-session write; `tdd` when test-first |
| refactoring | `codebase-design` |
| prototype | `prototype` |
| visual parity | `playwright-qa` + `impeccable` |
| authoring a skill | `writing-for-agents`; catalog hygiene → `skill-stocktake` |
| eval | `eval-harness` |
| babysit / shipping / opening a pr | `gh-axi` |
| multi-phase plan | OpenCode plan agent |
| autonomous run / orchestrate / autopilot-* | **REJECT** as skills. Overnight unattended merge fleets stay host-owned. `figure-it-out` covers an auditable long playbook when the user asks. |
| session pickup / pause safely / worktree cleanup | default session + git. No specialist. |

## Do not

- Do not add `/poteto-mode`, `/how`, `/swarm`, `/setup-pstack`, or `principle-*` to the 64-skill catalog.
- Do not copy Cursor `disable-model-invocation` fields into model-invoked skills.
- Do not `@`-import this inventory into `AGENTS.md`.
- Do not treat pstack availability as a reason to load a second implementation specialist.
