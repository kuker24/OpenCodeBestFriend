#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
VER="$(tr -d '[:space:]' < VERSION)"
NAME="OpenCodeBestFriend-v${VER}"
OUT="$ROOT/dist"
rm -rf "$OUT"
mkdir -p "$OUT"
git archive --format=tar.gz --prefix="${NAME}/" -o "$OUT/${NAME}.tar.gz" HEAD
(
  cd "$OUT"
  sha256sum "${NAME}.tar.gz" > SHA256SUMS
)
python3 - "$ROOT" "$OUT/SBOM.spdx.json" "$VER" <<'PY'
import json, sys, datetime
root, dest, ver = sys.argv[1], sys.argv[2], sys.argv[3]
prov = json.loads(open(f"{root}/vendor/provenance.json", encoding="utf-8").read())
doc = {
    "spdxVersion": "SPDX-2.3",
    "dataLicense": "CC0-1.0",
    "SPDXID": "SPDXRef-DOCUMENT",
    "name": f"OpenCodeBestFriend-{ver}",
    "documentNamespace": f"https://github.com/kuker24/OpenCodeBestFriend/spdx/{ver}",
    "creationInfo": {
        "created": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "creators": ["Tool: opencode-bestfriend-release"],
    },
    "packages": [
        {
            "SPDXID": "SPDXRef-Package-OpenCodeBestFriend",
            "name": "OpenCodeBestFriend",
            "versionInfo": ver,
            "downloadLocation": "https://github.com/kuker24/OpenCodeBestFriend",
            "licenseDeclared": prov.get("firstPartyLicense") or "MIT",
        }
    ],
}
for i, c in enumerate(prov.get("components") or []):
    doc["packages"].append(
        {
            "SPDXID": f"SPDXRef-Component-{i}",
            "name": c.get("component"),
            "licenseDeclared": c.get("license") or "NOASSERTION",
        }
    )
open(dest, "w", encoding="utf-8").write(json.dumps(doc, indent=2) + "\n")
PY
echo "wrote $OUT"
ls -l "$OUT"
