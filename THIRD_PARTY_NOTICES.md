# OpenCodeBestFriend third-party notices

Adapted from ClaudeBestFriend / GrokBestFriend. Adapted ≠ first-party. This OpenCode port does not include Context Guard, Claude hooks, or Claude runtime config.

First-party installer, docs, overlays, and tests are MIT (see `LICENSE`).

This product vendors OpenCode-adapted skills and Design Intelligence runtime, originally snapshotted through GrokBestFriend 1.3.1 and ClaudeBestFriend 1.4.2-claude.1 (`05e6fdc`).

Selected skills also come from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT © 2026 Matt Pocock) and [cursor/plugins](https://github.com/cursor/plugins) `pstack/` (`60c641e`, MIT © 2026 Lauren Tan). Full plugins are not installed.

Licenses below are taken from vendored frontmatter or an obvious upstream statement. If a skill has no license in tree, this file says so. **That is not a grant.**

Machine-readable copy: `vendor/license-audit.json`.

| Component | Upstream | License in this tree | Redistribution |
| --- | --- | --- | --- |
| `adhd` | vendored frontmatter | MIT | follow MIT |
| `impeccable` | vendored frontmatter | Apache-2.0 | follow Apache-2.0 |
| Matt Pocock selected skills (`diagnosing-bugs`, `domain-modeling`, `codebase-design`, `writing-for-agents`, `research`, `prototype`, `grilling`, `improve-codebase-architecture`, `wizard`, `wait-what`, `ask-matt`, `grill-with-docs`, `to-spec`, `to-tickets`, `tdd`, `matt-code-review` ← `code-review`, `matt-implement` ← `implement`) | mattpocock/skills MIT LICENSE — `vendor/licenses/MATT-POCOCK-MIT.txt` | MIT | follow MIT |
| Pstack selected skills (`blast-radius`, `unslop`, `create-verification-skill`, `maintain-verification-skill`, `technical-writing`, `arena`, `interrogate`, `architect`, `decision-log`, `why`, `reflect`, `figure-it-out`) | cursor/plugins pstack `60c641e` | MIT — `vendor/licenses/PSTACK-MIT.txt` | follow MIT |
| Remaining skills (`browser-act`, `chrome-devtools-axi`, `emil-design-eng`, `found-this-design`, `full-audit-keamanan`, `full-performance-audit`, `gh-axi`, `scroll-world`, `visual-studio`) | GrokBestFriend 1.3.1 snapshot; no license in SKILL.md frontmatter | **not stated** | **unknown** — not a grant |
| Design bank (`Design-bank.tgz`) | GrokBestFriend v1.0.0 release asset | **not cleared** | not in git; installer may download the existing asset |
| Codebase Memory, serena, browser-act CLI, semgrep, gitleaks, osv-scanner | `vendor/sources.json` | upstream | follow upstream |

See `vendor/provenance.json` and `vendor/sources.json` for pins.
