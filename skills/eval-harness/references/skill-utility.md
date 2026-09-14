# Skill Utility Gate (A/B)

Decide whether a skill earns its always-loaded description cost. This measures the skill against its own absence, not against a competitor.

Runs locally. No network, no API key, no external harness runtime, no container image.

## 1. Scope the Claim

Write the claim in one sentence, taken from the skill's own description: what job does it say it wins?

The gate only tests that claim. A skill that wins some unrelated task still fails if it does not beat no-skill on its own claimed job.

## 2. Build the Dataset

Minimum three bands, small on purpose:

- **Happy path** — the canonical case the description promises.
- **Boundary** — same domain, awkward input: missing field, ambiguous intent, conflicting constraint.
- **Adjacent-negative** — a task the description explicitly excludes. Correct behavior is declining or handing off.

Five to ten cases per band is enough to expose a dead skill. Record inputs and expected output properties before running anything.

## 3. Run Both Arms

- **Run A (baseline):** the task with the skill absent from context.
- **Run B (treatment):** the identical task with the skill loaded.

Same model, same temperature, same tooling, same ordering. Change one variable only.

## 4. Score

Deterministic assertions first, per the tiers in [methodology.md](methodology.md). Reach for a model-graded rubric only when the property cannot be checked mechanically.

Record per arm:

- Quality score against the rubric
- `pass@1`, and `pass@k` when the workflow is stochastic
- Total tokens, prompt and completion separately
- Wall-clock latency

Keep `pass@1` and `pass@k` as named metrics. Do not collapse them into a generic 1-5 rating.

## 5. Verdict Thresholds

| Result | Reading |
|---|---|
| B beats A on quality | Utility pass |
| Quality equal, B uses fewer tokens or less latency | Utility pass |
| Quality equal, B costs more | Utility fail; the body is overhead |
| `A ≈ B` on the skill's own claimed task | Evidence for `RETIRE` |
| B wins only on a subset, and the rest of the body is inert | Evidence for `COMPRESS` |
| B fails the adjacent-negative band where A passed | Fence is too broad; fix the description before re-testing |

Quality parity means identical verdicts on every gold case, not a close average.

## 6. Hand Off

Report the numbers and route the decision. `RETIRE` and `COMPRESS` proposals go to `skill-stocktake`, which owns the verdict table and the catalog view. This gate supplies the baseline; it does not delete skills, edit `SKILL.md`, or change the allowlist.

Project unit tests stay with `tdd`. Browser flows stay with `playwright-qa`. Security findings stay with `full-audit-keamanan`.
