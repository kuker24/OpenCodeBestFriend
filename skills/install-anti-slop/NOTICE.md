# Anti-Slop Skill Notice

This skill vendors and adapts the Anti-Slop Oxlint plugin originally authored by Dillon Mulroy.

- Upstream repository: https://github.com/dmmulroy/anti-slop
- Upstream commit: e8c4880471b23ab7f216fba7b27d173a6ef07d4c
- Upstream version: 0.1.2
- License: MIT License (see vendor/licenses/DMMULROY-ANTI-SLOP-MIT.txt)
- Copyright (c) 2026 Dillon Mulroy

## Modifications for OpenCodeBestFriend
- Adapted as an opt-in model-invoked skill for TypeScript/JavaScript projects.
- Added `scripts/manage.mjs` supporting 4 explicit modes:
  - `audit`: isolated discovery reporting findings per rule and file category without repo mutations.
  - `recommended`: curated high-signal OCBF profile (`no-chained-type-assertions`, `no-widen-then-assert`, audit on `no-known-value-widening`, audit/warn on `require-safety-comment-for-type-assertion`).
  - `strict`: full 15-rule generic ruleset from upstream snapshot.
  - `custom`: project-configured rules.
  - `effect`: opt-in Effect service layer rules for direct Effect dependencies.
- Added safe removal, update, idempotency checks, and collision detection.
- Strictly segregated from core OCBF Python dependencies (no Oxlint forced onto OCBF itself).
