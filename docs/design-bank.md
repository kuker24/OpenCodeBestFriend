# Design Bank

Not in git. Full bootstrap catalogs:

```text
21st/library/catalog.json
aura/library/catalog.json
Refero/bank/catalog.json
motionsites/library/catalog.json
```

Normal `./install.sh` installs the engine only. It does not download Design Bank media.

Run the optional bootstrap during or after install:

```bash
./install.sh --with-design-bank
opencode-bf design bootstrap
```

Bootstrap target order: `OPENCODE_DESIGN_BANK` → existing supported pointer → deprecated `GROK_DESIGN_BANK` → `~/Design`. The target and generated `~/DesignV2` are user data, not installer-owned.

The source declaration is `lib/design_v2/bootstrap_sources.json`. Network access is limited to checksum and archive acquisition. The archive is downloaded with curl, checked against both the downloaded checksum and the pinned SHA-256, bounded and checked for unsafe ZIP members, extracted to a temporary sibling, validated, then atomically committed. A healthy existing target returns `already_present`; an incompatible existing target is never overwritten.

The local pointer remains:

```text
~/.config/opencode/bestfriend/config/design-bank.json
```

After commit, existing DesignV2 APIs pointer-ingest Refero, Motionsites, 21st, and Aura, then dedupe, rebuild, and doctor. Preview media remains only under the Design root. Search, shortlist, inspect, doctor, dedupe, and rebuild do not contact the network.

Design Intelligence ships in-tree (`design-intelligence/`) and stays lazy inside Impeccable.
