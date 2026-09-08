# CodeTour format

Write to `.tours/<persona>-<focus>.tour`. Schema: `https://aka.ms/codetour-schema`.

## `ref`

| Tour | `ref` |
|---|---|
| PR | PR branch — never the base (new files are missing there) |
| Onboarding / architecture | Reader's branch (often `main`), or omit |
| Unsure | Omit so the editor reads the working tree |

## Step types

- Directory — orient to a module
- File + line — default
- Selection — one block matters more than the file
- Pattern — exact lines may drift
- URI — PR, issue, or doc
- Content-only — closing step only; never the first step

## Anti-patterns

- Flat file listing instead of a path
- Generic descriptions
- Guessed anchors
- Too many steps for a quick tour
- First step content-only
