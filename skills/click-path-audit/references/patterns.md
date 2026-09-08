# Click-path patterns

## Store map

```
STORE: <name>
  action(args) → sets: {…} RESETS: {…}

DANGEROUS RESETS
  action → resets field owned by a different action
```

## Patterns

1. **Sequential undo** — call A sets X; call B resets X.
2. **Async race** — two promises write the same field; final value depends on resolve order.
3. **Stale closure** — handler captures an old value and applies it twice.
4. **Missing transition** — label says save/delete/send; handler only validates or sets a flag.
5. **Dead path** — guard is always false at the call site.
6. **Effect interference** — handler sets X; an effect watching X clears it.

## Touchpoint card

```
TOUCHPOINT: [label] in [file:line]
  HANDLER: onClick → { call order and writes }
  EXPECTED: what the label promises
  ACTUAL: final store/UI state
  VERDICT: OK | BUG
```
