# Taste Quality Guard

Canonical lightweight quality guard for UI implementation and review.
Adapted from [taste-skill](https://github.com/Leonxlnx/taste-skill) (MIT, Leonxlnx) to integrate with OpenCodeBestFriend craft standards.

Load this once before UI editing and verify against it during final review. This reference is not a separate specialist; it operates within the phase owner (`impeccable`, `scroll-craft`, `emil-design-eng`).

## Precedence & Conflict Resolution

When guidelines diverge, resolve in strict order:
1. **User Scope & Request**: Explicit brief, pinned aesthetic, brand guidelines, and user constraints always win.
2. **Product Truth & Accessibility**: Real facts, working functionality, keyboard navigation, WCAG AA contrast (≥4.5:1 body, ≥3:1 large), and measured performance outrank aesthetic taste.
3. **Project System & Stack**: Inherit existing tokens, theme, components, and package manager. Never force Tailwind v4, React/Next.js, Motion, or new fonts onto projects that do not use them.
4. **OCBF Architecture Contracts**: Phase ownership, thin routing, isolated tests.
5. **Taste Heuristics**: Guidelines below refine execution; they never overrule layers 1–4.

*Anti-Dogma Rule*: Taste guidelines discourage unexamined category defaults, but they are NOT absolute bans. Purple accents, Inter font, SVG icons, symmetrical grids, eyebrows, or cards are fully permitted when the brand, project, or user requests them.

---

## The 11 Core Quality Guardrails

### 1. Intent & Surface Mode
- Classify the surface purpose: **Persuade** (marketing/landing), **Operate** (dashboard/admin/tools), **Read** (docs/articles), or **Experience** (showcase/portfolio).
- Match density and expression to mode: Operate demands scanability, high utility, and native conventions; Persuade allows bolder visual commitment.

### 2. Information Hierarchy & Typography
- Obvious visual scale: one dominant focal point per viewport, clear heading-to-body rhythm.
- Display type: default tight tracking, balanced lines; descender clearance on italic display fonts (`pb-1` / minimum `leading-[1.1]`).
- Body text: comfortable measure (65–75ch), readable line-height, distinct secondary text hierarchy.

### 3. Spacing & Visual Rhythm
- Consistent padding and gap scale across the page; more whitespace above a section heading than below it.
- Never let heroes float arbitrarily far down the viewport (cap hero top padding at ~6rem / `pt-24`).
- Desktop navigation on a single line (max height 80px).

### 4. Components, Tokens, & Navigation
- Single palette lock: choose neutral base + one primary accent role; maintain accent consistency throughout the page.
- Corner radius consistency: uniform scale across cards, inputs, and buttons unless a distinct token hierarchy is documented.
- Inherit existing design system tokens and component libraries where present.

### 5. Product Truth & Factual Content
- **Zero Hallucinated Precision**: Never invent precise statistics (`94.2%`, `4.8x`), fake customer logos, fake review quotes, or fake partner endorsements.
- If demonstration data is needed in greenfield work, label it clearly as synthetic demonstration data.
- Refinement preserves existing copy and claims; redesign replaces presentation while preserving factual truths.

### 6. Complete Interactive States
- Implement the full lifecycle: default, `:hover`, `:focus-visible`, `:active` (subtle tactile feedback), disabled, loading, empty, and inline error states.
- CTA clarity: button labels fit on a single line at desktop; avoid duplicate CTA intents with competing labels on the same page.

### 7. Responsiveness & Breakpoint Defense
- Explicit mobile collapse (`< 768px`) for every multi-column layout or bento grid; verify no horizontal overflow.
- Viewport stability: use `min-h-[100dvh]` rather than `h-screen` to prevent iOS address-bar layout jumping.
- Test with real copy at actual target viewports, not placeholder words that never wrap.

### 8. Accessibility & Reduced Motion
- Every interactive element has a visible, high-contrast `:focus-visible` ring.
- Respect `prefers-reduced-motion`: all ambient motion, parallax, and scroll-triggers must collapse to clean static presentation.
- Dark and light modes: maintain legible hierarchy and WCAG AA contrast across both color schemes.

### 9. Motivated Visual Effects
- Every animation must have a clear purpose: hierarchy, feedback, narrative pacing, or state change. If an effect cannot be justified in one sentence, omit it.
- Avoid unmotivated glassmorphism, glowing borders, or arbitrary parallax loops.
- Horizontal marquees: at most one per page where content genuinely benefits from continuous stream.

### 10. Dependency & Stack Discipline
- Verify packages in `package.json` before importing. Never assume a 3rd-party library is present.
- Do not introduce heavy dependencies (GSAP, Three.js, heavy icon sets) for simple CSS or native capabilities.

### 11. Observed Render Verification
- Judge visual quality solely on actual rendered output (inspected browser session or captured screenshot), never on stylesheet intention or mental model.
- Inspect desktop and mobile together before signing off.
