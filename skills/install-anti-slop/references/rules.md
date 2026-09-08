# Anti-Slop Rule Fixes & Principles

Guidelines for addressing Anti-Slop linter findings correctly without compromising code quality.

## Correct Fixing Principles

1. **Address Root Causes**:
   - Use TypeScript type inference rather than manual widening.
   - Validate input boundaries with parsers (Zod, ArkType, Schema) instead of type assertions.
   - Use `satisfies` to validate types without widening object literals.
2. **Never Cheat the Linter**:
   - DO NOT replace `unknown` with `any`.
   - DO NOT add extra casts to circumvent checks.
   - DO NOT invent generic or copy-pasted `// SAFETY: safe` comments without real reasoning.
   - DO NOT delete valid regression tests to silence `no-module-mocking`.
   - DO NOT weaken public API signatures without assessing breaking impact.

## Rule Summaries

- **`no-chained-type-assertions`**: `x as object as User` -> Validate input at boundary with schema.
- **`no-conditional-empty-object-spread`**: `...(cond ? { a } : {})` -> Assign conditionally or assemble object imperatively.
- **`no-known-value-widening`**: `const m: Record<string, T> = { k: v }` -> Use `satisfies Record<string, T>`.
- **`no-module-mocking`**: `vi.mock("./store")` -> Inject test doubles through constructor/function parameters.
- **`no-widen-then-assert`**: `const x: unknown = val; (x as Target)` -> Preserve variable's original static type.
- **`require-safety-comment-for-type-assertion`**: Add `// SAFETY: <justification why invariant holds>`.
