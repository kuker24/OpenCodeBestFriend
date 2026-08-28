# Security

- No secrets in the repository
- Checksums fail closed for Codebase Memory and Design Bank archives
- Archive extract rejects `..`, absolute paths, Windows-style paths, and outbound symlink/hardlink (`filter="data"` on Python 3.12+)
- Foreign helpers at `~/.local/bin/opencode-bf` and `opencode-chromium-cdp` fail closed; ClaudeBestFriend installer helpers are treated as legacy-owned and replaced on migrate
- Restore stamps must match `[A-Za-z0-9][A-Za-z0-9._-]{0,63}`; `../` fails closed
- Uninstall ignores skill names that are not `^[a-z0-9]+(-[a-z0-9]+)*$` and never deletes arbitrary `ownedFiles` paths
- Installer does not read or write `~/.claude/` except a hash snapshot used for integrity compare
- Uninstall uses the ownership manifest; foreign config is preserved
- Wildcard `"permission": { "*": "allow" }` is reported as `DEGRADED_SECURITY`; installer never mutates permission
- `opencode-bf security-profile` prints a recommendation only
- Optional scanners are detected, not bundled
- Model/provider names are opaque; do not print tokens or gateway maps
- `vendor/license-audit.json` lists every skill license **as evidenced**. `not-stated-in-frontmatter` is not a grant. Nine snapshot skills remain unknown.

CI: unittest matrix (3.10–3.13), shellcheck, gitleaks, semgrep (`.semgrep.yml`). OSV Scanner is `NOT_CONFIGURED` — this tree has no language lockfile. Release tarball/SBOM via `scripts/make-release-artifacts.sh` (no GitHub attestation wired).

Pre-push (maintainer): gitleaks, absolute personal-home path scan, active Claude-runtime scan.
