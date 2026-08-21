# Changelog

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
