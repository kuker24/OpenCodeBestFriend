# REST conventions

## Status

| Code | Use |
|---|---|
| 200 | GET/PUT/PATCH with a body |
| 201 | POST create; set `Location` |
| 204 | DELETE or empty PUT |
| 400 | Malformed request |
| 401 | Missing or invalid auth |
| 403 | Authenticated, not allowed |
| 404 | Resource missing |
| 409 | Duplicate or state conflict |
| 422 | Well-formed JSON, invalid data |
| 429 | Rate limit; set `Retry-After` |
| 500 | Unexpected failure; no internals |

## Pagination

| Case | Choice |
|---|---|
| Admin UI, search with page numbers, <10k rows | Offset `page` + `per_page` |
| Feeds, infinite scroll, public lists | Opaque cursor + `limit` |
| Mixed public API | Cursor default; offset optional |

## Versioning

- Additive: new optional fields, new endpoints, new query params — same version.
- Breaking: rename/remove fields, type changes, URL or auth changes — new version.
- Keep at most current + previous. Announce sunset; then `410 Gone`.

## Checklist

- Plural kebab-case resources, no verbs in collection paths
- Semantic status codes
- Validated input; field-level 422 details
- List endpoints paginated
- Auth required or explicitly public
- Authorization on owned resources
- Rate-limit headers on public surfaces
- No stack traces or SQL in error bodies
- OpenAPI updated when the contract is shared
