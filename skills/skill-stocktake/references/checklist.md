# 10-Point Skill Hygiene Checklist

Checklist for evaluating skill quality and catalog integrity.

## 1. Frontmatter Conformance
- `name` matches directory name exactly.
- `description` contains both positive activation triggers and negative exclusion boundaries.
- `compatibility` is set to `opencode`.
- `license` is explicitly stated (`MIT` or `Apache-2.0`).

## 2. Trigger Specificity
- Triggers avoid overly broad catch-all words ("code", "fix", "help").
- Activation requires high-signal contextual intent.

## 3. Negative Boundary Definitions
- Explicitly states which sibling specialists handle adjacent tasks.
- Avoids claiming ownership of general programming tasks.

## 4. Single Responsibility
- Skill focuses on one discrete problem domain.
- Does not bundle multi-domain monolithic instructions.

## 5. Path Sanitation
- Zero hardcoded foreign paths (`~/.claude/`, `~/.cursor/`).
- Standardized paths use `~/.config/opencode/`.

## 6. Procedural Determinism
- Core procedures are structured into ordered, reproducible steps.
- Clear distinction between mandatory rules and optional suggestions.

## 7. Toolchain Reality
- Missing host dependencies are reported as `NOT_CONFIGURED`.
- Does not simulate or fake absent binary tools.

## 8. License & Attribution
- Contains `NOTICE.md` with upstream copyright when adapted from third-party sources.
- No proprietary or restrictive non-commercial (CC-BY-NC) source text.

## 9. Policy & Allowlist Alignment
- Skill name is registered in `vendor/skill-policy.json`.
- Skill name is listed alphabetically in `vendor/skill-allowlist.txt`.

## 10. Test Verification
- Skill passes stage and install validation checks in `tests/test_skills.py`.
- Router needle tests in `tests/test_routing.py` verify correct boundary mappings.
