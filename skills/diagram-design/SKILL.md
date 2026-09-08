---
name: diagram-design
description: Design editorial HTML and inline SVG diagrams for software architecture, sequence flows, ER data models, system boundaries, and concept maps. Use for high-clarity technical diagrams, visual architecture documentation, and converting raw Mermaid/draw.io into polished visuals. Not for frontend application UI (impeccable) or code-level seam design (codebase-design).
compatibility: opencode
license: MIT
---

# Diagram Design

Editorial diagram specialist for technical systems, data models, workflows, and architecture documentation.

This skill produces publication-grade, self-contained HTML files with embedded responsive SVG graphics. It favors sparse editorial clarity, crisp hierarchy, purposeful deletion, and legible typography over generic chart fluff or unstyled box-and-arrow diagrams.

## Boundaries & Handoffs

| Need | Primary Route |
|---|---|
| Complete product UI, app layout, design system components | `impeccable` (or `found-this-design` first) |
| Module interfaces, code seams, and unit test surfaces in source | `codebase-design` |
| Multi-sketch comparative architecture bake-off | `/architect` (manual) |
| Quick throwaway UI experiment to validate state/logic | `prototype` |
| Quick monospace ASCII art or markdown table is sufficient | Do **not** load this skill |
| **Editorial HTML/inline SVG diagrams (Architecture, Sequence, ER, Wardley, Sankey, Flow)** | **`diagram-design`** |

Mermaid diagrams and draw.io exports are treated as **draft inputs to redraw**, never as final artifacts.

## References

- [references/types.md](references/types.md) — Diagram archetypes, structural semantics, and composition patterns.
- [references/selection.md](references/selection.md) — Decision matrix for selecting the right diagram archetype and complexity budget.
- [references/accessibility.md](references/accessibility.md) — Contrast requirements, font sizing, and accessible SVG labeling.

## Output Format & Constraints

1. **Self-Contained HTML File:**
   - Single `.html` file containing inline responsive `<svg>` with `viewBox`, clean CSS variables for palettes and typography, and embedded system fonts (`system-ui`, `ui-sans-serif`, `-apple-system`).
   - Scales responsively with `width: 100%; height: auto; max-width: 1200px;`.
2. **Export Capabilities:**
   - If CLI tools (`resvg`, `playwright`, `puppeteer`) are available on the host, render to high-res PNG/SVG.
   - If export binaries are absent, the HTML file itself is the final deliverable and export is marked `NOT_CONFIGURED`.
3. **Typography & Contrast:**
   - Minimum font size: 12px for metadata, 14px for node bodies, 18-24px for subsystem headers.
   - Text contrast must exceed WCAG 2.1 AA (minimum 4.5:1 ratio against container backgrounds).
4. **Purposeful Deletion:**
   - Eliminate redundant arrows, decorative gradient fills, drop-shadow clutter, and ambiguous floating icons.
   - Group related nodes inside clear subsystem boundaries with subdued background cards.
