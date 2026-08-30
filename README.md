# OpenCodeBestFriend

Production-ready capability layer for OpenCode:
40 routed skills, MCP, Codebase Memory,
Design Bank, Design Intelligence, browser and verification tooling.

OpenCodeBestFriend is an installer and runtime overlay for [OpenCode](https://opencode.ai). It is **not** Claude Code, **not** a model provider, and **not** a dump of a developer home directory.

## What it is

- 40 skills: 24 model-invoked, 16 manual slash commands
- A thin `AGENTS.md` router (lazy, one primary specialist)
- Core MCP: Codebase Memory, Context7, shadcn
- Design Bank discovery or download (media is **not** in git)
- Design Intelligence (lazy, inside Impeccable)
- `opencode-bf doctor`, transactional install, uninstall, restore
- Claude Code isolation: `OPENCODE_DISABLE_CLAUDE_CODE=1`

## What it is not

- Not Claude Code configuration
- Not Context Guard / Claude hooks / Claude autocompact
- Not your provider keys, models, or auth state
- Not a Design Bank media repository
- Not claimed as macOS/Windows-tested (Linux x86_64 only for this release)

## Quickstart

```bash
git clone https://github.com/kuker24/OpenCodeBestFriend.git
cd OpenCodeBestFriend

./install.sh --dry-run
./install.sh

# optional: acquire the full user-owned Design Bank and build DesignV2
./install.sh --with-design-bank

# pick up OPENCODE_DISABLE_CLAUDE_CODE=1
exec "$SHELL"
# or: source ~/.bashrc   (bash)
# or: source ~/.zshrc    (zsh)

opencode-bf verify
opencode-bf doctor
opencode-bf doctor --deep
opencode
```

Restart OpenCode after install. Config is not hot-reloaded.

## Architecture

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
      │  ├─ 21st
      │  ├─ Aura
      │  ├─ Refero
      │  └─ Motionsites
      ├─ Design Intelligence
      └─ Design V2 (offline user bank, ~/DesignV2)
```

Availability is not a reason to activate a tool. One primary specialist. At most one risk specialist.

## Skill routing

Default: repository evidence first. Then at most one specialist.

| Intent | Route |
| --- | --- |
| Repo understanding | Codebase Memory MCP |
| Hard unknown bug | `diagnosing-bugs` |
| Security-sensitive work | `full-audit-keamanan` |
| Measured performance regression | `full-performance-audit` |
| Current library docs | Context7 |
| UI registry | shadcn MCP |
| Visual direction | `found-this-design` |
| UI implementation after a direction | `impeccable` |
| Motion | `emil-design-eng` |
| Photoreal / media | `visual-studio` |
| Scroll-driven 3D | `scroll-world` |
| Architecture bake-off | `/architect` (manual) |
| Repo rationale | `/why` (manual) |

Manual skills are OpenCode commands. They are not auto-discovered.

When an agent names tools, it should report `USED` / `CONSIDERED_NOT_USED` / `MANUAL_NOT_INVOKED`.

## MCP

Core (installed):

- `codebase-memory-mcp` — downloaded, SHA-256 verified, Linux x86_64
- `context7` — `https://mcp.context7.com/mcp` (no secret stored)
- `shadcn` — `npx -y shadcn@4.18.0 mcp`

Optional:

- `serena` — host binary may exist; MCP is **not** registered unless you run `opencode-bf serena enable`
- `exa` — `FOREIGN_ON_DEMAND`; installer never adds, removes, or overwrites it

The installer merges only owned MCP keys. Provider, model, permissions, plugins, and foreign MCP stay yours.

## Design Bank

Design Bank content is **not** vendored in this repository. Redistribution of the media archive is not cleared as first-party content.

Normal `./install.sh` installs the engine only and never starts the multi-gigabyte download. Full setup is explicit:

```bash
./install.sh --with-design-bank
# or after installation
opencode-bf design bootstrap
```

Bootstrap resolves `OPENCODE_DESIGN_BANK` → existing pointer → deprecated `GROK_DESIGN_BANK` → `~/Design`. It downloads the declared public artifact with curl, verifies SHA-256, safely extracts into a temporary directory, validates all four catalogs, and commits the bank without merging into an existing directory. `~/Design` and `~/DesignV2` are user data and uninstall never removes them. Google Drive is contacted only by bootstrap; retrieval remains offline.

## Design Intelligence

Portable policy, taxonomy, schemas, and Python runtime ship in git. The installer copies them into OpenCode-owned paths. Retrieval stays lazy inside Impeccable `new-work`.

## Design V2

Offline user-data bank at `OPENCODE_DESIGN_V2` or `~/DesignV2` (`GROK_DESIGN_V2` is a deprecated alias). Not installer-owned. Uninstall does not touch it.

```bash
opencode-bf design import ~/Downloads/aura-export --provider aura
opencode-bf design sources
opencode-bf design ingest --provider aura --source-id <source_id>
opencode-bf design dedupe
opencode-bf design rebuild
opencode-bf design doctor
opencode-bf design search "premium cybersecurity dashboard dark minimal"
opencode-bf design shortlist --query "premium cybersecurity dashboard dark minimal"
opencode-bf design inspect <id>
```

`import` accepts local files, folders, or ZIPs only and returns a stable staged `source_id`. A direct `ingest --provider <provider> <local-path>` remains available as a one-step shortcut. URLs are rejected and no command fetches Aura or 21st content.

Search, inspect, doctor, sources, and shortlist are read-only and do not create the bank. JSONL is canonical; missing or stale FTS is `DEGRADED_FTS`. Run `opencode-bf design --help` for the complete local lifecycle.

## Claude isolation

OpenCodeBestFriend does not write `~/.claude/`, does not run `claude`, and does not import Claude hooks or Context Guard.

```text
Context Guard: NOT_PORTED_BY_DESIGN
OpenCode autocompact: NATIVE
```

## Installer

User-local, no sudo:

```text
~/.config/opencode/
~/.local/share/opencode-bestfriend/
~/.local/bin/
```

Transactional states: `PREPARING` → `STAGED` → `VALIDATED` → `BACKED_UP` → `APPLIED` → `VERIFIED` → `COMMITTED`.

Backup `preInstall` records whether config, `AGENTS.md`, commands, helpers, shell rc, and share trees existed. Recover restores present files and **deletes** installer-created files that were previously absent.

`AGENTS.md` is marker-merged (`<!-- OPENCODEBESTFRIEND:BEGIN -->` … `END`). Foreign text outside the markers is preserved. Foreign `commands/<name>.md` and foreign `~/.local/bin/opencode-bf` / `opencode-chromium-cdp` fail closed instead of being overwritten.

Upgrade recover restores prior `~/.local/share/opencode-bestfriend/product` and `components` when those trees existed before apply.

Collision preflight (foreign skills/commands/helpers, parseable config, writable targets) runs before backup and apply. `opencode-bf serena enable` does not strip JSONC comments.

Official OpenCode gate is **1.18.x** (not 1.19+). JSONC comments are preserved when MCP keys can be patched surgically.

```bash
./install.sh --dry-run
./install.sh --recover
opencode-bf uninstall
opencode-bf restore --list
opencode-bf verify
opencode-bf doctor
opencode-bf doctor --deep
opencode-bf doctor --strict
```

`verify` checks owned files are canonical. `doctor` checks install/config health (MCP `CONFIGURED` is not live). `doctor --deep` requires core MCP `CONNECTED`. `doctor --strict` fails on `DEGRADED`/`WARN`. ClaudeBestFriend 1.4.2 overlays are migrated on install (foreign MCP/provider kept).

Update:

```bash
git pull
./install.sh
```

## Compatibility

Officially tested:

- Linux x86_64
- OpenCode stable 1.18.x
- Python 3, Node + npx, git, curl, tar

Optional host tools: Chromium, `gh`, browser-act, serena, semgrep, osv-scanner, gitleaks.

## Security model

- Fail-closed checksums for Codebase Memory and Design Bank downloads
- No API keys, tokens, or provider maps in git
- Ownership manifest: only claimed files are uninstalled
- Optional scanners are detected, never bundled

See [docs/security.md](docs/security.md).

## Provenance

Adapted from [ClaudeBestFriend](https://github.com/kuker24/ClaudeBestFriend) `1.4.2-claude.1` (`05e6fdc`), itself adapted from GrokBestFriend. Adapted ≠ first-party. Licenses: [LICENSE](LICENSE), [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## License

MIT for first-party installer, docs, overlays, and tests. Vendored skills keep their upstream licenses.
