# Design Intelligence and DesignV2

## Three local systems

| Name | Root or data | Purpose | Acquisition and network |
|---|---|---|---|
| Legacy Design Bank | `OPENCODE_DESIGN_BANK` or `~/Design` | Refero, Motionsites, and local 21st/Aura visual catalogs | Existing legacy discovery; DesignV2 stores pointers only |
| Legacy Design Intelligence | `~/DesignIntelligence` | Open Design selection and retrieval reasoning inside Impeccable | Local archive catalog |
| DesignV2 | `OPENCODE_DESIGN_V2` or `~/DesignV2` | Normalized offline design/component library | User supplies local files; retrieval never uses the network |

DesignV2 is not a specialist, MCP server, marketplace mirror, or remote registry client. shadcn remains the component-installer MCP. The deprecated `GROK_DESIGN_V2` variable remains an alias for the DesignV2 root.

## Acquisition boundary

```text
USER ACQUISITION                 OPENCODEBESTFRIEND OFFLINE
legitimate export/download       security stage
          |                            |
          v                            v
local file, folder, or ZIP  ->  normalize + provenance
                                      |
                                      v
                              JSONL canonical catalog
                                 + optional FTS5
                                      |
                                      v
                         BM25 + DNA + context + trust
                          + license + anti-slop + diversity
```

OpenCodeBestFriend does not crawl Aura or 21st, reuse browser sessions, require an Aura/21st account at runtime, fetch a supplied URL, bulk-copy marketplace source, download catalog previews during ingest, or register their MCP servers. A URL passed to `import` or path-based `ingest` is rejected with `REMOTE_URL_REJECTED`. Local Aura/21st catalog banks are visual references only.

| Location | Meaning | Can implement directly? |
|---|---|---|
| aura.build / 21st.dev | Original marketplace/source platform | Only through a legitimate user account/export/copy flow |
| `Design/aura` | Local visual catalog + preview + metadata | Reference only |
| `Design/21st` | Local visual catalog + preview + metadata | Reference only |
| User-exported Aura folder | Actual local source | Yes, through the existing Aura importer |
| User-selected 21st source folder | Actual component source | Yes, through the existing 21st importer |

## Population lifecycle

```bash
opencode-bf design import ~/Downloads/my-design --provider aura
opencode-bf design sources
opencode-bf design ingest --provider aura --source-id <source_id>
opencode-bf design dedupe
opencode-bf design rebuild
opencode-bf design doctor
opencode-bf design search "premium cybersecurity dashboard dark minimal"
opencode-bf design shortlist --query "premium cybersecurity dashboard dark minimal" --framework react
opencode-bf design inspect <id>
```

`import` security-stages one local input and returns `source_id`. Re-importing the same payload returns `already_staged` with that ID and does not create a second source, including v1.1.0 UUID folders whose payload still matches. `sources` exposes the same ID. `ingest --source-id` normalizes exactly that staged source. `rebuild` refreshes FTS to schema 3 in place when the inbox generation is unchanged; item IDs, `alias_of`, and `duplicate_of` stay stable. Users do not delete `~/DesignV2`. The compatible one-step shortcut remains:

```bash
opencode-bf design ingest --provider aura ~/Downloads/my-design
```

`dedupe` records canonical relationships without deleting assets. `rebuild` atomically commits the current inbox to canonical JSONL and refreshes optional FTS5. Search, shortlist, and inspect read only the committed catalog. Search returns `catalog_item_id` and `preview_relative_path` for pointer cards. Inspect resolves that preview against `pointer.json` and reports `preview_status` without copying media.

## Provider behavior

### Aura

A local Aura catalog bank (`library/catalog.json` plus per-item preview/meta) is ingested as a pointer catalog. DesignV2 does not copy preview media and does not stage the library tree. Cards record `source.upstream_id` and `source.path` (preview relative to the catalog root). Still previews may be webp, png, jpg, jpeg, or avif. Remix HTML is obtained on aura.build when the user account allows it; it is not present in the catalog bank.

Aura also accepts one user-exported HTML/CSS/JavaScript folder, `DESIGN.md`, or an explicit user metadata file named `design-v2.json`. An arbitrary proprietary `manifest.json` is not reverse-engineered. To use `manifest.json`, place supported fields under `opencode_design_v2`.

Supported user-declared fields are bounded to `name`, `description`, `kind`, `role`, `frameworks`, `categories`, `tags`, `product_fit`, `intent`, `modes`, `anti_slop`, and `dna`. Invalid explicit manifests fail closed. Unknown layouts return `UNKNOWN_AURA_LAYOUT`.

### 21st

A local 21st catalog bank (`library/catalog.json` plus per-item preview/meta) is ingested as a pointer catalog. DesignV2 does not copy preview media, does not run `21st get`, and does not stage the library tree. Cards record `source.upstream_id` and `source.path` (preview relative to the catalog root). Component source is copied on 21st.dev when the user account and quota allow it; it is not present in the catalog bank.

21st also accepts one user-selected local component folder. Marketplace pages, scrape JSON, and media dumps are rejected. Trust defaults to `unknown`; redistribution defaults to `local-only`; license remains `unknown` unless a local license file provides recognized evidence. Provenance is not treated as license permission. `import` of a catalog-bank root is rejected with `CATALOG_POINTER_ONLY`; use `ingest --provider 21st|aura` on that root instead.

Lightweight preview images already present in the user package may be preserved and recorded as user-supplied preview media. Videos and animated marketplace media are skipped. The importer never downloads preview media.

### GitHub OSS

`github-oss` accepts local source selected by the user. The provider name does not prove upstream identity or trust. React is detected from source evidence; Tailwind is detected only from config, dependencies, or utility-class evidence. Package scripts are data and are never executed.

### Open Design

Open Design remains an adapter over a valid local legacy Design Intelligence bank containing `catalog.lock.json`. DesignV2 does not parse a second raw ZIP format.

### Refero and Motionsites

DesignV2 writes bounded catalog metadata and local pointers. It does not copy the legacy media library. Refero catalogs may list styles under `styles`. Broken pointer targets, including 21st and Aura catalog pointers, are reported by doctor. Doctor also requires pointer catalogs to parse, `items`/`styles` to be valid, `copied_media` not true, and a bounded sample of preview files to exist.

## Normalization evidence

Normalized records carry `extraction_evidence` entries prefixed with `detected:`, `inferred:`, or `user-declared:`. Missing evidence remains unknown and is surfaced through warnings such as `LICENSE_UNKNOWN`, `FRAMEWORK_UNKNOWN`, and `PRODUCT_FIT_UNKNOWN`.

Design DNA remains lexical and interpretable. Dimensions include aesthetic, density, geometry, typography, spacing, color, hierarchy, layout, motion, interaction, responsive behavior, product fit, content style, visual complexity, and accessibility. No embeddings or vector database are used.

Anti-slop is a ranking penalty, not a ban. Explicit requests such as `glass futuristic dashboard` reduce the relevant glass penalty. Explicit avoidance such as `no slop` increases penalties. Unrelated phrases such as `not childish` do not globally activate anti-slop avoidance. Structural query nouns such as `button`, `hero`, `pricing`, `shader`, and `landing` boost matching kind and category (for example a button query prefers `component`/`button` over an effect whose name happens to contain button).

## Health report

`opencode-bf design doctor` verifies the lock, canonical JSONL hash, optional SQLite hash, and FTS schema. It also reports bounded counts for providers, kinds, frameworks, license status, local-only items, quarantine, duplicates, missing local paths, broken pointers, DNA coverage, weak metadata, missing product fit, and missing framework metadata. Pointer health checks catalog JSON, item lists, `copied_media`, and a sample of preview paths — it does not scan every preview.

Use machine-readable output when needed:

```bash
opencode-bf design doctor --json
opencode-bf design status --json
```

JSONL remains canonical. Missing or stale FTS is `DEGRADED_FTS`, not a failed catalog generation; `rebuild` refreshes it. Read-only commands (`status`, `search`, `inspect`, `doctor`, `sources`, and `shortlist`) do not create the bank.

## Impeccable integration

`skills/impeccable/scripts/design_v2.py` is a read-only thin adapter exposing status, search, shortlist, inspect, doctor, and sources. It does not expose import, ingest, dedupe, or rebuild.

Search and shortlist open no asset folders and return bounded metadata cards with direction, system/style, structure, patterns, motion, reasons, compatibility, license/trust, avoid flags, and one `inspect_id`. Impeccable inspects only the user-selected candidate. It never loads the entire bank into model context.
