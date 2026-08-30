# Design Bank

Not in git. Catalogs required:

```text
Refero/bank/catalog.json
motionsites/library/catalog.json
```

Discover order: `OPENCODE_DESIGN_BANK` (deprecated alias `GROK_DESIGN_BANK`) → existing pointer → `~/Design` → owned cache → download GrokBestFriend v1.0.0 `Design-bank.tgz` (SHA-256 fail-closed).

Owned extract destination:

```text
~/.local/share/opencode-bestfriend/design-bank/
```

Pointer:

```text
~/.config/opencode/bestfriend/config/design-bank.json
```

`./install.sh --skip-design-bank` yields `DEGRADED_DESIGN_BANK`.

Design Intelligence ships in-tree (`design-intelligence/`) and stays lazy inside Impeccable.
