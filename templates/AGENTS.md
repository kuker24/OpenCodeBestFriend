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
5. Interview / glossary / ADR → skill `grill-with-docs` → `to-spec` → `to-tickets` only if asked or multi-session.
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

UI direction → skill `found-this-design` then `impeccable`. Motion → `emil-design-eng`. Media → `visual-studio`. Scroll/3D → `scroll-world`. Registry → shadcn MCP. Design Intelligence and Design V2 are internal to Impeccable `new-work`, never a route.

Browser QA → skill `browser-act`. Observed cause → `chrome-devtools-axi` after `opencode-chromium-cdp` (`127.0.0.1:9223`). Never Google Chrome. Project Playwright only if the project already has it.

Auth/secret/payment/upload/webhook/privileged/public API → `full-audit-keamanan`. Measured LCP/INP/CLS/latency/bundle → `full-performance-audit`. GitHub → `gh-axi`. Hard unknown bug → `diagnosing-bugs`.

## When routing is non-obvious

Read the file `~/.config/opencode/bestfriend/rules/00-routing.md` with the Read tool. Do not `@`-import it.

## When a verification profile is chosen

Read `~/.config/opencode/bestfriend/rules/01-verification.md`. Profiles: FAST, STANDARD, UI, SECURITY, PERFORMANCE, RELEASE. Missing project command = `NOT_CONFIGURED`, not PASS.

If you need operational principles or prose discipline, Read `~/.config/opencode/bestfriend/rules/02-engineering-principles.md` or `03-prose-discipline.md`. Do not `@`-import them.

There is no user `/implement`, `/code-review`, `/design`, or `/imagine` skill.

Manual-only specialists are OpenCode commands, not auto-discovered skills: `/architect` `/arena` `/blast-radius` `/create-verification-skill` `/decision-log` `/figure-it-out` `/improve-codebase-architecture` `/interrogate` `/maintain-verification-skill` `/matt-implement` `/reflect` `/technical-writing` `/unslop` `/wait-what` `/why` `/wizard`. Suggest them when the user names the job; do not load them as the default path.
<!-- OPENCODEBESTFRIEND:END -->
