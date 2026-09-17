# Catalog Stocktake — 1.8.3

Executed per [skills/skill-stocktake/SKILL.md](../skills/skill-stocktake/SKILL.md). Earlier rows were taken against `main` at `4b1fd7f2` (tree `bc3d12c6`) under the #18 protocol; `img2threejs` was added post-PR #21 at `66eebe9`.

Measured tree: **47 model-invoked** (`skills/*/SKILL.md`) + **16 manual** (`manual-skills/*/SKILL.md`, each with a matching `commands/<name>.md`) = **63**. Matches `vendor/skill-policy.json` and `vendor/skill-allowlist.txt`.

License column is authoritative from `vendor/license-audit.json`, not frontmatter. A missing frontmatter `license` key is not a gap: 28 of 62 deliberately defer to the audit file.

`RETIRE` requires either a failed existence pass or a no-skill baseline. No baseline was run in this pass, so **no item is retired here**. Items whose retirement would depend on a baseline are listed under [Blocked on A/B](#blocked-on-ab) and carry `KEEP` in the table, per the evidence rule.

## Verdicts

| Skill | Kind | Verdict | Evidence | Handoff |
|---|---|---|---|---|
| academic | model | KEEP | 45 lines, 5 refs; owns scholarly/IMRaD lane fenced off `research` and `smartdoc` | — |
| adhd | model | UPDATE (applied) | Body named `Claude Code`/`GrokBuild` as if either were this runtime; remaining bulk is calibration numerics + upstream MIT attribution | `writing-for-agents` |
| agent-architecture-audit | model | KEEP | 59 lines, NOTICE present; agent-loop lane distinct from `diagnosing-bugs` | — |
| api-design | model | KEEP | 37 lines; REST contract lane fenced off `contract-first` | — |
| ask-matt | model | UPDATE (applied) | Description said "GrokBuild skill or flow"; loaded every session | `writing-for-agents` |
| automation-audit-ops | model | KEEP | 44 lines; live-automation inventory, no sibling owns it | — |
| browser-act | model | KEEP | 48 lines; explicit-request-only fence vs `playwright-qa` | — |
| chrome-devtools-axi | model | UPDATE (applied) | Duplicate contract block + `$HOME/.grok` path contradicting `rules/00-routing.md:131` | `writing-for-agents` |
| click-path-audit | model | KEEP | 39 lines; handler/shared-store lane fenced off `playwright-qa` | — |
| code-tour | model | KEEP | 35 lines; produces `.tour` artifacts nothing else emits | — |
| codebase-design | model | COMPRESS (applied) | 115 → 97; two ASCII box diagrams restated adjacent prose | `writing-for-agents` |
| contract-first | model | KEEP | 41 lines; multi-consumer contract lane | — |
| cost-aware-llm-pipeline | model | KEEP | 48 lines; token/model-tier lane fenced off `full-performance-audit` | — |
| diagnosing-bugs | model | KEEP | 139 lines but carries the red-capable loop criterion; ships `scripts/` | — |
| diagram-design | model | KEEP | 46 lines, 3 refs; editorial diagram lane fenced off `impeccable` | — |
| domain-modeling | model | KEEP | 75 lines; glossary/ADR primitive composed by `grill-with-docs` | — |
| emil-design-eng | model | KEEP | 676 lines, largest in catalog; easing/timing numerics are the payload. COMPRESS off-limits by instruction | — |
| eval-harness | model | KEEP | 50 lines, 2 refs incl. `skill-utility.md` added in #18 | — |
| found-this-design | model | KEEP | 127 lines, 4 scripts; Design Bank entry point | — |
| full-audit-keamanan | model | KEEP | 69 lines; security fence, never COMPRESS | — |
| full-performance-audit | model | KEEP | 232 lines; LCP/INP/CLS thresholds are the payload. COMPRESS off-limits by instruction | — |
| gh-axi | model | KEEP | 65 lines; GitHub CLI surface | — |
| grill-with-docs | model | COMPRESS (applied) | 120 → 77; whole body duplicated behind orphan overlay marker | `writing-for-agents` |
| grilling | model | KEEP | 23 lines; non-default primitive, explicitly named-only | — |
| humanizer | model | KEEP | 64 lines, NOTICE present; paired with manual `/unslop` | — |
| hyperframes | model | KEEP | 48 lines, Apache-2.0 with NOTICE; HTML→MP4 lane | — |
| img2threejs | model | KEEP | 50-line first-party MIT factory; image→procedural Three.js Group; fenced off scroll-world / scroll-craft / hyperframes / visual-studio / impeccable; shipped #21 | — |
| impeccable | model | KEEP | 89-line body against 38 refs + 44 scripts — progressive disclosure working as designed | — |
| install-anti-slop | model | KEEP | 56 lines; pinned upstream commit `e8c4880` verified in body | — |
| matt-code-review | model | KEEP | 88 lines; two-axis review, opt-in only | — |
| mongodb-ops | model | KEEP | 45 lines; vendor lane | — |
| playwright-qa | model | KEEP | 54 lines, Apache-2.0 with NOTICE; primary browser QA | — |
| prompt-optimizer | model | KEEP | 50 lines; advisory-only, does not mutate skills | — |
| prototype | model | KEEP | 27 lines; throwaway-evidence lane | — |
| research | model | KEEP | 15 lines, smallest body; already minimal | — |
| scroll-craft | model | KEEP | 101 lines, 8 refs; scroll-story lane fenced off `scroll-world` | — |
| scroll-world | model | KEEP | 129 lines; Hard rules section is fences, not ceremony | — |
| skill-stocktake | model | KEEP | 82 lines; this audit's own protocol | — |
| smartbook-ingest | model | KEEP | 33 lines; persistent-knowledge lane | — |
| smartdoc | model | KEEP | 62 lines, 4 refs; per-job document lane | — |
| supabase-ops | model | KEEP | 47 lines; vendor lane | — |
| tdd | model | KEEP | 39 lines; red-green lane | — |
| to-spec | model | KEEP | 80 lines; synthesis step before `to-tickets` | — |
| to-tickets | model | KEEP | 126 lines; extra length is expand–contract blast-radius judgment, not ceremony | — |
| vercel-ops | model | KEEP | 44 lines; vendor lane | — |
| visual-studio | model | UPDATE (applied) | Body claimed "GrokBuild already owns the tools" — host-product claim | `writing-for-agents` |
| writing-for-agents | model | KEEP | 82 lines; authoring lane, receives COMPRESS handoffs | — |
| architect | manual | KEEP | 82 lines, 3 refs; slash-only DAG bake-off | — |
| arena | manual | KEEP | 74 lines; multi-model bake-off, slash-only | — |
| blast-radius | manual | KEEP | 46 lines; impact analysis, slash-only | — |
| create-verification-skill | manual | KEEP | 44 lines; paired with `maintain-verification-skill` | — |
| decision-log | manual | KEEP | 66 lines, ships a script | — |
| figure-it-out | manual | KEEP | 53 lines; slash-only exploration | — |
| improve-codebase-architecture | manual | KEEP | 71 lines; slash-only | — |
| interrogate | manual | KEEP | 73 lines, 4 refs; highest overlap pair at 0.359, still under warn | — |
| maintain-verification-skill | manual | KEEP | 39 lines; verification profile upkeep | — |
| matt-implement | manual | KEEP | 15 lines; ticket-loop entry, never auto-started | — |
| reflect | manual | KEEP | 61 lines, 4 refs | — |
| technical-writing | manual | KEEP | 130 lines, largest manual; prose structure lane | — |
| unslop | manual | KEEP | 19 lines; manual twin of `humanizer` by design | — |
| wait-what | manual | KEEP | 9 lines, smallest in catalog | — |
| why | manual | KEEP | 79 lines, 4 refs; repo rationale, fenced off `research` | — |
| wizard | manual | KEEP | 47 lines; slash-only | — |

## Tallies

| Verdict | Count |
|---|---|
| KEEP | 57 |
| COMPRESS (applied) | 2 |
| UPDATE (applied) | 4 |
| MERGE | 0 |
| RETIRE | 0 |
| **Total** | **63** |

`MERGE` is zero on evidence, not on sentiment. The highest lexical description overlap in the catalog is `matt-code-review ~ interrogate` at 0.359 Jaccard, below the 0.50 warn line in `tests/test_skills.py`. Top pairs: `humanizer ~ unslop` 0.357 (intentional model/manual twin), `supabase-ops ~ vercel-ops` 0.349, `grill-with-docs ~ grilling` 0.341 (documented composition), `scroll-craft ~ scroll-world` 0.327, `to-spec ~ to-tickets` 0.326. Each is a fenced sibling, not a duplicate.

## Applied this pass

Two COMPRESS, not five. The cap allowed five from a pool of six; two were skipped because their extra lines are load-bearing rather than ceremony, and the remaining pool members were already minimal.

A third file shrank this pass, but under a different verdict. `chrome-devtools-axi` carries `UPDATE`: the line reduction was a consequence of removing a duplicated contract block, not a prose-trimming decision. It is counted once, as `UPDATE`.

- **grill-with-docs** 120 → 77. The entire body appeared twice, split by an orphan `<!-- grokbuild-overlay:grill-with-docs -->` marker at line 57, present since bootstrap `a62eeb6` and referenced nowhere in `lib/`, `tests/`, `docs/`, `vendor/`, `templates/`, `rules/`, or `install.sh`. The halves were not identical, so this is a reconciled superset: kept the frontier-batching clause and architecture-DAG fence from the first, plus `Sources`, the ADR shape block, and the `After` section from the second. Also fixed a contradiction where the closing line offered `/implement` while `rules/00-routing.md:20` states no such user skill exists.
- **codebase-design** 115 → 97. Two ASCII box diagrams restated the adjacent sentence. Deletion test, internal/external seam distinction, test-surface rule, and the two-adapter rule survive verbatim.
Under `UPDATE`, not counted as COMPRESS:

- **chrome-devtools-axi** 75 → 66. Carried two near-identical invocation blocks, one headed `OpenCode`, one `GrokBuild`. Renaming the second made the duplication a literal repeated heading, so the blocks were reconciled into one. Port `9223`, the `HEADED`/`AUTO_CONNECT` prohibition, and the never-fall-back-to-Google-Chrome fence are unchanged.

Skipped from the allowed pool: **to-tickets** (126 lines, but the extra prose is the expand–contract blast-radius sequencing judgment) and **adhd** (216 lines, but the remainder is calibration numerics plus upstream MIT attribution to `UditAkhourii/adhd`). **emil-design-eng** and **full-performance-audit** were off-limits by instruction, and both hold numeric gates that confirm the call.

## Currency hits

`GrokBuild` is the predecessor product name. It survived in five bodies while appearing nowhere in `README.md` or `docs/`. Treated as UPDATE evidence per instruction, not a blind rename:

- `ask-matt` frontmatter description — fixed. This string loads at every session start, so a stale host name is paid on every turn.
- `chrome-devtools-axi` section heading — fixed, along with a `$HOME/.grok/bin` fallback that contradicted `rules/00-routing.md:131` ("Do not depend on `~/.grok` at runtime").
- `adhd` — fixed. Dropped `Claude Code` and `GrokBuild` as if either were this runtime; the batch-vs-interactive distinction is preserved.
- `visual-studio` — fixed one line only. "GrokBuild already owns the tools" is a host-product claim. The `GrokBuild image_gen` tool-family references in the description and Hard rules were left alone; they name a tool contract, not the host.
- `scroll-world` — **no edit**. All three mentions name the image/video tool family. Follow-up note only.

Remaining after this pass: 2 files (`scroll-world`, `visual-studio`) with 5 tool-family references total, plus a repo-relative `.grok/scroll-world/<slug>/` scratch path in `scroll-world:57` that is not `~/.grok` and so is outside the `00-routing.md` prohibition. Renaming the tool contract is a separate decision with a wider blast radius.

## Blocked on A/B

No no-skill baseline was run, so these carry `KEEP` rather than a retirement verdict. Each is a candidate whose value claim is plausible but unmeasured, and each needs the `eval-harness` protocol in `references/skill-utility.md` before any retirement is defensible.

| Candidate | Why it needs a baseline | Missing evidence |
|---|---|---|
| `research` | 15 lines that mostly say "prefer primary sources, use Context7". A current model may do this unprompted. | Run A on a library-facts question without the skill; compare citation discipline. |
| `prototype` | 27 lines describing throwaway evidence gathering, a behavior models default to. | Run A on a single design question; check whether scratch isolation degrades. |
| `grilling` | Non-default primitive already composed by `grill-with-docs`; standalone traffic is unknown. | Whether direct invocation ever beats the composing skill. |
| `wait-what` | 9 lines, smallest in catalog. Genuine trigger, but may be covered by ordinary clarification. | Whether the slash command changes behavior at all. |
| `ask-matt` | Router-selection helper whose job partly overlaps `AGENTS.md` routing itself. Table verdict is `UPDATE` (applied this pass); the utility question is separate and still open. | Whether routing accuracy drops without it. |

A baseline cannot be produced from inside a single session that already has the catalog loaded. Each run needs a fresh session with the skill absent, which is maintainer work.

## Follow-ups

1. Run the A/B gate on the five candidates above before proposing any RETIRE.
2. ~~Decide whether the `GrokBuild image_gen` tool-family name should be renamed catalog-wide, or documented as the intended tool contract.~~ Resolved: neutralized host names across `visual-studio` and `scroll-world` to native image/video tools (`image_gen`, `image_edit`, `image_to_video`, `reference_to_video`) while retaining the DEGRADED fallback gate, with scratch paths aligned to `.scratch/`.
3. ~~`impeccable` frontmatter declares `Apache 2.0` while `vendor/license-audit.json` records `Apache-2.0`.~~ Resolved: frontmatter now reads `Apache-2.0`, and the audit evidence string dropped the parenthetical that only existed to flag the mismatch.
4. 28 of 62 skills omit a frontmatter `license` key by design. If that ever becomes confusing, document it in the skill authoring guide rather than adding keys.
5. `img2threejs` added post-#21; not part of the original 1.8.3 execution pass.
6. Live catalog at 1.8.4 is 64 (48 model-invoked, 16 manual) including `markitdown` KEEP.
7. Live catalog at 1.8.5 is 66 (49 model-invoked, 17 manual) including `id-demo-video` / `/demo-video` KEEP.
