#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

usage() {
  cat <<'EOF'
Usage: make-release-artifacts.sh [--sha SHA] [--tag TAG] [--allow-untagged]

Build dist/ from an explicit immutable git commit.
HEAD, VERSION, and --sha must match. A missing or mismatched tag fails
closed unless --allow-untagged is set for CI smoke.
EOF
}

ALLOW_UNTAGGED=0
RELEASE_SHA=""
RELEASE_TAG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --sha)
      RELEASE_SHA="${2:-}"
      shift 2
      ;;
    --tag)
      RELEASE_TAG="${2:-}"
      shift 2
      ;;
    --allow-untagged)
      ALLOW_UNTAGGED=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'SOURCE_REF_MISMATCH: unknown argument %s\n' "$1" >&2
      exit 2
      ;;
  esac
done

VER="$(tr -d '[:space:]' < VERSION)"
NAME="OpenCodeBestFriend-v${VER}"
HEAD_SHA="$(git rev-parse HEAD)"
RELEASE_SHA="${RELEASE_SHA:-$HEAD_SHA}"
EXPECTED_TAG="v${VER}"

if [[ "$HEAD_SHA" != "$RELEASE_SHA" ]]; then
  printf 'SOURCE_REF_MISMATCH: HEAD %s != %s\n' "$HEAD_SHA" "$RELEASE_SHA" >&2
  exit 1
fi

if [[ -n "$RELEASE_TAG" && "$RELEASE_TAG" != "$EXPECTED_TAG" ]]; then
  printf 'VERSION_TAG_MISMATCH: VERSION %s vs tag %s\n' "$VER" "$RELEASE_TAG" >&2
  exit 1
fi

TAG="${RELEASE_TAG:-$EXPECTED_TAG}"
SOURCE_TAG=""
if git rev-parse -q --verify "refs/tags/${TAG}" >/dev/null; then
  TAG_SHA="$(git rev-parse "${TAG}^{commit}")"
  if [[ "$TAG_SHA" != "$RELEASE_SHA" ]]; then
    printf 'SOURCE_REF_MISMATCH: tag %s -> %s != %s\n' "$TAG" "$TAG_SHA" "$RELEASE_SHA" >&2
    exit 1
  fi
  SOURCE_TAG="$TAG"
else
  if [[ "$ALLOW_UNTAGGED" -eq 0 ]]; then
    printf 'SOURCE_REF_MISMATCH: tag %s does not exist\n' "$TAG" >&2
    exit 1
  fi
fi

if [[ -n "$(git status --porcelain --untracked-files=normal)" ]]; then
  printf 'SOURCE_REF_MISMATCH: working tree is not clean\n' >&2
  exit 1
fi

OUT="$ROOT/dist"
rm -rf "$OUT"
mkdir -p "$OUT"
git archive --format=tar --prefix="${NAME}/" "$RELEASE_SHA" | gzip -n >"$OUT/${NAME}.tar.gz"
CREATED="$(python3 - "$RELEASE_SHA" <<'PY'
import subprocess, sys
from datetime import datetime, timezone
sha = sys.argv[1]
ts = subprocess.check_output(["git", "show", "-s", "--format=%ct", sha], text=True).strip()
print(datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
PY
)"
python3 -m lib.release inspect-tar "$OUT/${NAME}.tar.gz" --version "$VER"
python3 -m lib.release pack \
  --root "$ROOT" \
  --out "$OUT" \
  --version "$VER" \
  --sha "$RELEASE_SHA" \
  --tag "$SOURCE_TAG" \
  --created "$CREATED"
printf 'wrote %s from %s tag=%s\n' "$OUT" "$RELEASE_SHA" "${SOURCE_TAG:-NOT_APPLICABLE}"
ls -l "$OUT"
