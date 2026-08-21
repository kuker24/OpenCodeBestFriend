# Security

- No secrets in the repository
- Checksums fail closed for Codebase Memory and Design Bank archives
- Installer does not read or write `~/.claude/`
- Uninstall uses the ownership manifest; foreign config is preserved
- Optional scanners are detected, not bundled
- Model/provider names are opaque; do not print tokens or gateway maps
- `vendor/license-audit.json` lists every skill license **as evidenced**. `not-stated-in-frontmatter` is not a grant.

Pre-push (maintainer): gitleaks, absolute personal-home path scan, active Claude-runtime scan.
