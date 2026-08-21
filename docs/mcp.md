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
- `exa` — foreign; never add/remove/overwrite

Merge is parse-aware. Comment-free JSON is rewritten with `json.dumps`. JSONC with comments is patched surgically (owned MCP keys only). If surgical merge cannot be verified, install fails closed instead of destroying comments.

Doctor reports `CONFIGURED` for owned MCP entries present in config. That is not a live connection. `opencode-bf doctor --deep` may probe `opencode mcp list` per server/per line and report `CONNECTED` / `DISCONNECTED` / `LISTED` / `NOT_CHECKED` / `SKIPPED_MOCK`. The substring `connected` inside `disconnected` is not treated as connected.

`opencode-bf serena enable` adds Serena only if absent. JSONC comments, provider keys, and foreign MCP are preserved via the same surgical merge as core MCP. Invalid config fails closed.
