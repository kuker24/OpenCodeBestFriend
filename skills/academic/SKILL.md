---
name: academic
description: Academic research, literature synthesis, thesis/paper drafting, and peer review. Use for scholarly literature surveys, claim-to-source tracing, academic manuscripts (IMRaD/proposals), and rigorous peer critique. Not for library/API docs (research), one-off document OCR/render (smartdoc), or local book ingest (smartbook-ingest).
compatibility: opencode
license: MIT
---

# Academic

One primary specialist for scholarly research workflows: literature surveying, manuscript drafting, structured peer review, and revision ledgers.

## Load One Mode

Select exactly one mode reference based on the user's current goal. Do not load all mode files at once:

| Mode | Purpose | Reference |
|---|---|---|
| `research` | Literature discovery, claim-source matrix, DOI/URL verification | [references/research.md](references/research.md) |
| `write` | Scholarly drafting (IMRaD, thesis, proposal, methodology) | [references/write.md](references/write.md) |
| `review` | Criterion-bound critique, methodology evaluation, anti-sycophancy | [references/review.md](references/review.md) |
| `revise` | Change ledger, rebuttal response matrix, critique addressing | [references/revise.md](references/revise.md) |

Always observe academic integrity standards in [references/integrity.md](references/integrity.md).

## Boundaries

| Task | Route |
|---|---|
| Official software library, framework specs, or first-party API facts | `research` + Context7 |
| Why this codebase made an architectural choice | `/why` (manual) |
| Document ingestion, OCR, table extraction, or PDF rendering | `smartdoc` |
| Compiling reusable local textbook/module knowledge | `smartbook-ingest` |
| Product feature interview and ADR writing | `grill-with-docs` |
| User-facing prose AI-tell cleanup | `humanizer` / `/unslop` |
| Scholarly literature, thesis, manuscript, and peer critique | **`academic`** |

`smartdoc` may render the final locked manuscript to PDF/DOCX. `academic` owns the academic claims, citations, and scholarly structure; `smartdoc` owns rendering and document formats.

## Core Rules

1. **One mode per session turn:** Do not execute all four phases simultaneously. Complete the current phase and request confirmation before advancing.
2. **Missing toolchains are NOT_CONFIGURED:** If compilation tools (Pandoc, LaTeX, typst) or reference managers (Zotero) are absent from the host environment, report `NOT_CONFIGURED`. Never fake build or export success.
3. **No detector evasion or fake similarity scores:** Never promise 0% similarity or Turnitin evasion. Do not participate in deceptive rewriting loops.
4. **Primary source verification:** Every cited factual claim must be backed by a verifiable paper title, DOI, author, or canonical URL. Flag unverified claims explicitly as `[UNVERIFIED]`.
5. **Anti-sycophancy in review:** Academic reviews must stress-test assumptions, assess sample size/method limitations, and identify overclaiming. Honest critique takes priority over compliments.
