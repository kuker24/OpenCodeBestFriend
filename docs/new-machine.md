# New machine

1. Install OpenCode 1.18.x, Python 3, Node + npx, git, curl, tar.
2. Clone this repository.
3. `./install.sh --dry-run` then `./install.sh` for the lightweight engine.
4. Optionally run `./install.sh --with-design-bank` instead, or later run `opencode-bf design bootstrap`, to acquire the full user-owned bank and build DesignV2.
5. `exec "$SHELL"` or source your rc file.
6. `opencode-bf verify`
7. `opencode-bf doctor --deep`
8. Restart OpenCode.

If a previous ClaudeBestFriend overlay is present, `./install.sh` prints `MIGRATION_DETECTED` and replaces owned files only.

Optional: Chromium for CDP, `gh auth login`, browser-act, serena.

Do not copy `~/.config/opencode` from another machine as the install method.
