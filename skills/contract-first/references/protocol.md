# Contract change protocol

1. Propose the consumer need and compatibility impact.
2. Change the canonical artifact.
3. Review the diff with affected consumers and the provider.
4. Regenerate types, clients, or fixtures.
5. Update implementations.
6. Verify both sides against the artifact.
7. Merge only when affected owners agree.

## Anti-patterns

- Provider leaks storage models (`SELECT *`) as the public shape.
- Wiki, mock JSON, frontend types, and serializer each claim the same payload.
- `as unknown as Contract` hiding runtime drift.
- Rename a field in one implementation without a contract diff.
- Generate the spec after both sides already shipped.

## Completion

- Owners known
- One authoritative artifact named
- Required fields, nullability, enums, and errors explicit
- Consumer types/fixtures derived from the artifact
- Provider responses verified, including error and empty paths
- Breaking changes have a version or migration plan
