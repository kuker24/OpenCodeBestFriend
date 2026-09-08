# Anti-Slop Profiles Guide

## 1. Recommended Profile (OCBF Default)

The recommended profile enables high-signal rules that catch artificial type evidence bypassing without obstructing legitimate software patterns:

- `anti-slop/no-chained-type-assertions`: `"error"`
  Rejects chained `as object as Target` or `<Target><object>x` assertions that fabricate evidence. Chains of `as const` remain valid.
- `anti-slop/no-widen-then-assert`: `"error"`
  Rejects local flows where a known type is widened to `unknown`/`any`/`object` and later re-asserted.
- `anti-slop/no-known-value-widening`: `"warn"` (audit first; upgrade to error after baseline is clean)
  Catches known values explicitly typed as generic `Record<string, unknown>` or `unknown`.
- `anti-slop/require-safety-comment-for-type-assertion`: `"warn"`
  Flags unadorned type assertions that lack a `// SAFETY: <justification>` explanation.

### Excluded from Recommended Default
These rules are reserved for the `strict` or `custom` profiles:
- `no-module-mocking`: Too disruptive for existing test suites that legitimately mock external SDKs/transports.
- `no-runtime-typeof`: `typeof` is valid in projects without schema decoding libraries.
- `no-shape-in-symbol-names`: Pure naming convention, not a type-correctness proof.
- `no-conditional-empty-object-spread`: Depends on object exact-optional semantics.
- `no-object-parameters`, `no-unknown-*`, `no-unsafe-dictionary-type`: Too broad as universal standards.
- `no-reflect-get`, `no-reflect-apply`: Useful only where project policy specifically forbids Reflect metaprogramming.

---

## 2. Strict Profile

Enables all 15 generic upstream rules as `"error"`:
- `anti-slop/no-chained-type-assertions`: `"error"`
- `anti-slop/no-conditional-empty-object-spread`: `"error"`
- `anti-slop/no-known-value-widening`: `"error"`
- `anti-slop/no-module-mocking`: `"error"`
- `anti-slop/no-object-parameters`: `"error"`
- `anti-slop/no-reflect-apply`: `"error"`
- `anti-slop/no-reflect-get`: `"error"`
- `anti-slop/no-runtime-typeof`: `"error"`
- `anti-slop/no-shape-in-symbol-names`: `"error"`
- `anti-slop/no-unknown-parameters`: `"error"`
- `anti-slop/no-unknown-returns`: `"error"`
- `anti-slop/no-unknown-type-aliases`: `"error"`
- `anti-slop/no-unsafe-dictionary-type`: `"error"`
- `anti-slop/no-widen-then-assert`: `"error"`
- `anti-slop/require-safety-comment-for-type-assertion`: `"error"`

---

## 3. Effect Rule Group (Opt-In)

Enables Effect-specific architectural discipline:
- `anti-slop-effect/no-service-constructor-imports`: `"error"`
  Rejects named `make<CapabilityName>` imports from project modules outside tests. Callers must import the owning Layer and yield the contextual service.
