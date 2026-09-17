# Catalog Stocktake — 1.8.5

Executed per [skills/skill-stocktake/SKILL.md](../skills/skill-stocktake/SKILL.md).

Measured tree: **49 model-invoked** (`skills/*/SKILL.md`) + **17 manual** (`manual-skills/*/SKILL.md`, each with a matching `commands/<name>.md`) = **66**. Matches `vendor/skill-policy.json` and `vendor/skill-allowlist.txt`.

License column is authoritative from `vendor/license-audit.json`, not frontmatter. A missing frontmatter `license` key is not a gap: 28 of 66 deliberately defer to the audit file.

`RETIRE` requires either a failed existence pass or a no-skill baseline. No baseline was run in this pass, so **no item is retired here**. Items whose retirement would depend on a baseline are listed under [Blocked on A/B](#blocked-on-ab) and carry `KEEP` in the table, per the evidence rule.

## Verdicts

| Skill | Kind | Verdict | Evidence | Handoff |
|---|---|---|---|---|
| academic | model | KEEP | 45 lines, 5 refs; owns scholarly/IMRaD lane fenced off `research` and `smartdoc` | — |
| adhd | model | UPDATE (applied) | Body named `Claude Code`/`GrokBuild` as if either were this runtime; remaining bulk is calibration numerics + upstream MIT attribution | `writing-for-agents` |
| agent-architecture-audit | model | KEEP | 59 lines, NOTICE present; agent-loop lane distinct from `diagnosing-bugs` | — |
| api-design | model | KEEP | 37 lines; REST contract lane fenced off `contract-first` | — |
| architect | manual | KEEP | 82 lines, 3 refs; slash-only DAG bake-off | — |
| arena | manual | KEEP | 74 lines; multi-model bake-off, slash-only | — |
| ask-matt | model | UPDATE (applied) | Description said "GrokBuild skill or flow"; loaded every session | `writing-for-agents` |
| automation-audit-ops | model | KEEP | 44 lines; live-automation inventory, no sibling owns it | — |
| blast-radius | manual | KEEP | 46 lines; impact analysis, slash-only | — |
| browser-act | model | KEEP | 48 lines; explicit-request-only fence vs `playwright-qa` | — |
| chrome-devtools-axi | model | UPDATE (applied) | Duplicate contract block + `$HOME/.grok` path contradicting `rules/00-routing.md:131` | `writing-for-agents` |
| click-path-audit | model | KEEP | 39 lines; handler/shared-store lane fenced off `playwright-qa` | — |
| code-tour | model | KEEP | 35 lines; produces `.tour` artifacts nothing else emits | — |
| codebase-design | model | COMPRESS (applied) | 115 → 97; two ASCII box diagrams restated adjacent prose | `writing-for-agents` |
| contract-first | model | KEEP | 41 lines; multi-consumer contract lane | — |
| cost-aware-llm-pipeline | model | KEEP | 48 lines; token/model-tier lane fenced off `full-performance-audit` | — |
| create-verification-skill | manual | KEEP | 44 lines; paired with `maintain-verification-skill` | — |
| decision-log | manual | KEEP | 66 lines, ships a script | — |
| demo-video | manual | KEEP | 19 lines; manual slash command alias for `id-demo-video` | — |
| diagnosing-bugs | model | KEEP | 139 lines but carries the red-capable loop criterion; ships `scripts/` | — |
| diagram-design | model | KEEP | 46 lines, 3 refs; editorial diagram lane fenced off `impeccable` | — |
| domain-modeling | model | KEEP | 75 lines; glossary/ADR primitive composed by `grill-with-docs` | — |
| emil-design-eng | model | KEEP | 676 lines, largest in catalog; easing/timing numerics are the payload. COMPRESS off-limits by instruction | — |
| eval-harness | model | KEEP | 50 lines, 2 refs incl. `skill-utility.md` added in #18 | — |
| figure-it-out | manual | KEEP | 53 lines; slash-only exploration | — |
| found-this-design | model | KEEP | 127 lines, 4 scripts; Design Bank entry point | — |
| full-audit-keamanan | model | KEEP | 69 lines; security fence, never COMPRESS | — |
| full-performance-audit | model | KEEP | 232 lines; LCP/INP/CLS thresholds are the payload. COMPRESS off-limits by instruction | — |
| gh-axi | model | KEEP | 65 lines; GitHub CLI surface | — |
| grill-with-docs | model | COMPRESS (applied) | 120 → 77; whole body duplicated behind orphan overlay marker | `writing-for-agents` |
| grilling | model | KEEP | 23 lines; non-default primitive, explicitly named-only | — |
| humanizer | model | KEEP | 64 lines, NOTICE present; paired with manual `/unslop` | — |
| hyperframes | model | KEEP | 48 lines, Apache-2.0 with NOTICE; HTML→MP4 lane | — |
| id-demo-video | model | KEEP | 230 lines, 4 refs, 2 scripts; Indonesian walkthrough video production lane fenced off `hyperframes`, `playwright-qa`, and `visual-studio` | — |
| img2threejs | model | KEEP | 50-line first-party MIT factory; image→procedural Three.js Group; fenced off scroll-world / scroll-craft / hyperframes / visual-studio / impeccable; shipped #21 | — |
| impeccable | model | KEEP | 89-line body against 38 refs + 44 scripts — progressive disclosure working as designed | — |
| improve-codebase-architecture | manual | KEEP | 71 lines; slash-only | — |
| install-anti-slop | model | KEEP | 56 lines; pinned upstream commit `e8c4880` verified in body | — |
| interrogate | manual | KEEP | 73 lines, 4 refs; highest overlap pair at 0.359, still under warn | — |
| maintain-verification-skill | manual | KEEP | 39 lines; verification profile upkeep | — |
| markitdown | model | KEEP | Document text/table conversion to Markdown; preserves SmartDoc boundaries | — |
| matt-code-review | model | KEEP | 88 lines; two-axis review, opt-in only | — |
| matt-implement | manual | KEEP | 15 lines; ticket-loop entry, never auto-started | — |
| mongodb-ops | model | KEEP | 45 lines; vendor lane | — |
| playwright-qa | model | KEEP | 54 lines, Apache-2.0 with NOTICE; primary browser QA | — |
| prompt-optimizer | model | KEEP | 50 lines; advisory-only, does not mutate skills | — |
| prototype | model | KEEP | 27 lines; throwaway-evidence lane | — |
| reflect | manual | KEEP | 61 lines, 4 refs | — |
| research | model | KEEP | 15 lines, smallest body; already minimal | — |
| scroll-craft | model | KEEP | 101 lines, 8 refs; scroll-story lane fenced off `scroll-world` | — |
| scroll-world | model | KEEP | 129 lines; Hard rules section is fences, not ceremony | — |
| skill-stocktake | model | KEEP | 82 lines; this audit's own protocol | — |
| smartbook-ingest | model | KEEP | 33 lines; persistent-knowledge lane | — |
| smartdoc | model | KEEP | 62 lines, 4 refs; per-job document lane | — |
| supabase-ops | model | KEEP | 47 lines; vendor lane | — |
| tdd | model | KEEP | 39 lines; red-green lane | — |
| technical-writing | manual | KEEP | 130 lines, largest manual; prose structure lane | — |
| to-spec | model | KEEP | 80 lines; synthesis step before `to-tickets` | — |
| to-tickets | model | KEEP | 126 lines; extra length is expand–contract blast-radius judgment, not ceremony | — |
| unslop | manual | KEEP | 19 lines; manual twin of `humanizer` by design | — |
| vercel-ops | model | KEEP | 44 lines; vendor lane | — |
| visual-studio | model | UPDATE (applied) | Body claimed "GrokBuild already owns the tools" — host-product claim | `writing-for-agents` |
| wait-what | manual | KEEP | 9 lines, smallest in catalog | — |
| why | manual | KEEP | 79 lines, 4 refs; repo rationale, fenced off `research` | — |
| wizard | manual | KEEP | 47 lines; slash-only | — |
| writing-for-agents | model | KEEP | 82 lines; authoring lane, receives COMPRESS handoffs | — |

## Tallies

| Verdict | Count |
|---|---|
| KEEP | 60 |
| COMPRESS (applied) | 2 |
| UPDATE (applied) | 4 |
| MERGE | 0 |
| RETIRE | 0 |
| **Total** | **66** |

Live catalog at 1.8.5 is 66 (49 model-invoked, 17 manual) including `id-demo-video` and `/demo-video`.
