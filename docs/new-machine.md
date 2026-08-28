# New machine

1. Install OpenCode 1.18.x, Python 3, Node + npx, git, curl, tar.
2. Clone this repository.
3. `./install.sh --dry-run` then `./install.sh`.
4. `exec "$SHELL"` or source your rc file.
5. `opencode-bf verify`
6. `opencode-bf doctor --deep`
7. Restart OpenCode.

If a previous ClaudeBestFriend overlay is present, `./install.sh` prints `MIGRATION_DETECTED` and replaces owned files only.

Optional: Chromium for CDP, `gh auth login`, browser-act, serena.

Do not copy `~/.config/opencode` from another machine as the install method.
