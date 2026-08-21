# Troubleshooting

`OPENCODE_MISSING` — install OpenCode 1.18.x and put `opencode` on PATH.

`UNSUPPORTED_OPENCODE_VERSION` — this release supports 1.18.x (`mcp.<name>`).

`CODEBASE_MEMORY_CHECKSUM_FAILED` — delete `~/.local/share/opencode-bestfriend/cache/downloads/` and retry. Do not ignore a mismatch.

`DESIGN_BANK_CORRUPT_OR_MISSING` — set `OPENCODE_DESIGN_BANK` to a tree with both catalogs, or omit `--skip-design-bank` so the installer can download.

`FOREIGN skill collision` — an unowned skill already occupies that name. Move or rename it.

`STALE_TRANSACTION` — `./install.sh --recover`

Doctor `OPTIONAL_ABSENT` is not a core failure.

Restart OpenCode after install.
