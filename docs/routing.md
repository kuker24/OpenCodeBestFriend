# Routing

Philosophy:

```text
pikir dulu → bukti di repo → satu spesialis → cek hasil
```

Load `00-routing.md` only when the thin router is not enough. Do not `@`-import rules.

One primary specialist per problem. At most one risk specialist (`full-audit-keamanan` XOR `full-performance-audit`). Availability is not a reason to activate a tool. For mixed requests (e.g. landing + button + video), pick the primary largest surface (typically `impeccable`); motion or video is step 2 after user pick, never a parallel load.

Manual specialists stay behind slash commands. Suggest them when the user names the job. Product interviews, glossaries, and ADRs route to `grill-with-docs` (including frontier rounds). Spec and ticket implementations stay in-session with `tdd`. Workflow choice is resolved directly via the router without an extra specialist.

Tool reporting:

```text
USED
CONSIDERED_NOT_USED
MANUAL_NOT_INVOKED
```

Never list unused tools as used.

UI direction from the bank routes to `found-this-design` first, which stops before component implementation. Visual UI and UI atoms (buttons, inputs, cards, nav) route to `impeccable` after Design V2 shortlist; BANK_MISS ≠ generate (+ shadcn/Design V2 internal). Stitch MCP is for screen/comp generation only, then found-this-design or impeccable with Design V2 atom shortlisting; never implement production UI from Stitch alone. UI Skills MCP is design-skill lookup only; product UI remains Design Bank + Impeccable + Design V2 atoms + shadcn; BANK_MISS ≠ generate from a random ui-skills document. Motion UI routes to `emil-design-eng`. Still/ads/non-UI surface route to `visual-studio`. Scroll-led stories route to `scroll-craft`, while continuous camera 3D fly-throughs route to `scroll-world`. Procedural Three.js object models from reference images route to `img2threejs`.

Browser verification follows four explicit doors: exploratory application UI routes to `playwright-qa`, persistent multi-account sessions route to `browser-act`, observed Chromium cause routes to `chrome-devtools-axi`, and button handler sequential undo / shared-store side effects route to `click-path-audit`.

Documents (answer, create, transform, extract, review, PDF/DOCX) route to `smartdoc`. File-to-Markdown ingest routes to `markitdown`. Reusable book/module knowledge routes to `smartbook-ingest`. `/docx` and `/pdf` are missing aliases; nearest is `smartdoc`. `/pptx` is NOT_APPLICABLE. Do not add `commands/pdf.md` or `commands/docx.md`. Impeccable `document` remains DESIGN.md generation.

Prose AI-tell removal and natural tone polishing route to `humanizer` (`/unslop` is its manual alias). Scholarly research, academic manuscripts, and structured peer critique route to `academic`. Deterministic HTML composition rendered to video routes to `hyperframes`. Demo video aplikasi, walkthrough layar, narasi Indonesia, dan demo lomba route to `id-demo-video` (bukan `hyperframes` untuk durasi panjang utuh, bukan `playwright-qa`, bukan `visual-studio`). Kartu judul HTML→MP4 tetap `hyperframes`. Editorial technical diagrams (HTML/SVG) route to `diagram-design`.

Warehouse diagnostics load only when the user names the job: `agent-architecture-audit` (architecture layers), `cost-aware-llm-pipeline` (token budgeting), `eval-harness` (benchmarks), `prompt-optimizer` (prompt refinement), and `skill-stocktake` (catalog hygiene). Wave 3 warehouse procedures route to `api-design` (REST resources), `contract-first` (consumer/provider contracts), `automation-audit-ops` (live inventory), and `code-tour` (guided tours). Foreign harnesses (such as ECC control plane) remain `FOREIGN_ON_DEMAND`; never vendored, auto-merged, or shadowed.

Operational stack adapters route to `supabase-ops` (Supabase Auth/RLS/migrations/Edge Functions), `mongodb-ops` (MongoDB schemas/indexing/aggregation), and `vercel-ops` (Vercel hosting/deploy config). These operational skills never generate visual UI and never replace `found-this-design` or `impeccable`. FOREIGN vendor packs stay off the overlay; user may npx skills add mongodb/agent-skills|supabase/agent-skills locally; never frontend-design for product UI.

Architecture and comprehension routes: how it works / where it lives routes to Codebase Memory, then `code-tour`; architectural rationale routes to manual `/why`; break risk routes to manual `/blast-radius`. Generic AI UI aesthetics route to `impeccable` taste-guard (never `install-anti-slop`); generic AI prose routes to `humanizer` (`/unslop`); TypeScript static linting routes strictly to `install-anti-slop` upon explicit request. A `DESIGN.md` without a Design Bank match still filters slop without inventing brand assets. Pstack playbooks route to existing specialists (no `/poteto-mode`). Foreign harness control planes or continual learning loops that attempt to mutate `AGENTS.md` or skill definitions are strictly rejected.
