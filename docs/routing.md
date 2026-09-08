# Routing

Philosophy:

```text
pikir dulu → bukti di repo → satu spesialis → cek hasil
```

Load `00-routing.md` only when the thin router is not enough. Do not `@`-import rules.

Manual specialists stay behind slash commands. Suggest them when the user names the job.

Tool reporting:

```text
USED
CONSIDERED_NOT_USED
MANUAL_NOT_INVOKED
```

Never list unused tools as used.

Documents (answer, create, transform, extract, review, PDF/DOCX) route to `smartdoc`. Reusable book/module knowledge routes to `smartbook-ingest`. `/docx` and `/pdf` are missing aliases; nearest is `smartdoc`. `/pptx` is NOT_APPLICABLE. Do not add `commands/pdf.md` or `commands/docx.md`. Impeccable `document` remains DESIGN.md generation.

Prose AI-tell removal and natural tone polishing route to `humanizer` (`/unslop` is its manual alias). Scholarly research, academic manuscripts, and structured peer critique route to `academic`. Deterministic HTML composition rendered to video routes to `hyperframes`. Editorial technical diagrams (HTML/SVG) route to `diagram-design`. Foreign harnesses (such as ECC) remain `FOREIGN_ON_DEMAND`; never vendored, auto-merged, or shadowed.
