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
| Authoring or rewriting SKILL.md bodies and descriptions | `writing-for-agents` |
| Optimizing prompt wording and instructional clarity | `prompt-optimizer` |
| Measuring whether a skill actually beats no-skill | `eval-harness` |
| **Auditing skill catalog hygiene, boundaries, and schema conformance** | **`skill-stocktake`** |

This skill audits and reports. It does not rewrite another skill's body, and it does not delete files.

## Verdict Protocol

Every audited skill or command resolves to exactly one verdict. No item is left unjudged, and no item carries two verdicts.

| Verdict | Meaning |
|---|---|
| `KEEP` | Unique trigger, current artifacts, defensible cost asymmetry, existence pass clears |
| `COMPRESS` | Still needed, but the body is longer than the judgment it carries. Scripts and verification gates survive; prose shrinks |
| `UPDATE` | Artifacts, versions, paths, or flags are stale. Requires cited evidence |
| `MERGE → <target>` | Overlaps a sibling. Name the single target and the residue that moves |
| `RETIRE` | Existence pass fails, or the no-skill baseline matches the with-skill run, or the trigger was always covered by runtime, rules, Context7, or the model itself |

## Audit Methodology

Consult [references/checklist.md](references/checklist.md) for the full inspection protocol.

1. **Existence pass (ask explicitly, per item):**
   - If this file disappeared, would the user lose a job that no other skill, rule, core MCP, or cheap on-demand generation already covers?
   - Does an independent trigger plus reusable judgment justify the selection cost, drift risk, and maintenance burden?
   - A skill that only restates what a current model does unprompted fails this pass.

2. **Currency pass:**
   - Paths resolve under `~/.config/opencode/...`, not foreign agent-host directories.
   - Flag references to foreign platforms and stale CLI flags, versions, or pinned artifacts.
   - Preserve greppable terms, self-enforcing prohibitions, and numeric thresholds verbatim. Do not abstract them into softer prose.

3. **Frontmatter schema validation:**
   - Mandatory keys: `name`, `description`, `compatibility: opencode`, `license`.
   - `name` matches the directory name.
   - Description carries unambiguous positive triggers and explicit negative boundaries ("Use when... Not for...").

4. **Trigger and routing discipline:**
   - Detect overlapping or competing trigger phrases across skills.
   - Verify model-invoked skills do not shadow manual slash commands.
   - Confirm each high-traffic intent has one owner.

5. **Provenance and policy parity:**
   - Non-first-party skills carry a compliant `NOTICE.md` under MIT or Apache-2.0. Unknown license is not a grant.
   - Name is registered in `vendor/skill-policy.json` and listed alphabetically in `vendor/skill-allowlist.txt`.
   - `tests/test_skills.py` assertions match the measured tree, not a remembered count.

## Evidence Requirement

`UPDATE`, `MERGE`, and `RETIRE` are not opinions. Cite at least one of: a path listing, a `--help` or version probe, a checksum, an upstream doc reference, or a no-skill baseline from `eval-harness`. An unproven claim downgrades to `KEEP` with a follow-up note.

## Output

Report a single table, one row per audited item, plus a short list of follow-ups.

```text
| Skill | Verdict | Evidence | Handoff |
```

Handoffs: `COMPRESS` and `UPDATE` go to `writing-for-agents` (structure, description, pointers) or `prompt-optimizer` (instruction phrasing). Security findings go to `full-audit-keamanan`. Application code style goes to `matt-code-review`. Utility measurement goes to `eval-harness`.

Never auto-delete a file, never auto-edit another skill's body, and never mutate a catalog from a learning log.
