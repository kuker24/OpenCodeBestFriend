# Architecture

```text
                         OpenCode
                            │
                       AGENTS.md
                            │
                     Thin Lazy Router
                            │
        ┌───────────────────┼────────────────────┐
        ▼                   ▼                    ▼
      Skills               MCP                 Rules
   24 automatic       Codebase Memory        Verification
   16 manual          Context7              Engineering
                      shadcn
        │
        ▼
     Design
     ├─ Design Bank
     │  ├─ Refero
     │  └─ Motionsites
     └─ Design Intelligence
```

Runtime destinations (user-local):

- Model skills → `~/.config/opencode/skills/<name>/`
- Manual skills → `~/.config/opencode/bestfriend/skills/<name>/`
- Commands → `~/.config/opencode/commands/<name>.md`
- Rules → `~/.config/opencode/bestfriend/rules/`
- Ownership → `~/.config/opencode/bestfriend/manifests/ownership.json`

OpenCode native context engine and autocompact are unchanged. Context Guard is not ported.
