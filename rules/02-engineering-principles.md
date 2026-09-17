# Engineering principles (managed, Read on demand)

Read this file only when a skill or the user asks for operational principles. Do not `@`-import it. Path after install:

`~/.config/opencode/bestfriend/rules/02-engineering-principles.md`

These are working rules, not an essay and not a skill catalog. Apply the smallest set that changes the next action.
Adapted in part from cursor/plugins pstack principles (MIT © 2026 Lauren Tan). Full `principle-*` skills are not installed.

1. **Smallest change.** Prefer the edit that solves the stated problem and nothing else. Minimize the diff. Question a new signal threaded through types, schemas, or pipelines; look for a direct path.
2. **Foundational thinking.** Scaffold and verification before features when the shape is still wrong.
3. **Subtract before add.** Delete or collapse a wrong layer before introducing a new one. Prefer deletion when asked to refactor.
4. **First principles.** When the current shape fights the work, redesign from the constraint, not from the last patch.
5. **Domain first.** Name the real nouns and seams before inventing modules.
6. **Boundary discipline.** Hide complexity behind a small public surface. Do not leak internals to callers.
7. **Idempotency.** Operations that may retry must be safe to run twice.
8. **Prove it.** A claim needs an artifact: test, command output, screenshot, commit, or file:line. Test behavior users can observe, not private implementation details, unless the seam itself is the contract.
9. **Root cause.** Fix the cause. Do not paper over the symptom unless the user asked for a temporary guard.
10. **Verifiable units.** Land work in independently checkable pieces. Do not batch verification at the end.
11. **Guard context.** Load one specialist. Do not dump every skill into the window.
12. **Encode lessons.** Recurring corrections become a gate, lint, test, or script — not a memory of “be careful”, and not a comment that restates the code.
13. **Exhaust the design space only when warranted.** Two structurally different sketches for one-way-door design. Skip for mechanical work whose shape is already concrete.
14. **Attack the premise.** After two fixes that share one assumption fail the same gate, write the assumption down and measure who holds the imbalance before writing a third patch.
15. **Build the lever.** When the same check will run again, write the script that does it. Do not hand-walk the census.
16. **Experience first.** Judge the running product. A green unit suite is not a substitute for the user-visible path.
17. **Migrate callers, then delete.** Do not leave a legacy API beside the new one. Move callers, delete the old surface in the same effort when safe.
18. **Minimize reader load.** Flat call chains. One source of truth for a decision. A human who must trace more than three files to answer “what happens” is a design smell.
19. **Type-system discipline.** Put invariants in types and tests, not in comments that beg the next editor to be careful.
20. **Separate before sharing mutable state.** Do not serialize access to a blob that should have been two values.
21. **Outcome over ceremony.** Optimize for the falsifiable done-predicate, not for looking busy.
22. **Do not block the human on reversible work.** In this session, make the reversible edit and show it. Confirm only irreversible steps (force-push, production delete, external send) or product direction. This is not a license for `--auto`, overnight merge fleets, or skill self-mutation.
