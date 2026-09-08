---
name: skill-stocktake
description: Audit and maintain quality, hygiene, and boundary integrity across OpenCodeBestFriend skills. Checks frontmatter schema, trigger keywords, exclusivity fences, path references, and test coverage. Use when reviewing installed or warehouse skills, auditing catalog health, or cleaning up skill bloat. Not for code-level security audits (full-audit-keamanan), code style review (matt-code-review), or prompt text optimization (prompt-optimizer).
compatibility: opencode
license: MIT
---

# Skill Stocktake

Quality audit and catalog hygiene specialist for OpenCodeBestFriend skills and commands.

This skill inspects installed skills (`~/.config/opencode/skills/`), manual commands (`~/.config/opencode/commands/`), and repository sources (`skills/`, `manual-skills/`) to maintain tight trigger discipline, clean boundaries, and zero catalog bloat.

## Boundaries & Handoffs

| Need | Route |
|---|---|
| Reviewing application source code quality or standards | `matt-code-review` |
| Auditing code security, secrets, permissions, or supply chain | `full-audit-keamanan` |
| Authoring new SKILL.md files or adapting new skills | `writing-for-agents` |
| Optimizing prompt wording and instructional clarity | `prompt-optimizer` |
| **Auditing skill catalog hygiene, boundaries, and schema conformance** | **`skill-stocktake`** |

## Audit Methodology

Consult [references/checklist.md](references/checklist.md) for the 10-point inspection protocol:

1. **Frontmatter Schema Validation:**
   - Mandatory keys: `name`, `description`, `compatibility: opencode`, `license`.
   - Description length and trigger specificity: description must define unambiguous triggers and explicit negative boundaries ("Use when... Not for...").

2. **Trigger & Routing Discipline:**
   - Detect overlapping or competing trigger phrases across different skills.
   - Verify that model-invoked skills do not shadow manual slash commands.
   - Ensure high-traffic intents have distinct single-specialist ownership.

3. **Path & Environment Hygiene:**
   - Verify all path references target OpenCode paths (`~/.config/opencode/skills/...`).
   - Flag stale references to foreign platforms (Claude Code, Cursor, Codex).

4. **Provenance & Attribution:**
   - Confirm every non-first-party skill contains a compliant `NOTICE.md`.
   - Ensure licenses match approved policies (MIT or Apache-2.0).
   - Verify zero uncredited third-party verbatim copying.

5. **Test & Policy Parity:**
   - Confirm the skill name is registered in `vendor/skill-policy.json` and `vendor/skill-allowlist.txt`.
   - Verify that test assertions in `tests/test_skills.py` reflect the current catalog count.
