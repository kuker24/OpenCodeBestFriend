# Skills

Policy: `vendor/skill-policy.json` plus `vendor/skill-allowlist.txt`.

- 24 model-invoked skills live under `skills/` and install to `~/.config/opencode/skills/`
- 16 manual skills live under `manual-skills/` and install to `~/.config/opencode/bestfriend/skills/` plus `commands/`

OpenCode 1.18.x has no `disable-model-invocation` field. Manual skills must not be copied into the discovered skills directory.

`opencode-bf skills verify` checks counts, missing files, and duplicates.
