# Acceptance

`verify` = are installed owned files canonical?
`doctor` = is installation/config healthy?
`doctor --deep` = is live runtime proven?
`doctor --strict` = treat DEGRADED/WARN as failure.

A successful 1.6.2 install should report approximately:

```text
PASS INSTALLED_PRODUCT opencode-bestfriend
PASS INSTALLED_VERSION 1.6.2
PASS SOURCE_REPOSITORY https://github.com/kuker24/OpenCodeBestFriend

PASS OpenCode
PASS opencode.jsonc parseable
PASS AGENTS.md thin owned-lines=…
PASS skills TOTAL 43/43 MODEL 27/27 MANUAL 16/16
PASS rules 6 portable; 04-context-guard EXCLUDED_BY_DESIGN

CONFIGURED mcp:codebase-memory-mcp
CONFIGURED mcp:context7
CONFIGURED mcp:shadcn
OPTIONAL_ABSENT mcp:serena
OPTIONAL_ABSENT mcp:exa

PASS codebase-memory bin
PASS Design Bank / 21st / Aura / Refero / Motionsites   (when bootstrapped; or DEGRADED Design Bank)
EMPTY Design V2 absent   (or PASS catalog / DEGRADED_FTS)
PASS DI policy / taxonomy / CLI / runtime
PASS OPENCODE_DISABLE_CLAUDE_CODE
PASS ~/.claude mutations 0
PASS Active Claude dependencies 0
NOT_APPLICABLE Context Guard NOT_PORTED_BY_DESIGN
PASS OpenCode context engine NATIVE_UNCHANGED
PASS ownership manifest
```

Deep acceptance additionally requires:

```text
PASS mcp:codebase-memory-mcp CONNECTED
PASS mcp:context7 CONNECTED
PASS mcp:shadcn CONNECTED
```

CBM current project not indexed is `DEGRADED CBM project CURRENT_REPO_NOT_INDEXED`, never a fake PASS.
Chromium stopped or port occupied is `DEGRADED`, not core FAIL unless `--strict`.

Public CI uses a tiny Design Bank fixture and a mock Codebase Memory binary. Live archive download is a manual acceptance test.
