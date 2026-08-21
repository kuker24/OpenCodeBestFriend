#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export OPENCODE_BF_ROOT="$ROOT"
export OPENCODE_DISABLE_CLAUDE_CODE=1
exec python3 -m unittest tests.test_install tests.test_mcp -v
