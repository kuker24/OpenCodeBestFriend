# Acceptance

A successful 1.0.0 install should report approximately:

```text
PASS OpenCode
PASS opencode.jsonc
PASS AGENTS.md
PASS skills TOTAL 40/40 MODEL 24/24 MANUAL 16/16
PASS rules 6 portable; 04-context-guard EXCLUDED_BY_DESIGN
CONFIGURED mcp:codebase-memory-mcp
CONFIGURED mcp:context7
CONFIGURED mcp:shadcn
OPTIONAL_ABSENT mcp:serena
OPTIONAL_ABSENT mcp:exa
PASS Codebase Memory
PASS Design Bank / Refero / Motionsites   (or DEGRADED_DESIGN_BANK if skipped)
PASS DI policy / taxonomy / CLI / runtime
PASS OPENCODE_DISABLE_CLAUDE_CODE
PASS ~/.claude mutations 0
PASS Active Claude dependencies 0
PASS Context Guard NOT_PORTED_BY_DESIGN
PASS ownership manifest
```

Public CI uses a tiny Design Bank fixture and a mock Codebase Memory binary. Live archive download is a manual acceptance test.
