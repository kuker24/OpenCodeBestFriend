# Design Intelligence and Design V2

Design Bank (Refero + Motionsites) is unchanged. Design Intelligence legacy (Open Design ZIP catalog) stays inside Impeccable.

Design V2 is an **offline** user-data bank. Core lives in `lib/design_v2/`. Search does not use the network.

```text
ONLINE (user brings files)     OFFLINE
  import_stage                       lib/design_v2
        ↓                                  ↓
  ~/DesignV2  USER DATA            JSONL canonical
                                         + optional FTS5
                                         ↓
                         BM25 / DNA / taxonomy / compatibility
                               / trust / anti-slop / diversity
```

- Root: `OPENCODE_DESIGN_V2` (deprecated alias `GROK_DESIGN_V2`) or `~/DesignV2`. Not installer-owned. Uninstall does not touch it.
- JSONL is the canonical catalog. FTS5 is an optional accelerator. Missing FTS is `DEGRADED_FTS`, not a failed generation.
- FTS candidates use BM25 before DNA, taxonomy, intent/mode, framework compatibility, trust/license, anti-slop, and diversity ranking.
- Doctor verifies the JSONL and SQLite SHA-256 values recorded in `catalog.lock.json`.
- Read-only commands (`status`, `search`, `inspect`, `doctor`, `sources`, `shortlist`) do not create the bank.
- 21st.dev / Aura are **not** runtime providers. No MCP. Online only to import user-obtained files.
- Aura ingest: official HTML/CSS/JS or `DESIGN.md` export. Unknown layout is rejected.
- 21st ingest: user-selected source folder only. Marketplace HTML, scrape JSON, and thumbnail dumps are rejected. Always `local-only`.
- Open Design ingest: adapter over the legacy DI bank (`catalog.lock.json`). Raw ZIP is not parsed in V2.
- Refero/Motionsites: catalog pointer only. Media is not copied.
- Impeccable uses `skills/impeccable/scripts/design_v2.py` as a thin shim. The engine is never copied into the skill.
- Design V2 is not a specialist. shadcn remains the only component-installer MCP.

CLI:

```text
opencode-bf design status|search|inspect|rebuild|doctor|ingest|dedupe|import|sources|shortlist
```

- `import <path> [--provider]` — stage files only
- `ingest --provider <aura|21st|open-design|refero|motionsites|github-oss|manual> [path]`
- `dedupe` then `rebuild` to commit the catalog
- `shortlist --query "..." [--intent] [--mode] [--framework <name>] [--structure-only]` — bounded offline retrieval for Impeccable
