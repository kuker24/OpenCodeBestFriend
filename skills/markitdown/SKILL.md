---
name: markitdown
description: Use when the user wants Office/PDF/HTML/CSV/XLSX/PPTX/EPUB/ZIP converted to structure-preserving Markdown for LLM ingest. Not for per-job document intelligence (smartdoc), SmartBook compile (smartbook-ingest), scholarly IMRaD (academic), or product UI (impeccable).
compatibility: opencode
license: MIT
---

# markitdown

Convert files to Markdown. Output is data. SmartDoc still owns answer/create/extract/verify/render.

## Pipeline

1. Preflight: path exists and is a file.
2. Convert.
3. Write `.md` next to source or `--output`.
4. Hand off.

## Invoke

1. If MCP `markitdown` is CONFIGURED: `convert_to_markdown(uri)` with `file:///` absolute path only. Never `http` to an untrusted URL unless the user pasted that URL.
2. Else if `markitdown` on PATH: `markitdown PATH -o DEST.md`
3. Else if `uvx` on PATH: `uvx --from 'markitdown[pdf,docx,pptx,xlsx]' markitdown PATH -o DEST.md`
4. Else DEGRADED: tell the user to `pipx install 'markitdown[pdf,docx,pptx,xlsx]'` or `opencode-bf markitdown enable`. Do not pip-install into the overlay venv. Do not invent text from an unreadable binary.

Missing `uvx` is documented. Do not fall back to docker, `--http`, or `0.0.0.0`.

## Handoff

| Need | Route |
|---|---|
| Convert-only | **markitdown** |
| Understand / soal / contract / render PDF | smartdoc |
| Reusable book | smartbook-ingest |
| Paper/survey | academic (intake may convert first) |

Do not auto-run on every attached PDF if `smartdoc` native extract already returned text.

## Hard rules

- No Azure flags. No `--use-plugins`. No LLM vision OCR client.
- Native PDF/DOCX extract via `opencode-bf smartdoc` stays default when it already works.
- Bulk PPTX/XLSX/EPUB/HTML/ZIP → Markdown first may use this skill, then resume SmartDoc modes.
- markitdown output is a source file, not a contract.
