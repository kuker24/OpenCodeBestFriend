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

Merge is parse-aware (JSON or JSONC comments stripped on parse). Provider, model, `small_model`, compaction, permissions, plugins, and foreign MCP keys are preserved.
