#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
DIR="${1:-dist}"
EXPECTED_COMMIT="${2:-}"

if [[ -n "$EXPECTED_COMMIT" ]]; then
  python3 -m lib.release verify "$DIR" --root "$ROOT" --expected-commit "$EXPECTED_COMMIT"
else
  python3 -m lib.release verify "$DIR" --root "$ROOT"
fi
