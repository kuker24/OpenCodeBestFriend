# OpenCodeBestFriend — Skill Warehouse Inventory

This inventory establishes the contract for warehouse skills across the five analyzed upstream repositories:
1. `blader/humanizer` (MIT)
2. `cathrynlavery/diagram-design` (MIT)
3. `heygen-com/hyperframes` (Apache-2.0)
4. `Imbad0202/academic-research-skills` (CC-BY-NC-4.0)
5. `affaan-m/ECC` (MIT)

## Contract Rules
- Decisions: `NEW | MERGE | REJECT | DEFER | DONE`
- Batch `2a`: Rows marked `decision=NEW` with `batch=2a` were ported in Wave 2.
- Batch `3a`: Only remaining `DEFER` rows marked `decision=NEW` with `batch=3a` are ported in Wave 3. Do not reopen `REJECT`. Do not re-port `DONE`/`MERGE`.
- External harness runtimes, auto-mutations, and CC-BY-NC text are strictly REJECTED.

## Summary Counts

| Decision | Count | Description |
| :--- | :---: | :--- |
| `NEW` | 10 | Uniquely missing capabilities ported to first-party MIT BestFriend specialists (Batch 2a + 3a) |
| `DONE` | 3 | Specialists already ported to OpenCodeBestFriend (`humanizer`, `diagram-design`, `hyperframes`) |
| `MERGE` | 83 | Capabilities merged into existing BestFriend specialists or references (zero text plagiarism) |
| `REJECT` | 158 | Foreign harness runtimes, framework sprawl, trading bots, vendor ops, and incompatible licenses |
| `DEFER` | 64 | Domain-specific procedures cataloged for future warehouse wave evaluation |
| **TOTAL** | **318** | Total upstream skill items cataloged |

---

## Detailed Inventory Table

| Source | Upstream Name | Decision | BestFriend Target | Reason | Batch |
| :--- | :--- | :---: | :--- | :--- | :---: |
| `blader/humanizer` | `humanizer` | **DONE** | `skills/humanizer` | Ported in Wave 1 as model-invoked specialist with semantic-preservation constitution; /unslop aliases it | `-` |
| `cathrynlavery/diagram-design` | `diagram-design` | **DONE** | `skills/diagram-design` | Ported in Wave 1; expand references/types.md with 39-type catalog in Batch 2a without HTML gallery dumps | `2a` |
| `heygen-com/hyperframes` | `embedded-captions` | **MERGE** | `hyperframes` | Part of HyperFrames caption overlay architecture; merged into references/composition.md | `-` |
| `heygen-com/hyperframes` | `faceless-explainer` | **MERGE** | `hyperframes` | Prompt workflow utilizing the core HTML-to-video compiler; documented in references/workflows.md | `-` |
| `heygen-com/hyperframes` | `figma` | **DEFER** | `-` | Requires external Figma API credentials; FOREIGN_ON_DEMAND | `-` |
| `heygen-com/hyperframes` | `general-video` | **MERGE** | `hyperframes` | Prompt workflow for general narrative video; documented in references/workflows.md | `-` |
| `heygen-com/hyperframes` | `hyperframes-animation` | **MERGE** | `hyperframes` | GSAP/CSS animation techniques for seekable HTML video; merged into references/composition.md | `-` |
| `heygen-com/hyperframes` | `hyperframes-audio` | **MERGE** | `hyperframes` | Audio and SFX alignment procedures; merged into references/composition.md | `-` |
| `heygen-com/hyperframes` | `hyperframes-cli` | **MERGE** | `hyperframes` | CLI render invocations and Chrome flags; documented in references/render.md | `-` |
| `heygen-com/hyperframes` | `hyperframes-core` | **MERGE** | `hyperframes` | Core timeline and frame-budget concepts; documented in references/composition.md | `-` |
| `heygen-com/hyperframes` | `hyperframes-creative` | **MERGE** | `hyperframes` | Creative frame presets and palette guidelines; merged into references/composition.md | `-` |
| `heygen-com/hyperframes` | `hyperframes-keyframes` | **MERGE** | `hyperframes` | Deterministic keyframe scrubbing patterns; documented in references/composition.md | `-` |
| `heygen-com/hyperframes` | `hyperframes-registry` | **MERGE** | `hyperframes` | Component and template registry reuse; documented in references/composition.md | `-` |
| `heygen-com/hyperframes` | `hyperframes` | **DONE** | `skills/hyperframes` | Core deterministic HTML-to-MP4 video specialist ported in Wave 1 | `-` |
| `heygen-com/hyperframes` | `media-use` | **MERGE** | `hyperframes` | Media asset integration and LUT color handling; documented in references/composition.md | `-` |
| `heygen-com/hyperframes` | `motion-graphics` | **MERGE** | `hyperframes` | Motion graphics building blocks; documented in references/workflows.md | `-` |
| `heygen-com/hyperframes` | `music-to-video` | **MERGE** | `hyperframes` | Beat-synced video generation workflow; documented in references/workflows.md | `-` |
| `heygen-com/hyperframes` | `pr-to-video` | **MERGE** | `hyperframes` | Pull request walkthrough video workflow; documented in references/workflows.md | `-` |
| `heygen-com/hyperframes` | `product-launch-video` | **MERGE** | `hyperframes` | Product launch video workflow; documented in references/workflows.md | `-` |
| `heygen-com/hyperframes` | `remotion-to-hyperframes` | **REJECT** | `-` | Remotion is foreign React runtime stack; outside BestFriend scope | `-` |
| `heygen-com/hyperframes` | `slideshow` | **MERGE** | `hyperframes` | Slide transition video workflow; documented in references/workflows.md | `-` |
| `heygen-com/hyperframes` | `talking-head-recut` | **MERGE** | `hyperframes` | Talking head recut workflow; documented in references/workflows.md | `-` |
| `heygen-com/hyperframes` | `.agents/skills/captions-overlay` | **MERGE** | `hyperframes` | Caption typography and positioning rules; merged into references/composition.md | `-` |
| `heygen-com/hyperframes` | `.agents/skills/changelog-video` | **DEFER** | `-` | Changelog video pipeline coupled to proprietary HeyGen assets and voices | `-` |
| `heygen-com/hyperframes` | `.agents/skills/cut-the-curve` | **MERGE** | `emil-design-eng` | Easing curves already live in emil-design-eng; one handoff sentence, no twin skill | `3a` |
| `heygen-com/hyperframes` | `.agents/skills/motion-doctrine` | **MERGE** | `emil-design-eng` | Seam-gate motion doctrine overlaps emil-design-eng; handoff only | `3a` |
| `heygen-com/hyperframes` | `.agents/skills/oversized-cursor` | **MERGE** | `emil-design-eng` | Pointer chrome overlaps emil-design-eng; handoff only | `3a` |
| `heygen-com/hyperframes` | `.agents/skills/seam-craft` | **MERGE** | `emil-design-eng` | Transition seams overlap emil-design-eng; handoff only | `3a` |
| `Imbad0202/academic-research-skills` | `academic-paper` | **MERGE** | `academic` | Manuscript drafting methodology synthesized in first-party skills/academic/references/write.md; zero CC-BY-NC text copied | `-` |
| `Imbad0202/academic-research-skills` | `academic-paper-reviewer` | **MERGE** | `academic` | Peer critique framework synthesized in first-party skills/academic/references/review.md; zero CC-BY-NC text copied | `-` |
| `Imbad0202/academic-research-skills` | `academic-pipeline` | **MERGE** | `academic` | End-to-end research synthesis pipeline merged into skills/academic/SKILL.md; zero CC-BY-NC text copied | `-` |
| `Imbad0202/academic-research-skills` | `deep-research` | **MERGE** | `research / academic` | Overlaps BestFriend research (web/repo) and academic (literature); reject CC-BY-NC text copy | `-` |
| `affaan-m/ECC` | `accessibility` | **MERGE** | `impeccable` | MERGE into impeccable accessibility reference | `-` |
| `affaan-m/ECC` | `agent-architecture-audit` | **NEW** | `agent-architecture-audit` | Diagnostic for 12-layer agent stack (wrapper regression, memory pollution, tool loops, context leakage); handoff security to full-audit-keamanan | `2a` |
| `affaan-m/ECC` | `agent-eval` | **MERGE** | `eval-harness` | MERGE into eval-harness | `-` |
| `affaan-m/ECC` | `agent-harness-construction` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `agent-introspection-debugging` | **MERGE** | `diagnosing-bugs` | MERGE into diagnosing-bugs | `-` |
| `affaan-m/ECC` | `agent-payment-x402` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `agent-self-evaluation` | **MERGE** | `eval-harness` | MERGE into eval-harness | `-` |
| `affaan-m/ECC` | `agent-sort` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `agentic-engineering` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `agentic-os` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `ai-first-engineering` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `ai-regression-testing` | **MERGE** | `eval-harness` | MERGE into eval-harness | `-` |
| `affaan-m/ECC` | `android-clean-architecture` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `angular-developer` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `api-connector-builder` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `api-design` | **NEW** | `api-design` | REST resource, status, pagination, error, and versioning design; not a Context7 clone | `3a` |
| `affaan-m/ECC` | `architecture-decision-records` | **MERGE** | `grill-with-docs` | MERGE into grill-with-docs / domain-modeling ADR generation | `-` |
| `affaan-m/ECC` | `article-writing` | **MERGE** | `humanizer` | MERGE into humanizer / technical-writing | `-` |
| `affaan-m/ECC` | `automation-audit-ops` | **NEW** | `automation-audit-ops` | Evidence-first live cron/CI/hook/MCP inventory with keep/merge/cut | `3a` |
| `affaan-m/ECC` | `autonomous-agent-harness` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `autonomous-loops` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `backend-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `benchmark-methodology` | **MERGE** | `eval-harness` | MERGE into eval-harness | `-` |
| `affaan-m/ECC` | `benchmark-optimization-loop` | **MERGE** | `eval-harness` | MERGE into eval-harness | `-` |
| `affaan-m/ECC` | `benchmark` | **MERGE** | `full-performance-audit` | MERGE into full-performance-audit / eval-harness | `-` |
| `affaan-m/ECC` | `blender-motion-state-inspection` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `blueprint` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `brand-discovery` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `brand-voice` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `browser-qa` | **MERGE** | `playwright-qa` | MERGE into playwright-qa exploratory browser adapter | `-` |
| `affaan-m/ECC` | `bun-runtime` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `canary-watch` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `carrier-relationship-management` | **REJECT** | `-` | Third-party vendor operations and niche business workflows; reject proprietary automation | `-` |
| `affaan-m/ECC` | `cisco-ios-patterns` | **REJECT** | `-` | Third-party vendor operations and niche business workflows; reject proprietary automation | `-` |
| `affaan-m/ECC` | `ck` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `claude-devfleet` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `click-path-audit` | **NEW** | `click-path-audit` | Handler vs shared-store sequential-undo audit; not playwright-qa | `3a` |
| `affaan-m/ECC` | `clickhouse-io` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `code-tour` | **NEW** | `code-tour` | CodeTour `.tour` walkthroughs with verified file anchors | `3a` |
| `affaan-m/ECC` | `codebase-onboarding` | **MERGE** | `codebase-memory` | MERGE into codebase-memory MCP | `-` |
| `affaan-m/ECC` | `codehealth-mcp` | **MERGE** | `codebase-memory` | MERGE into codebase-memory MCP | `-` |
| `affaan-m/ECC` | `coding-standards` | **MERGE** | `matt-code-review` | MERGE into matt-code-review / 02-engineering-principles | `-` |
| `affaan-m/ECC` | `competitive-platform-analysis` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `competitive-report-structure` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `compose-multiplatform-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `config-gc` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `configure-ecc` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `connections-optimizer` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `content-engine` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `content-hash-cache-pattern` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `context-budget` | **MERGE** | `cost-aware-llm-pipeline` | MERGE into cost-aware-llm-pipeline token management | `-` |
| `affaan-m/ECC` | `continuous-agent-loop` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `continuous-learning-v2` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `continuous-learning` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `contract-first` | **NEW** | `contract-first` | One canonical machine-checkable consumer/provider contract artifact | `3a` |
| `affaan-m/ECC` | `cost-aware-llm-pipeline` | **NEW** | `cost-aware-llm-pipeline` | Cost engineering patterns for LLM APIs (complexity routing, token budgeting, prompt caching, fallback tiers) | `2a` |
| `affaan-m/ECC` | `cost-tracking` | **MERGE** | `cost-aware-llm-pipeline` | MERGE into cost-aware-llm-pipeline | `-` |
| `affaan-m/ECC` | `council-multi-model` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `council` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `cpp-coding-standards` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `cpp-testing` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `crosspost` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `csharp-testing` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `customer-billing-ops` | **REJECT** | `-` | Third-party vendor operations and niche business workflows; reject proprietary automation | `-` |
| `affaan-m/ECC` | `customs-trade-compliance` | **REJECT** | `-` | Third-party vendor operations and niche business workflows; reject proprietary automation | `-` |
| `affaan-m/ECC` | `dart-flutter-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `dashboard-builder` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `data-scraper-agent` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `data-throughput-accelerator` | **MERGE** | `full-performance-audit` | MERGE into full-performance-audit | `-` |
| `affaan-m/ECC` | `database-migrations` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `deep-research` | **MERGE** | `research` | MERGE into research / academic | `-` |
| `affaan-m/ECC` | `defi-amm-security` | **REJECT** | `-` | Cryptocurrency / Web3 / automated trading specific domain; outside BestFriend core mission | `-` |
| `affaan-m/ECC` | `delivery-gate` | **MERGE** | `rules/01-verification.md` | Mechanical completion gates already live in verification profiles; no Claude Stop hook | `3a` |
| `affaan-m/ECC` | `deployment-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `design-system` | **MERGE** | `impeccable` | MERGE into impeccable design tokens | `-` |
| `affaan-m/ECC` | `dev-team` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `django-celery` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `django-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `django-security` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `django-tdd` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `django-verification` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `dmux-workflows` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `docker-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `documentation-lookup` | **MERGE** | `context7` | MERGE into context7 / grill-with-docs | `-` |
| `affaan-m/ECC` | `dotnet-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `dynamic-workflow-mode` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `e2e-testing` | **MERGE** | `playwright-qa` | MERGE into playwright-qa / project test suite | `-` |
| `affaan-m/ECC` | `ecc-guide` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `ecc-recipes` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `ecc-tools-cost-audit` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `email-ops` | **REJECT** | `-` | Third-party vendor operations and niche business workflows; reject proprietary automation | `-` |
| `affaan-m/ECC` | `energy-procurement` | **REJECT** | `-` | Third-party vendor operations and niche business workflows; reject proprietary automation | `-` |
| `affaan-m/ECC` | `enterprise-agent-ops` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `error-handling` | **MERGE** | `diagnosing-bugs` | MERGE into diagnosing-bugs / codebase-design | `-` |
| `affaan-m/ECC` | `eval-harness` | **NEW** | `eval-harness` | Evaluation framework for prompts, skills, and agents (eval-driven development, grading rubrics, pass@k, regression suites) | `2a` |
| `affaan-m/ECC` | `evm-token-decimals` | **REJECT** | `-` | Cryptocurrency / Web3 / automated trading specific domain; outside BestFriend core mission | `-` |
| `affaan-m/ECC` | `exa-search` | **REJECT** | `-` | Foreign search MCP / FOREIGN_ON_DEMAND | `-` |
| `affaan-m/ECC` | `fal-ai-media` | **REJECT** | `-` | Third-party vendor operations and niche business workflows; reject proprietary automation | `-` |
| `affaan-m/ECC` | `fastapi-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `finance-billing-ops` | **REJECT** | `-` | Third-party vendor operations and niche business workflows; reject proprietary automation | `-` |
| `affaan-m/ECC` | `flox-environments` | **REJECT** | `-` | Third-party vendor operations and niche business workflows; reject proprietary automation | `-` |
| `affaan-m/ECC` | `flutter-dart-code-review` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `foundation-models-on-device` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `frontend-a11y` | **MERGE** | `impeccable` | MERGE into impeccable accessibility reference | `-` |
| `affaan-m/ECC` | `frontend-design-direction` | **MERGE** | `found-this-design` | MERGE into found-this-design / impeccable | `-` |
| `affaan-m/ECC` | `frontend-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `frontend-slides` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `fsharp-testing` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `gan-style-harness` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `gateguard` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `generating-python-installer` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `git-workflow` | **MERGE** | `gh-axi` | MERGE into gh-axi and repository git conventions | `-` |
| `affaan-m/ECC` | `github-ops` | **MERGE** | `gh-axi` | MERGE into gh-axi GitHub operations | `-` |
| `affaan-m/ECC` | `golang-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `golang-testing` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `google-workspace-ops` | **REJECT** | `-` | Third-party vendor operations and niche business workflows; reject proprietary automation | `-` |
| `affaan-m/ECC` | `growth-log` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `healthcare-cdss-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `healthcare-emr-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `healthcare-eval-harness` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `healthcare-phi-compliance` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `hermes-imports` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `hexagonal-architecture` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `hipaa-compliance` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `homelab-network-readiness` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `homelab-network-setup` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `homelab-pihole-dns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `homelab-vlan-segmentation` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `homelab-wireguard-vpn` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `hookify-rules` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `inherit-legacy-style` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `intent-driven-development` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `inventory-demand-planning` | **REJECT** | `-` | Third-party vendor operations and niche business workflows; reject proprietary automation | `-` |
| `affaan-m/ECC` | `investor-materials` | **REJECT** | `-` | Third-party vendor operations and niche business workflows; reject proprietary automation | `-` |
| `affaan-m/ECC` | `investor-outreach` | **REJECT** | `-` | Third-party vendor operations and niche business workflows; reject proprietary automation | `-` |
| `affaan-m/ECC` | `ios-icon-gen` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `iterative-retrieval` | **MERGE** | `research` | MERGE into research / CBM | `-` |
| `affaan-m/ECC` | `ito-baskets` | **REJECT** | `-` | Third-party vendor operations and niche business workflows; reject proprietary automation | `-` |
| `affaan-m/ECC` | `ito-compute` | **REJECT** | `-` | Third-party vendor operations and niche business workflows; reject proprietary automation | `-` |
| `affaan-m/ECC` | `ito-inference` | **REJECT** | `-` | Third-party vendor operations and niche business workflows; reject proprietary automation | `-` |
| `affaan-m/ECC` | `ito-training` | **REJECT** | `-` | Third-party vendor operations and niche business workflows; reject proprietary automation | `-` |
| `affaan-m/ECC` | `java-coding-standards` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `jira-integration` | **REJECT** | `-` | Third-party vendor operations and niche business workflows; reject proprietary automation | `-` |
| `affaan-m/ECC` | `jpa-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `knowledge-ops` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `kotlin-coroutines-flows` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `kotlin-exposed-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `kotlin-ktor-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `kotlin-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `kotlin-testing` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `kubernetes-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `laravel-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `laravel-plugin-discovery` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `laravel-security` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `laravel-tdd` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `laravel-verification` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `latency-critical-systems` | **MERGE** | `full-performance-audit` | MERGE into full-performance-audit | `-` |
| `affaan-m/ECC` | `lead-intelligence` | **REJECT** | `-` | Third-party vendor operations and niche business workflows; reject proprietary automation | `-` |
| `affaan-m/ECC` | `liquid-glass-design` | **MERGE** | `impeccable` | MERGE into impeccable UI styling | `-` |
| `affaan-m/ECC` | `living-docs-governance` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `llm-trading-agent-security` | **REJECT** | `-` | Cryptocurrency / Web3 / automated trading specific domain; outside BestFriend core mission | `-` |
| `affaan-m/ECC` | `logistics-exception-management` | **REJECT** | `-` | Third-party vendor operations and niche business workflows; reject proprietary automation | `-` |
| `affaan-m/ECC` | `loop-design-check` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `mailtrap-email-integration` | **REJECT** | `-` | Third-party vendor operations and niche business workflows; reject proprietary automation | `-` |
| `affaan-m/ECC` | `make-interfaces-feel-better` | **MERGE** | `emil-design-eng` | MERGE into emil-design-eng | `-` |
| `affaan-m/ECC` | `manim-video` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `market-research` | **MERGE** | `research` | MERGE into research specialist | `-` |
| `affaan-m/ECC` | `marketing-campaign` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `mcp-server-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `messages-ops` | **REJECT** | `-` | Third-party vendor operations and niche business workflows; reject proprietary automation | `-` |
| `affaan-m/ECC` | `ml-adoption-playbook` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `mle-workflow` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `motion-advanced` | **MERGE** | `emil-design-eng` | MERGE into emil-design-eng / scroll-craft | `-` |
| `affaan-m/ECC` | `motion-foundations` | **MERGE** | `emil-design-eng` | MERGE into emil-design-eng | `-` |
| `affaan-m/ECC` | `motion-patterns` | **MERGE** | `emil-design-eng` | MERGE into emil-design-eng | `-` |
| `affaan-m/ECC` | `motion-ui` | **MERGE** | `emil-design-eng` | MERGE into emil-design-eng | `-` |
| `affaan-m/ECC` | `mysql-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `nanoclaw-repl` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `nasiko-control-plane` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `nestjs-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `netmiko-ssh-automation` | **REJECT** | `-` | Third-party vendor operations and niche business workflows; reject proprietary automation | `-` |
| `affaan-m/ECC` | `network-bgp-diagnostics` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `network-config-validation` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `network-interface-health` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `nextjs-turbopack` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `nodejs-keccak256` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `nutrient-document-processing` | **REJECT** | `-` | Third-party vendor operations and niche business workflows; reject proprietary automation | `-` |
| `affaan-m/ECC` | `nuxt4-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `openclaw-persona-forge` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `opensource-pipeline` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `orch-add-feature` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `orch-build-mvp` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `orch-change-feature` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `orch-fix-defect` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `orch-pipeline` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `orch-refine-code` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `parallel-execution-optimizer` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `perl-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `perl-security` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `perl-testing` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `plan-canvas` | **MERGE** | `ask-matt` | MERGE into plan agent | `-` |
| `affaan-m/ECC` | `plan-orchestrate` | **MERGE** | `ask-matt` | MERGE into plan agent and ask-matt workflow | `-` |
| `affaan-m/ECC` | `plankton-code-quality` | **MERGE** | `matt-code-review` | MERGE into matt-code-review | `-` |
| `affaan-m/ECC` | `postgres-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `prediction-market-oracle-research` | **REJECT** | `-` | Cryptocurrency / Web3 / automated trading specific domain; outside BestFriend core mission | `-` |
| `affaan-m/ECC` | `prediction-market-risk-review` | **REJECT** | `-` | Cryptocurrency / Web3 / automated trading specific domain; outside BestFriend core mission | `-` |
| `affaan-m/ECC` | `prisma-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `product-capability` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `product-lens` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `production-audit` | **MERGE** | `full-audit-keamanan` | MERGE into full-audit-keamanan / performance-audit | `-` |
| `affaan-m/ECC` | `production-scheduling` | **REJECT** | `-` | Third-party vendor operations and niche business workflows; reject proprietary automation | `-` |
| `affaan-m/ECC` | `project-flow-ops` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `prompt-optimizer` | **NEW** | `prompt-optimizer` | Advisory prompt optimizer for structural clarity and boundary constraints; does not auto-mutate installed skills | `2a` |
| `affaan-m/ECC` | `python-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `python-testing` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `pytorch-patterns` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `quality-nonconformance` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `quarkus-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `quarkus-security` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `quarkus-tdd` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `quarkus-verification` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `ralphinho-rfc-pipeline` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `react-native-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `react-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `react-performance` | **MERGE** | `full-performance-audit` | MERGE into full-performance-audit | `-` |
| `affaan-m/ECC` | `react-testing` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `recsys-pipeline-architect` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `recursive-decision-ledger` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `redis-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `regex-vs-llm-structured-text` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `remotion-video-creation` | **MERGE** | `hyperframes` | MERGE into hyperframes / visual-studio | `-` |
| `affaan-m/ECC` | `repo-scan` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `research-ops` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `returns-reverse-logistics` | **REJECT** | `-` | Third-party vendor operations and niche business workflows; reject proprietary automation | `-` |
| `affaan-m/ECC` | `rules-distill` | **MERGE** | `writing-for-agents` | MERGE into writing-for-agents rule authoring | `-` |
| `affaan-m/ECC` | `rust-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `rust-testing` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `safety-guard` | **MERGE** | `full-audit-keamanan` | MERGE into full-audit-keamanan | `-` |
| `affaan-m/ECC` | `santa-method` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `scientific-db-pubmed-database` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `scientific-db-uspto-database` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `scientific-pkg-gget` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `scientific-thinking-literature-review` | **MERGE** | `academic` | MERGE into academic literature survey | `-` |
| `affaan-m/ECC` | `scientific-thinking-scholar-evaluation` | **MERGE** | `academic` | MERGE into academic peer review | `-` |
| `affaan-m/ECC` | `search-first` | **MERGE** | `research` | MERGE into research / CBM repo evidence | `-` |
| `affaan-m/ECC` | `security-bounty-hunter` | **MERGE** | `full-audit-keamanan` | MERGE into full-audit-keamanan | `-` |
| `affaan-m/ECC` | `security-review` | **MERGE** | `full-audit-keamanan` | MERGE into full-audit-keamanan defensive security | `-` |
| `affaan-m/ECC` | `security-scan` | **MERGE** | `full-audit-keamanan` | MERGE into full-audit-keamanan defensive security | `-` |
| `affaan-m/ECC` | `seo` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `skill-comply` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `skill-scout` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `skill-stocktake` | **NEW** | `skill-stocktake` | Hygiene and quality audit for BestFriend skills catalog (frontmatter schema, boundaries, trigger specificity, dead links) | `2a` |
| `affaan-m/ECC` | `social-graph-ranker` | **REJECT** | `-` | Third-party vendor operations and niche business workflows; reject proprietary automation | `-` |
| `affaan-m/ECC` | `social-publisher` | **REJECT** | `-` | Third-party vendor operations and niche business workflows; reject proprietary automation | `-` |
| `affaan-m/ECC` | `springboot-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `springboot-security` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `springboot-tdd` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `springboot-verification` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `strategic-compact` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `swift-actor-persistence` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `swift-concurrency-6-2` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `swift-protocol-di-testing` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `swiftui-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `taste` | **MERGE** | `impeccable` | MERGE into impeccable taste-guard reference | `-` |
| `affaan-m/ECC` | `tasteforge-video` | **MERGE** | `hyperframes` | MERGE into hyperframes / visual-studio | `-` |
| `affaan-m/ECC` | `tdd-workflow` | **MERGE** | `tdd` | MERGE into tdd specialist | `-` |
| `affaan-m/ECC` | `team-agent-orchestration` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `team-builder` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `terminal-opener` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `terminal-ops` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `tinystruct-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `token-budget-advisor` | **MERGE** | `cost-aware-llm-pipeline` | MERGE into cost-aware-llm-pipeline | `-` |
| `affaan-m/ECC` | `ui-demo` | **MERGE** | `prototype` | MERGE into prototype / impeccable | `-` |
| `affaan-m/ECC` | `ui-to-vue` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `uncloud` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `unified-memory` | **REJECT** | `-` | Harness control plane / autonomous loop / host adapter runtime; reject vendor runtime | `-` |
| `affaan-m/ECC` | `unified-notifications-ops` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `verification-loop` | **MERGE** | `rules/01-verification.md` | MERGE into rules/01-verification.md standard verification profiles | `-` |
| `affaan-m/ECC` | `video-editing` | **MERGE** | `hyperframes` | MERGE into hyperframes / visual-studio | `-` |
| `affaan-m/ECC` | `videodb` | **REJECT** | `-` | Third-party vendor operations and niche business workflows; reject proprietary automation | `-` |
| `affaan-m/ECC` | `visa-doc-translate` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `vite-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `vue-patterns` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `windows-desktop-e2e` | **REJECT** | `-` | Language/framework pattern sprawl already covered by repo context + Context7 docs | `-` |
| `affaan-m/ECC` | `workspace-surface-audit` | **DEFER** | `-` | Specialized domain procedure deferred for future warehouse wave evaluation | `-` |
| `affaan-m/ECC` | `x-api` | **REJECT** | `-` | Third-party vendor operations and niche business workflows; reject proprietary automation | `-` |
