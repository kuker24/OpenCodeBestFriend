<!-- OPENCODEBESTFRIEND:BEGIN -->
# opencode-bestfriend router

```text
pikir dulu → bukti di repo → satu spesialis → cek hasil
```

Availability is not a reason to use a tool. One primary specialist. At most one risk specialist (`full-audit-keamanan` **or** `full-performance-audit`). Never print tokens, gateway URLs, or model maps. Model names are opaque identifiers. Never enable `--auto` unless the user explicitly asked.

## Default

1. Repo evidence is enough → do the work. No specialist.
2. User typed a slash command → load that command's specialist. Do not substitute.
3. Choosing a workflow → load skill `ask-matt`.
4. Architecture DAG → OpenCode **plan** agent, then implement in-session after approval.
5. Interview / glossary / ADR → skill `grill-with-docs` (`grilling` is not default; load `grilling` only if user names it) → `to-spec` → `to-tickets` only if asked or multi-session.
6. Ordinary implementation → this session. Skill `tdd` when test-first. Never auto `/matt-implement`.
7. Review → in-session. Skill `matt-code-review` only if two-axis asked.

## Report

If you name specialists or tools, use only:

- `USED` — actually loaded or called
- `CONSIDERED_NOT_USED` — considered, skipped, with a one-line why
- `MANUAL_NOT_INVOKED` — slash-only specialists not requested

Do not list unused tools as if they ran.

## Knowledge (lazy)

repo/file → Codebase Memory MCP first (skip if no project for cwd) → Serena only if already registered and exact symbol work → Context7 for current lib docs → OpenCode WebSearch/WebFetch; foreign Exa only if already connected → skill `adhd` only for high-ambiguity/high-risk.

## Specialists (load one)

UI direction → skill `found-this-design` then `impeccable`. UI atoms (button, input, card, nav) after world/brief → impeccable after Design V2 shortlist; BANK_MISS ≠ generate (never `found-this-design` for buttons). Motion UI (easing, hover, seam) → `emil-design-eng`. Still/ads/non-UI surface → `visual-studio`. Scroll-led story → `scroll-craft`. Camera/3D world/diorama → `scroll-world`. Registry → shadcn MCP. Design Intelligence and Design V2 are internal to Impeccable `new-work`, never a route. Stitch MCP = screen/comp generation only; then found-this-design or impeccable + Design V2 atoms. Never implement production UI from Stitch alone.

Browser QA → skill `playwright-qa`. Explicit/session BrowserAct → `browser-act`. Observed cause → `chrome-devtools-axi` after `opencode-chromium-cdp` (`127.0.0.1:9223`). Never Google Chrome. Project E2E suites (Playwright Test/Cypress) stay authoritative for regressions.

Auth/secret/payment/upload/webhook/privileged/public API → `full-audit-keamanan`. Measured LCP/INP/CLS/latency/bundle → `full-performance-audit`. GitHub → `gh-axi`. Hard unknown bug → `diagnosing-bugs`. Documents (PDF/DOCX/extract/review) → `smartdoc`. Reusable local knowledge → `smartbook-ingest`.

Prose AI-tells / humanize → skill `humanizer`. Slash `/unslop` is the same specialist, manual only. Technical writing structure → suggest `/technical-writing`. Academic literature / manuscript / peer-critique → skill `academic` (not `research`, not `smartdoc` unless file extract/render). Facts library/API → Context7; `research` only if repo lacking. Deterministic HTML video / render HTML to MP4 → skill `hyperframes` (not `visual-studio`, not `emil-design-eng`). Editorial diagram HTML/SVG → skill `diagram-design` (not `impeccable`).

REST resource/status/pagination/versioning → skill `api-design`. Consumer/provider OpenAPI/AsyncAPI/Protobuf → skill `contract-first`. Live cron/CI/hook/MCP inventory keep-merge-cut → skill `automation-audit-ops`. CodeTour .tour + anchor file → skill `code-tour`. Handler vs shared-store sequential-undo → skill `click-path-audit` (not `playwright-qa`).

Agent stack diagnostics / context leak / wrapper regression → skill `agent-architecture-audit`. Benchmark agent / pass@k → skill `eval-harness` (project unit tests stay `tdd`). Token budget / model tier / prompt cache → skill `cost-aware-llm-pipeline` (not `full-performance-audit`). Structural prompt critique → skill `prompt-optimizer` (not `humanizer`). Skill catalog hygiene → skill `skill-stocktake`.

Supabase Auth/RLS/migrations/Edge → skill `supabase-ops` (Context7; not impeccable). Mongo schema/index/aggregation → skill `mongodb-ops`. Vercel/Next hosting/deploy config → skill `vercel-ops` (not visual UI). Library facts remain Context7. These three never replace found-this-design or impeccable.

## When routing is non-obvious

Read the file `~/.config/opencode/bestfriend/rules/00-routing.md` with the Read tool. Do not `@`-import it.

## When a verification profile is chosen

Read `~/.config/opencode/bestfriend/rules/01-verification.md`. Profiles: FAST, STANDARD, UI, SECURITY, PERFORMANCE, RELEASE. Missing project command = `NOT_CONFIGURED`, not PASS.

If you need operational principles or prose discipline, Read `~/.config/opencode/bestfriend/rules/02-engineering-principles.md` or `03-prose-discipline.md`. Do not `@`-import them.

There is no user `/implement`, `/code-review`, `/design`, or `/imagine` skill.

Manual-only specialists are OpenCode commands, not auto-discovered skills: `/architect` `/arena` `/blast-radius` `/create-verification-skill` `/decision-log` `/figure-it-out` `/improve-codebase-architecture` `/interrogate` `/maintain-verification-skill` `/matt-implement` `/reflect` `/technical-writing` `/unslop` `/wait-what` `/why` `/wizard`. Suggest them when the user names the job; do not load them as the default path.
<!-- OPENCODEBESTFRIEND:END -->
