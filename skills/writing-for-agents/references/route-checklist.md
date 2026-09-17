# Router and Skill Inventory Checklist

Authoring and audit reference for routing instructions, AGENTS.md, and skill catalog integrity.
Preserved from the router checklist reference.

## Standard Category Mapping

- **Plan:** `grill-with-docs` (with frontier rounds), `to-spec`, `to-tickets`, `tdd` · Architecture DAG: OpenCode plan agent
- **Write:** Current session. Test-first: `tdd`. Spec/ticket implementation stays in-session with `tdd`.
- **Review:** In-session review (default). Two-axis Standards + Spec: `matt-code-review`. Adversarial multi-review: `/interrogate` (manual).
- **Design:** `found-this-design` (direction/bank) → `impeccable` (atoms/composition) → `emil-design-eng` (motion/interactions). Continuous 3D world: `scroll-world`. Scrollytelling: `scroll-craft`. Media/stills: `visual-studio`.
- **Documents:** `smartdoc` (per-job doc intelligence), `markitdown` (file-to-markdown ingest), `smartbook-ingest` (reusable library compilation).
- **Engineering (Model-invoked on match):** `diagnosing-bugs`, `domain-modeling`, `codebase-design`, `writing-for-agents`, `research`, `prototype`, `diagram-design`.
- **Diagnostics & Governance (Model-invoked on match):** `agent-architecture-audit`, `cost-aware-llm-pipeline`, `eval-harness`, `prompt-optimizer`, `skill-stocktake`, `api-design`, `contract-first`, `automation-audit-ops`, `code-tour`, `click-path-audit`.
- **Vendor / Cloud (Model-invoked on match):** `supabase-ops`, `mongodb-ops`, `vercel-ops`.
- **Browser / GitHub / Risk:** `playwright-qa` (primary QA), `browser-act` (multi-account/stealth), `chrome-devtools-axi` (CDP diagnostics), `gh-axi`, `full-audit-keamanan` (security), `full-performance-audit` (performance), `adhd` (divergent ideation).
- **Engineering (Manual / Slash-only):** `/architect`, `/arena`, `/blast-radius`, `/create-verification-skill`, `/decision-log`, `/demo-video`, `/figure-it-out`, `/improve-codebase-architecture`, `/interrogate`, `/maintain-verification-skill`, `/reflect`, `/technical-writing`, `/unslop`, `/why`, `/wizard`.

## Not Installed (Inform User Directly)

Do not hallucinate or auto-install:
`/design`, `/execute-plan`, `/implement`, `/review`, `/code-review`, `/imagine`, `/docx`, `/pdf`, `/pptx`, `/grill-me`, `/handoff`, `/triage`, `/wayfinder`, `/bro`, `/poteto-mode`, `/swarm`, `/setup-matt-pocock-skills`, `/pr-babysit`, `/create-skill`, `/create-workflow`, `/build-with-ai`, `game-asset-*`.

## Standard Routing Decision Order

1. Repo evidence is enough → do the work directly without a specialist.
2. User typed a slash command → load that manual command.
3. Architecture / PR-plan DAG → OpenCode plan agent, then implement in-session after approval.
4. Feature needs an interview, glossary, or ADR → `grill-with-docs`. Then `/to-spec` → `/to-tickets` only if asked or multi-session.
5. Ordinary implementation → write in-session; `tdd` when test-first.
6. UI direction unknown → `found-this-design` then `impeccable`. Direction chosen → `impeccable`.
7. Official library/spec facts → `research` (Context7). Why *this repo* made a choice → `/why` (manual).
