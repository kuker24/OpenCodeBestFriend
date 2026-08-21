# OpenCodeBestFriend third-party notices

Adapted from ClaudeBestFriend / GrokBestFriend. Adapted ≠ first-party. This OpenCode port does not include Context Guard, Claude hooks, or Claude runtime config.

# Third-party notices

This file covers **vendored** components. First-party installer, docs, overlays, and tests are MIT (see `LICENSE`).

This product vendors OpenCode-adapted skills and Design Intelligence runtime, originally snapshotted through GrokBestFriend 1.3.1 and ClaudeBestFriend 1.4.2-claude.1 (`05e6fdc`). Adapted ≠ first-party.

1.4 also vendors **selected** skills from [mattpocock/skills](https://github.com/mattpocock/skills) (`9c9f36ccd3995266cd675468af71639c8dde1ec5`, MIT © 2026 Matt Pocock) and [cursor/plugins](https://github.com/cursor/plugins) `pstack/` (`60c641e4fad674784b30abcf9f8915dea39df38d`, MIT © 2026 Lauren Tan). Adapted copies are not first-party. Full plugins are not installed.

Licenses below are taken from vendored frontmatter or an obvious upstream statement. If a skill has no license in tree, this file says so. That is not a grant.

| Component | Upstream | License in this tree | Modified | Redistribution |
| --- | --- | --- | --- | --- |
| `skills/` or `manual-skills/` (adhd` | vendored skill frontmatter | MIT | yes (OpenCode overlay/routing) | follow MIT |
| `skills/` or `manual-skills/` (impeccable` | vendored skill frontmatter | Apache-2.0 | yes (OpenCode overlay/routing) | follow Apache-2.0 |
| Other `skills/` or `manual-skills/` (*` | see each `SKILL.md` | **not stated** in vendored frontmatter | yes | unknown — see upstream |
| Design bank (`Design-bank.tgz` Release asset) | Refero + Motionsites catalogs packed by GrokBestFriend | **not cleared** | packed | **unknown**. The installer downloads the existing GrokBestFriend v1.0.0 asset. It is not shipped in this git tree. |
| Codebase Memory, serena, browser-act, semgrep, gitleaks, osv-scanner, uv | see `vendor/sources.json` | their upstream licenses | no (downloaded at install) | follow upstream |
| Matt Pocock selected skills (`diagnosing-bugs`, `domain-modeling`, `codebase-design`, `writing-for-agents`, `research`, `prototype`, `grilling`, `improve-codebase-architecture`, `wizard`, `wait-what`) | [mattpocock/skills](https://github.com/mattpocock/skills) `9c9f36c` | MIT — `vendor/licenses/MATT-POCOCK-MIT.txt` | yes (OpenCode routing, no `openai.yaml`) | follow MIT |
| Pstack selected skills (`blast-radius`, `unslop`, `create-verification-skill`, `maintain-verification-skill`, `technical-writing`, `arena`, `interrogate`, `architect`, `decision-log` from `show-me-your-work`, `why`, `reflect`, `figure-it-out`) | [cursor/plugins](https://github.com/cursor/plugins) `pstack/` `60c641e` | MIT — `vendor/licenses/PSTACK-MIT.txt` | yes (OpenCode paths, no Cursor runtime) | follow MIT |

See `vendor/provenance.json` for the machine-readable copy. `vendor/UPSTREAM_GROK` records the GrokBestFriend commit this snapshot came from. `vendor/sources.json` records the Matt and Pstack pins.
