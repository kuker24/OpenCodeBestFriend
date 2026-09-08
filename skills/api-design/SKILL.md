---
name: api-design
description: Design or review REST API contracts — resource naming, HTTP methods, status codes, pagination, filtering, errors, versioning, and rate-limit headers. Use when shaping or auditing HTTP endpoints. Not for library/API docs (research/Context7), consumer-provider schema ownership (contract-first), or auth/secrets review (full-audit-keamanan).
compatibility: opencode
license: MIT
---

# API Design

First-party REST design specialist. Shape the public HTTP surface so clients can predict resources, status, errors, and pagination without guessing.

## Boundaries & Handoffs

| Need | Route |
|---|---|
| Official library or framework docs | `research` / Context7 |
| One canonical OpenAPI/AsyncAPI/Protobuf artifact shared by consumers and providers | `contract-first` |
| Auth, secrets, public API attack surface | `full-audit-keamanan` |
| Module seams and testability inside one codebase | `codebase-design` |
| **REST resource, status, pagination, error, and versioning design** | **`api-design`** |

## Procedure

Consult [references/conventions.md](references/conventions.md) for the checklist.

1. **Name the resource.** Nouns, plural, lowercase kebab-case. Nest only for true ownership. Verbs belong on actions that are not CRUD (`POST /orders/:id/cancel`).
2. **Pick the method and status.** GET/PUT/DELETE are idempotent. POST creates or triggers. Do not wrap failures in `200` with `"success": false`.
3. **Lock the envelope.** One success shape and one error shape for the API. Collections carry pagination meta. Errors carry a stable `code`, a message, and field details when validation fails.
4. **Paginate lists.** Offset for small admin/search pages. Cursor for feeds and public lists. State which one, and why.
5. **Filter and sort as query params.** Equality, bracket comparators, comma-separated multi-values. Do not invent a second RPC style beside REST.
6. **Version only on breaking changes.** Path `/api/v1` is the default. Additive fields do not need a new version. Breaking changes need a deprecation window.

Do not dump framework tutorials. Implement in the project's existing stack.

## Output

Return a contract sketch: paths, methods, status codes, request/response fields, pagination choice, and breaking vs additive notes. Point `contract-first` at the artifact if more than one consumer will implement against it.
