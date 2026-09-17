# Skills

Policy: `vendor/skill-policy.json` plus `vendor/skill-allowlist.txt`.

- 48 model-invoked skills live under `skills/` and install to `~/.config/opencode/skills/` (core + Wave 2/3 warehouse specialists)
- 16 manual skills live under `manual-skills/` and install to `~/.config/opencode/bestfriend/skills/` plus `commands/`

`smartdoc` is per-job document intelligence. `markitdown` converts Office/PDF/HTML/CSV/XLSX/PPTX/EPUB/ZIP to Markdown for ingest; SmartDoc keeps contract/QA/render. `smartbook-ingest` compiles reusable local knowledge. `humanizer` cleans user-facing prose tells (`/unslop` is its manual alias). `academic` manages scholarly research, writing, and peer review. `hyperframes` handles deterministic HTML-to-MP4 video composition. `diagram-design` crafts editorial HTML/SVG diagrams. `img2threejs` reconstructs procedural Three.js models from reference images. Warehouse diagnostics include `agent-architecture-audit` (agent stack layers), `cost-aware-llm-pipeline` (token budgeting), `eval-harness` (benchmarks), `prompt-optimizer` (prompt refinement), and `skill-stocktake` (catalog hygiene). Wave 3 adds `api-design`, `contract-first`, `automation-audit-ops`, `code-tour`, and `click-path-audit`. Handwriting is a SmartDoc renderer, not a skill.

OpenCode 1.18.x has no `disable-model-invocation` field. Manual skills must not be copied into the discovered skills directory.

`opencode-bf skills verify` checks counts, missing files, and duplicates.

pstack / poteto-mode is not a 65th skill. Playbooks route through `docs/routing.md` and `docs/pstack-inventory.md`.
