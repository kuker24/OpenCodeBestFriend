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
- Installed `product/lib/design_v2/**` Python and JSON files are covered by `opencode-bf verify`.
- SmartDoc treats document text as data. DOCX read uses stdlib zip/XML with traversal, size, ratio, symlink, and DTD rejection. Persistent writes stay under the resolved SmartDoc root (`OPENCODE_SMARTDOC` or `~/SmartDoc`), mode 0700/0600. Uninstall leaves that tree. Local Similarity Audit names its corpus and is not Turnitin.
- Design V2 import rejects common API tokens, private-key headers, credential-bearing database URLs, unsafe links, traversal, and oversized input; normalized assets replace rather than merge prior destinations.
- Design V2 doctor checks catalog JSONL and SQLite hashes against the canonical lock.
- Model/provider names are opaque; do not print tokens or gateway maps
- `vendor/license-audit.json` lists every skill license **as evidenced**. `not-stated-in-frontmatter` is not a grant. Nine snapshot skills remain unknown.

CI: unittest matrix (3.10–3.13), shellcheck, gitleaks, semgrep (`.semgrep.yml`). OSV Scanner is `NOT_CONFIGURED` — this tree has no language lockfile. Release tarball/SBOM via `scripts/make-release-artifacts.sh` (no GitHub attestation wired).

Pre-push (maintainer): gitleaks, absolute personal-home path scan, active Claude-runtime scan.
