# MCP

OpenCode 1.18.x schema: `mcp.<name>` (not v2 `mcp.servers`). Unknown majors fail closed.

Owned:

| Name | Type | Pin |
| --- | --- | --- |
| codebase-memory-mcp | local stdio | 0.9.0 SHA-256 verified |
| context7 | remote HTTP | https://mcp.context7.com/mcp |
| shadcn | local stdio | `npx -y shadcn@4.18.0 mcp` |

Optional:

- `serena` — `opencode-bf serena enable` if the binary is on PATH
- `stitch` — `opencode-bf stitch enable` (remote comp/mock source only; auth via `{env:STITCH_API_KEY}` or `--oauth`)
- `reticle` — `opencode-bf reticle enable` (local stdio via `npx -y @reticlehq/server mcp`; perception only, never auto-implementer)
- `ui-skills` — `opencode-bf ui-skills enable` (remote HTTP `https://www.ui-skills.com/mcp`; design-skill lookup only)
- `exa` — foreign; never add/remove/overwrite

Merge is parse-aware. Comment-free JSON is rewritten with `json.dumps`. JSONC with comments is patched surgically (owned MCP keys only). If surgical merge cannot be verified, install fails closed instead of destroying comments.

Doctor reports `CONFIGURED` for owned MCP entries present in config. That is not a live connection. `opencode-bf doctor --deep` probes `opencode mcp list` per server/per line and **exits 1** unless every core server is `CONNECTED`. `DISCONNECTED`, `NOT_CHECKED`, `LISTED`, empty output, and command failure are not healthy. The substring `connected` inside `disconnected` is not treated as connected. ANSI codes are stripped before parse.

`opencode-bf serena enable` adds Serena only if absent. JSONC comments, provider keys, and foreign MCP are preserved via the same surgical merge as core MCP. Invalid config fails closed.

`opencode-bf stitch enable` configures Google Stitch as an optional remote comp/mock server (`https://stitch.googleapis.com/mcp`). It is not an owned core server and not a UI implementer. Keys are never written directly to config, only referenced via `{env:STITCH_API_KEY}` or omitted when using `--oauth`. `opencode-bf stitch disable` surgically removes only the stitch server key.

`opencode-bf reticle enable` configures Reticle as an optional local perception MCP server (`npx -y @reticlehq/server mcp`). It is `FOREIGN_ON_DEMAND`. The server package is FSL-1.1-ALv2 (competing-use clause); SDK packages (Apache-2.0) are not vendored. Reticle is never an auto-implementer; after a feature is done, default verification remains `playwright-qa` or `chrome-devtools-axi`. Reticle is extra perception if the user enabled it. `opencode-bf reticle disable` surgically removes only the reticle server key. Absent is not a doctor failure; a malformed entry fails closed.

`opencode-bf ui-skills enable` configures UI Skills as an optional remote MCP server (`https://www.ui-skills.com/mcp`). It is `FOREIGN_ON_DEMAND` for design-skill lookup only (`list_skills`, `get_skill`). Product UI remains Design Bank + Impeccable + Design V2 atoms + shadcn; `BANK_MISS` never generates from a random ui-skills document. `opencode-bf ui-skills disable` surgically removes only the ui-skills server key. Absent is not a doctor failure; a malformed entry fails closed.
