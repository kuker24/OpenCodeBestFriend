# Wave A Modernization Notes

Catalog modernization summary for OpenCodeBestFriend: retiring obsolete twins, compressing overlapping primitives, tightening boundaries, and upgrading surviving specialists.

## Final Catalog Counts

| Category | Prior (1.8.5) | After Wave A | Delta |
|---|:---:|:---:|:---:|
| **Model-Invoked Skills** (`skills/*/SKILL.md`) | 49 | **47** | -2 (`ask-matt`, `grilling`) |
| **Manual Commands** (`manual-skills/*/SKILL.md` + `commands/*.md`) | 17 | **15** | -2 (`matt-implement`, `wait-what`) |
| **Total Allowlist Items** (`vendor/skill-allowlist.txt`) | 66 | **62** | -4 |

All assertions in `tests/test_skills.py`, `tests/test_routing.py`, `tests/test_license_audit.py`, `tests/test_version.py`, and documentation tables match the measured tree. No padding.

---

## Dispositions

### 1. Retired & Compressed

- **`wait-what`** (Manual) → **RETIRED**
  - *Rationale*: Convenience re-pitch failed the existence gate against standard technical writing and repository domain discipline.
  - *Residue*: Moved into a single re-pitch instruction in `rules/03-prose-discipline.md` (stop, brief context, ASD-STE100 Simplified Technical English, ubiquitous language from `CONTEXT.md`).
  - *Target*: `technical-writing` + `rules/03-prose-discipline.md`.

- **`grilling`** (Model) → **COMPRESSED into `grill-with-docs`**
  - *Rationale*: Grilling as a primitive without documentation produces transient decisions. Full planning interviews were already using `grill-with-docs`.
  - *Residue*: Frontier rounds and design-tree structure merged directly into `skills/grill-with-docs/SKILL.md`. Model skill directory removed.

- **`ask-matt`** (Model) → **RETIRED**
  - *Rationale*: Having a specialist dedicated solely to choosing which workflow to run is a category error that adds token overhead on every session turn. The router (`templates/AGENTS.md` and `rules/00-routing.md`) handles workflow selection directly without loading a specialist.
  - *Residue*: Standard category mapping and router checklist moved to `skills/writing-for-agents/references/route-checklist.md`; session transition decision tree preserved in `skills/writing-for-agents/references/phase-boundaries.md`.

- **`matt-implement`** (Manual) → **RETIRED**
  - *Rationale*: Twin of in-session implementation and `tdd`. Spec-driven implementation and tracer-bullet tickets from `/to-tickets` execute directly in-session using `tdd`.
  - *Target*: In-session write + `tdd`. Boundary line added to `skills/tdd/SKILL.md`.

### 2. Decided & Kept

- **`wizard`** (Manual) → **KEPT**
  - *Rationale*: Distinct from agent setup or OCBF doctor. Generates interactive bash wizards for steps only a human can perform (OAuth, secret provisioning, cloud dashboard cutover).
- **`codebase-design`** (Model) & **`/improve-codebase-architecture`** (Manual) → **BOTH KEPT**
  - *Rationale*: Non-overlapping responsibilities. `codebase-design` defines single-module interface depth and seams; `improve-codebase-architecture` performs whole-codebase scans for shallow modules and generates visual zero-network HTML reports. Boundaries mutually clarified in frontmatter descriptions.

### 3. Updated Survivors (Bodies Only — Zero New Names)

- **`impeccable`**:
  - Incorporated 4-tier Taste Gate architecture into `reference/taste-guard.md`: Hard Gate (absolute bans on hallucinated data/fake proof/status dots/two-state layouts), Purpose-Gate (reason required for animations/marquees/glass), Quality Locks (surface mode, contrast, reduced-motion, states), and Delivery Gate (pre-ship check).
  - Explicit rule: Filter ≠ style guide. Filters remove category defaults; direction comes from Design Bank or `DESIGN.md`.
  - Enforced `BANK_MISS ≠ generate`.
  - Stated that `DESIGN_VARIANCE`, `MOTION_INTENSITY`, and `VISUAL_DENSITY` dials in `taste/direction.md` are optional controls evaluated *after* a direction exists.
  - Reaffirmed that Stitch MCP (comps only) and UI Skills MCP (lookup only) never implement production UI alone.
- **`humanizer`**:
  - Added During-Generation vs After-Audit copy checks adapted from anti-slop copy rules without raw rule dumping.
  - Explicit boundary: strictly refuses UI implementation and static linter (`install-anti-slop`) installation.
- **`scroll-world`**:
  - Updated camera style intake choices and seam QA (evaluates composition and vector continuity, not numerical PSNR).
  - Explicit `NOT_CONFIGURED` degradation note when paid video backends (Monid, Higgsfield, Kling) are absent.
  - Preserved boundary: `scroll-craft` (2D scrollytelling) vs `scroll-world` (3D continuous camera flight).
- **`markitdown`**:
  - Pinned to current Microsoft `markitdown` v0.1.7 (`945314a`).
  - Stated that output is Markdown data; SmartDoc retains contract, QA, and rendering ownership. Optional stdio MCP remains enable-gated.
- **`gh-axi` & `chrome-devtools-axi`**:
  - Updated command surfaces from upstream `kunchenguid/axi` (`fb75216`). No generic `axi` skill introduced.
  - Enforced 4-door browser hierarchy: `playwright-qa` → `browser-act` → `chrome-devtools-axi` → `click-path-audit`.
- **`browser-act`**:
  - Documented three supported execution modes: `chrome` (profile reuse), `stealth-fresh` (ephemeral), and `stealth-fixed` (persistent).
  - Reaffirmed strict ban on `--type chrome-direct`. Reaffirmed that `playwright-qa` remains the primary default verifier.
- **`found-this-design`**:
  - Added explicit allowance for humans referencing external DESIGN.md patterns (e.g. `awesome-design-md`) while strictly forbidding fetching, cloning, or vendoring brand packs. Product UI stays Design Bank → `impeccable`.
- **`code-tour` & `why`**:
  - Added "How it works" and "Where it lives" tour scaffolding to `code-tour`.
  - Added optional critique step to `/why` to evaluate whether historical rationale still holds.

### 4. Rejected Upstream Additions

- **`affaan-m/ECC`**: Rejected vendoring control plane and 292 skills. Remains `FOREIGN_ON_DEMAND`. Doctor does not fail when absent.
- **`ashemag/human-atlas`**: Rejected 3D anatomy application from catalog.
- **`VoltAgent/awesome-design-md`**: Rejected cloning brand files into overlay.
- **Cursor SaaS Plugins**: Rejected connectors for Gmail, HubSpot, Salesforce, Gong, etc.
- **Autopilot Loops**: Rejected `ralph-loop`, `orchestrate`, and `continual-learning` that auto-mutate agent rules or skills.
