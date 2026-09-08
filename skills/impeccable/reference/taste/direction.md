# Taste: Direction & Brief Inference

Deep reference module for Impeccable (Persuade and Experience modes).
Adapted from [taste-skill](https://github.com/Leonxlnx/taste-skill) (MIT, Leonxlnx).

Load this when a new surface, campaign, landing page, portfolio, or major redesign requires establishing a visual direction.

## 1. Reading the Brief Before Code

Infer the visitor scene and context:
1. **Surface Purpose**: Landing (SaaS, consumer, event), portfolio (engineer, designer, studio), editorial, or showcase.
2. **Context Signals**: User adjectives, competitor references, linked URLs, cultural anchors.
3. **Audience Demographics**: Technical buyers vs design-conscious consumers vs hiring managers. The audience sets the register, not developer preference.
4. **Existing Brand Assets**: Pinned logos, fonts, palettes, and imagery are starting material to inherit and elevate, not ignore.
5. **Quiet Constraints**: Regulated industries, public sector, and high-trust commerce enforce strict clarity over artistic eccentricity.

State a 1-line Design Read in the surface brief:
`Reading this as: <page kind> for <audience>, with a <vibe> language, leaning toward <aesthetic family>.`

## 2. Anti-Default Discipline

Deliberately step beyond default training-data tropes:
- Avoid the predictable triad: warm beige background + terracotta/brass accent + high-contrast display serif.
- Avoid the "AI startup dark theme": near-black + glowing purple/cyan mesh + gradient text on all headings.
- Avoid 3 identical feature cards with generic rounded icons.
- Reach for authentic material metaphors grounded in the product's real domain.

## 3. The Three Dials (Recorded in Surface Brief)

Record visual dial choices in the project's surface brief (`.impeccable/briefs/` or memory):
- **`DESIGN_VARIANCE` (1–10)**:
  - 1–3: Symmetrical, predictable grid, uniform padding.
  - 4–7: Offset rhythms, varied aspect ratios, intentional asymmetric whitespace.
  - 8–10: Asymmetric hero compositions, expressive editorial layouts (collapsing to clean single-column on mobile).
- **`MOTION_INTENSITY` (1–10)**:
  - 1–3: Static with crisp `:hover` and `:active` feedback. Default for task-oriented surfaces.
  - 4–7: Orchestrated entrance reveals, smooth transitions, spring physics.
  - 8–10: Scroll-driven timelines, interactive choreography (always with full reduced-motion fallback).
- **`VISUAL_DENSITY` (1–10)**:
  - 1–3: Generous whitespace, gallery spacing (`py-24` to `py-36`).
  - 4–7: Standard web application density (`py-12` to `py-20`).
  - 8–10: High-density data presentation, minimal padding, structured tables/lists.

*Note*: These dials are recorded as qualitative guidance within the surface brief, never as global hard gates that alter non-UI or dashboard code.
