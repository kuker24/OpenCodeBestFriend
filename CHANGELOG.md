# Changelog

## Unreleased

No unreleased changes.

## 1.7.1 — 2026-09-05

Release provenance hardening. No new skills. `scroll-craft` runtime is unchanged.

- Build release artifacts from an explicit immutable git commit. HEAD mismatch, dirty worktree, and VERSION/tag mismatch fail closed.
- SHA256SUMS covers the tarball, SPDX 2.3 SBOM, and release provenance. The sums file is not self-hashed.
- Record product, version, source repository, source tag, source commit, prompt SHA-256, and tarball identity in `release-provenance.json`.
- Pin the canonical prompt SHA-256 in `vendor/release-contract.json`.
- SBOM packages now include license, version/commit when known, download location, and CONTAINS relationships.
- Add `scripts/verify-release-artifacts.sh` and a `release-artifact` CI job with extract smoke and a second-build reproducibility check.
- GitHub release immutability remains `NOT_CONFIGURED`. Signed tags remain `DEFERRED`.

## 1.7.0 — 2026-09-05

- Add model-invoked `scroll-craft` for scroll-led storytelling. Continuous camera worlds stay `scroll-world`. Skills remain 43 total, 27 model, 16 manual.
- Remove worldflight from the ScrollCraft runtime and CSS, and hand that responsibility to `scroll-world` without a dormant alternative implementation.
- Make `destroy()` release per-mount listeners, observers, animation frames, timers, image callbacks, pending clip fetches, and Blob URLs; anchor jumps and keyboard focus now land on readable pinned content.
- Split the safe mechanism CSS from the optional scoped starter theme.
- Add dependency-free Chromium/CDP interaction and lifecycle regression coverage for desktop, mobile, reverse scroll, reduced motion, keyboard, anchors, network isolation, and remounting.
- Upgrade GitHub JavaScript Actions to immutable Node 24 releases and require the complete CI suite before merging `main`.
- Snapshot skill wrappers inherit GrokBestFriend MIT (`vendor/licenses/GROKBESTFRIEND-MIT.txt`); frontmatter now states `license: MIT`. Separate CLIs stay their own packages.
- GitHub rulesets protect `main` and `v*` tags from force-push and deletion. Signed tags remain deferred until a maintainer signing key exists.

## 1.6.2 — 2026-09-02

SmartDoc correctness micro-release. No new skills. v1.6.1 stays published.

- Distinguish `PdfRasterEnd` from `PdfRasterFailed` so interior raster errors are `PARTIAL`, not silent truncation.
- Empty Local Similarity Audit corpus is `AUDIT_NOT_RUN` / `EMPTY_CORPUS` with no score.
- Image OCR `PARTIAL` reaches `page_record.status` and SmartBook `source_status`.
- `smartbook retrieve` returns source page, method, confidence, warnings, and status.
- `smartdoc render` stays `PARTIAL` when source extraction was partial.
- Profile/style wiring to public render remains deferred.

## 1.6.1 — 2026-09-02

SmartDoc final stabilization. No new skills.

- Remove silent PDF truncation: native pages are not constrained by the 200-page OCR budget; OCR limit/deadline results are explicit `PARTIAL` with page provenance.
- Preserve SmartBook source page numbers, method, confidence, warnings, and unavailable-page markers through staged atomic ingest.
- Fail Local Similarity Audit closed for unreadable source/corpus items and disclose partial extraction coverage.
- Add public `smartdoc render --renderer handwriting` with content lock, atomic PDF output, structural QA, and real post-raster QA.
- Guard image pixels before full decode, bound subprocess output, and mark truncated OCR TSV as `PARTIAL`.
- Replace capability-only mixed doctor check with a real native-plus-OCR PDF probe.
- Add a real OCR CI job and pin GitHub Actions to immutable commit SHAs.
- Include `vendor/sources.json` in product version consistency checks.

## 1.6.0 — 2026-09-01

SmartDoc mixed-document OCR. No new skills.

- Hybrid extract: native PDF text when sufficient, Tesseract OCR AUTO fallback per page. Combined PDF text joins pages with form-feed.
- Image OCR with EXIF-aware preprocess, confidence bands, and `OCR_CRITICAL_UNCERTAINTY` when numbers/units/formulas are weak. Never invent unread text.
- Optional stack: `pypdf`, Pillow, `pdftoppm`, `tesseract` (`eng`/`ind`). Missing tools stay `NOT_CONFIGURED`.
- Doctor checks tesseract, languages, OCR_IMAGE, OCR_PDF, mixed-document path, and profile roundtrip.
- Unreadable PDFs fall through to OCR instead of crashing when pypdf cannot parse.

## 1.5.1 — 2026-09-01

SmartDoc stabilization from real-document dogfood. No new skills.

- Add `opencode-bf smartdoc doctor --json` smoke tests (root, profile, DOCX, pypdf, Pillow, PDF assembly, pdftoppm, SmartBook, temp cleanup).
- Split heading-less SmartBooks on form-feed pages or paragraph windows so retrieve can hit the middle of a book.
- Weight retrieve scores toward section bodies; question-only titles lose.
- Golden E2E coverage for the six dogfood attack points. PDF_READ remains optional `NOT_CONFIGURED`.

## 1.5.0 — 2026-09-01

SmartDoc and SmartBook.

- Add model-invoked `smartdoc` (per-job document intelligence) and `smartbook-ingest` (reusable local knowledge). Skills 42 total, 26 model, 16 manual.
- Deterministic runtime in `lib/smartdoc/`: contract lock, sanitize, DOCX zip/XML extract, profiles, Local Similarity Audit against a named corpus, handwriting renderer.
- User data lives under the resolved SmartDoc root (`OPENCODE_SMARTDOC` or `~/SmartDoc`). Uninstall preserves it.
- Optional `pypdf` / Pillow / `pdftoppm` degrade to `NOT_CONFIGURED`. No Turnitin claim, no detector-evasion loop, no new MCP.

## 1.4.0 — 2026-08-31

Portable full Design Bank bootstrap.

- Add opt-in `opencode-bf design bootstrap` and `./install.sh --with-design-bank`; normal installation remains lightweight and never starts the multi-gigabyte download.
- Acquire the public Google Drive archive with curl retries/resume, a downloaded checksum, and a bundled pinned SHA-256 trust anchor.
- Reject malformed or unsafe ZIPs with bounded member, size, depth, path, encryption, special-file, and compression-ratio policies.
- Extract and validate 21st, Aura, Refero, and Motionsites catalogs in temporary storage before atomically committing the user-owned `~/Design` tree.
- Pointer-ingest into `~/DesignV2` without copying preview media, then dedupe, rebuild, and run doctor entirely offline.
- Preserve existing compatible banks, fail closed on incompatible targets, and leave `~/Design` plus `~/DesignV2` untouched during uninstall.
- Validated with the genuine 3+ GB archive: 30,612 cards, zero broken pointers, zero copied media, and offline retrieval lifecycle PASS.

## 1.3.0 — 2026-08-30

Offline visual catalog expansion and retrieval refinement.

- Pointer-index local 21st and Aura visual catalogs without copying preview media.
- Item-level preview traceability from search and inspect into the original local Design Bank.
- Hardened pointer doctor with catalog validation and bounded preview sampling.
- Kind-aware ranking for components, sections, effects, pages, and templates.
- Local AVIF preview support.
- Existing single-source Aura/21st imports remain unchanged.
- Validated against a 30,612-item local catalog with FTS5 and offline retrieval on an 8 GB system.

## 1.2.0 — 2026-08-30

Design Engine V2 population workflow. No new skills or MCP.

- Lifecycle: `import` → `sources` → `ingest --source-id` → `dedupe` → `rebuild` → `doctor` → `search`/`shortlist`/`inspect`
- Idempotent import: same payload returns `already_staged` with the original `source_id`, including v1.1.0 UUID folders
- FTS schema 3 rebuild in place; item IDs, `alias_of`, and `duplicate_of` stay stable. Users do not delete `~/DesignV2`
- Metadata evidence prefixes, 15-D lexical DNA, contextual anti-slop, framework-aware dedupe
- Bounded doctor health report; Impeccable shim read-only; URL inputs rejected with `REMOTE_URL_REJECTED`

## 1.1.0 — 2026-08-30

Offline Design Engine V2. No new skills or MCP.

- `opencode-bf design {status,search,inspect,rebuild,doctor,ingest,dedupe,import,sources,shortlist}`
- User bank at `OPENCODE_DESIGN_V2` or `~/DesignV2` (deprecated alias `GROK_DESIGN_V2`). Not installer-owned
- JSONL canonical catalog; FTS5 optional (`DEGRADED_FTS`). Read-only commands do not create the bank
- Ingest: Aura export, user-selected 21st/github-oss, Open Design v1 adapter (no ZIP parser), Refero/Motionsites pointer
- Impeccable thin shim `design_v2.py`; shortlist is lazy inside `new-work`. Design V2 is not a specialist
- Doctor reports EMPTY/PASS/DEGRADED/DEGRADED_FTS for Design V2. Uninstall does not touch `~/DesignV2`
- Release hardening: installed V2 runtime integrity, BM25 candidates, intent/mode/framework/trust ranking, catalog hashes, fail-closed secret coverage, replace-not-merge ingest, and FTS recovery

## 1.0.5 — 2026-08-28

Runtime integrity, migration, and supply-chain hardening. No new skills or MCP. Nine snapshot skills remain unknown — not a grant.

- `opencode-bf verify` checks product identity and SHA-256 of owned runtime files
- `doctor --deep` fails unless core MCP is live `CONNECTED` (no false-green)
- `doctor --strict` treats `DEGRADED`/`WARN` as failure; Serena stays optional
- Product identity: `product`, `productVersion`, `sourceRepository` must match this release
- Detects stale AGENTS.md (missing USED/CONSIDERED_NOT_USED/MANUAL_NOT_INVOKED) and stale routing title
- Migrates ClaudeBestFriend 1.4.2-claude.1 overlays (legacy helpers replaceable; foreign MCP/provider preserved)
- Host gate: `node`/`npx` required when shadcn MCP is enabled; wildcard `"*": "allow"` is `DEGRADED_SECURITY` (not mutated)
- Isolation scan skips `state/` (pre-install Claude snapshot is not an active dependency); migrate removes leftover `components/installer`
- `doctor --deep` keeps MCP `CONNECTED` when a later path line repeats the server name
- CBM CLI parser ignores `level=info` log lines mixed with JSON
- Uninstall/restore fail-closed on path/stamp traversal; archive extract rejects absolute/symlink/hardlink/Windows traversal
- Context Guard reported as `NOT_APPLICABLE` / `NOT_PORTED_BY_DESIGN`
- `opencode-bf cbm status|index` and `security-profile` (recommendation only)

## 1.0.4 — 2026-08-21

Installer freeze-prep. No new skills or MCP. Nine snapshot skills remain unknown — not a grant.

- `opencode-bf serena enable` uses surgical MCP merge; JSONC comments, provider, and foreign MCP are preserved; existing `serena` is not overwritten
- Collision preflight runs after `VALIDATED` and before backup/apply (skills, commands, helpers, parseable config, AGENTS type, writable targets)

## 1.0.3 — 2026-08-21

Installer hardening. No new skills or MCP. Nine snapshot skills remain unknown — not a grant.

- Foreign `~/.local/bin/opencode-bf` and `opencode-chromium-cdp` fail closed; uninstall removes owned helpers only
- Upgrade rollback copies `share/product` and `share/components` when they already existed
- Design Bank and Codebase Memory archives reject path traversal (`..`, absolute, outbound links)

## 1.0.2 — 2026-08-21

Installer polish. No new skills or MCP.

- Absence-aware rollback: `preInstall` records absent vs present; recover deletes installer-created files that did not exist before apply
- MCP `--deep` parser is per-line / per-server (`disconnected` is not `connected`)
- Doctor `AGENTS.md` thickness counts only the `OPENCODEBESTFRIEND` block
- `vendor/provenance.json` `productVersion` matches the product
- License audit: 7 more skills pinned to mattpocock/skills MIT (`ask-matt`, `grill-with-docs`, `to-spec`, `to-tickets`, `tdd`, `matt-code-review`, `matt-implement`). 9 skills remain unknown — not a grant.

## 1.0.1 — 2026-08-21

Hardening release. No new skills or MCP.

- Merge `AGENTS.md` via `OPENCODEBESTFRIEND` markers; preserve foreign text
- Fail closed on foreign command collisions (`/architect`, `/why`, …)
- Installer lifecycle includes `VERIFIED` before `COMMITTED`
- Broader pre-apply backup and restore (config, AGENTS, commands, skills, bestfriend, helpers, shell rc)
- Doctor `~/.claude mutations` uses a real file-hash baseline (`NOT_BASELINED` if missing)
- MCP doctor reports `CONFIGURED` (not live CONNECTED); `--deep` may probe `opencode mcp list`
- OpenCode gate is exact `1.18.x`
- JSONC comments preserved via surgical MCP merge (fail closed if surgical merge cannot parse)
- Complete 40-skill license audit (`vendor/license-audit.json`); unknown licenses are not grants

## 1.0.0 — 2026-08-21

Initial public OpenCodeBestFriend release.

- 40 skills (24 model-invoked, 16 manual commands)
- Thin `AGENTS.md` router with `USED` / `CONSIDERED_NOT_USED` / `MANUAL_NOT_INVOKED` reporting
- Core MCP: Codebase Memory 0.9.0, Context7, shadcn@4.18.0
- Design Bank discover-or-download (media not in git)
- Design Intelligence portable runtime
- Transactional installer, doctor, uninstall, restore
- Claude Code isolation; Context Guard not ported
- Tested against OpenCode stable 1.18.x on Linux x86_64

Adapted from ClaudeBestFriend 1.4.2-claude.1 (`05e6fdcdb70fe7f4420827e4df1a360f2152700c`).
