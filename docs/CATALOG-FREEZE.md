# Catalog Freeze Contract (1.8.6)

This contract defines the immutable boundary and governance for the OpenCodeBestFriend catalog following the 1.8.6 modernization closeout.

- **Product version**: 1.8.6
- **Catalog**: 62 names. 47 model-invoked under `skills/`. 15 manual under `manual-skills/` + `commands/`.
- **Retired in this wave and not to be revived**: `ask-matt`, `grilling`, `wait-what`, `matt-implement`.
- **Kept on purpose**: `wizard` (target-app bash wizard), `codebase-design` (new module), `/improve-codebase-architecture` (scan + HTML report).
- **Name collision remains**: `install-anti-slop` = Oxlint; UI/copy filter lives in `impeccable` taste-gate + `humanizer`; `/unslop` = `humanizer`.
- **FOREIGN_ON_DEMAND stays out of the overlay**: `ECC`, `noodle`, `serena`, `stitch`, `reticle`, `ui-skills` MCP, `markitdown` MCP, `exa`, `Caliper`, `SkillEvaluator`. `doctor` must not fail when they are absent.
- **No new allowlist name without retiring one existing name in the same change.**
- **No padding back to 64.**
- **No `/how`, `/poteto-mode`, `/antislop`, `taste-skill`, `axi-core`, `human-atlas`, `awesome-design-md` vendor.**
- **No auto-edit of skills/rules from a learning log. No silent `--auto`.**
- **Next unfreeze requires a human-written exception in CHANGELOG Unreleased that names the retired twin.**
