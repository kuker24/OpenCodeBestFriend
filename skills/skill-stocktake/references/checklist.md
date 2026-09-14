# Skill Hygiene Checklist

Inspection protocol behind the verdict table. Work an item top to bottom, then assign exactly one verdict: `KEEP`, `COMPRESS`, `UPDATE`, `MERGE → <target>`, or `RETIRE`.

## 1. Existence Pass

- If this file disappeared, does the user lose a job that no other skill, rule, core MCP, or cheap on-demand generation already covers?
- Is the trigger independent, or does it only fire when another skill is already loaded?
- Does the reusable judgment justify the selection cost, drift risk, and maintenance burden?
- Does the body only restate behavior a current model already performs unprompted? If yes, this is `RETIRE` or `COMPRESS`, never a twin skill.

Failing this pass is sufficient grounds for `RETIRE`.

## 2. Currency Pass

- Paths resolve under `~/.config/opencode/`. No foreign agent-host directories as runtime targets.
- No stale references to foreign platforms, except in an explicitly negative or isolating sentence.
- Pinned versions, CLI flags, artifact names, and checksums still match reality.
- Greppable terms, self-enforcing prohibitions, and numeric thresholds are preserved verbatim, not abstracted.

Any stale artifact is `UPDATE`, with the probe cited.

## 3. Frontmatter Conformance

- `name` matches the directory name exactly.
- `description` carries positive activation triggers and negative exclusion boundaries.
- `compatibility` is `opencode`.
- `license` is stated explicitly (`MIT` or `Apache-2.0`).

## 4. Trigger Specificity

- Triggers avoid catch-all words ("code", "fix", "help").
- Activation requires high-signal contextual intent.
- No competing ownership of the same intent across two skills.

## 5. Boundary and Collision Integrity

- Adjacent tasks name their sibling specialist explicitly.
- Model-invoked names never shadow a manual slash command.
- Description overlap against every sibling stays under the lexical gate enforced in `tests/test_skills.py`: warn at 50%, fail at 75% Jaccard over lowercase alphanumeric tokens.

High overlap plus a shared intent is `MERGE → <target>`; name the residue that moves.

## 6. Cost Asymmetry

- Weigh the always-loaded description cost against how often the skill is the correct route.
- A rarely correct skill with a broad description is a net loss even when its body is good.
- Prefer one skill with a sharp fence over two with fuzzy fences.

## 7. Body Economy

- Procedures are ordered and reproducible; mandatory rules are separable from suggestions.
- Tested scripts in the skill folder outrank prose restating what the model already does.
- Prose that exceeds the judgment it carries is `COMPRESS`; scripts and verification gates survive compression.

## 8. Toolchain Reality

- Missing host dependencies report `NOT_CONFIGURED`.
- No simulated or faked absent binaries.
- No dependency on a foreign harness runtime, control plane, or auto-mutation loop.

## 9. Provenance and Attribution

- Adapted skills carry `NOTICE.md` with upstream copyright.
- License is MIT or Apache-2.0. Unknown license is not a grant.
- No proprietary or non-commercial (CC-BY-NC) source text.

## 10. Policy and Test Parity

- Name is registered in `vendor/skill-policy.json`.
- Name is listed alphabetically in `vendor/skill-allowlist.txt`.
- `tests/test_skills.py` reconciles declared counts against the measured `skills/`, `manual-skills/`, and `commands/` trees.
- Router needle tests in `tests/test_routing.py` still map the boundary correctly.

## 11. Evidence and Handoff

- `UPDATE`, `MERGE`, and `RETIRE` cite a path listing, a `--help` or version probe, a checksum, an upstream doc, or an `eval-harness` no-skill baseline.
- Unproven claims downgrade to `KEEP` with a follow-up note.
- `COMPRESS` / `UPDATE` → `writing-for-agents` or `prompt-optimizer`. Security → `full-audit-keamanan`. Application code style → `matt-code-review`. Utility measurement → `eval-harness`.

Report verdicts. Do not delete files and do not rewrite another skill's body from this audit.
