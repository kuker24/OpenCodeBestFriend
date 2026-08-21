#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
export OPENCODE_BF_ROOT="$ROOT"
export OPENCODE_DISABLE_CLAUDE_CODE="${OPENCODE_DISABLE_CLAUDE_CODE:-1}"
exec python3 "$ROOT/lib/cli.py" uninstall "$@"
