---
name: scroll-craft
description: "Build scroll-led storytelling websites where scroll is the timeline: scrollytelling, signature interaction, pin/pan/reveal, layered hero, cinematic scroll without camera flight. Use when the user runs /scroll-craft, or asks for a site where scrolling tells the product story. Not for ordinary dashboards or landings (impeccable), continuous camera fly-through / diorama / 3D world (scroll-world), chrome motion (emil-design-eng), or photoreal ads (visual-studio)."
compatibility: opencode
license: MIT
---

# Scroll Craft

Scroll is the timeline. The page is a story the visitor drives with their hand.
One grammar, one peak, one signature move. Premium means clear composition and
a meaningful interaction, not video, pinning, or effects.

## Load when

| Need | File |
|---|---|
| Journey, feeling curve, peak | [journey.md](references/journey.md) |
| Eight grammars | [grammars.md](references/grammars.md) |
| Devices and `--sc-p` | [devices.md](references/devices.md) |
| Signature + fingerprint | [signature-fingerprint.md](references/signature-fingerprint.md) |
| Optional hero depth | [hero-depth.md](references/hero-depth.md) |
| Mobile, keyboard, reduced motion | [mobile-accessibility.md](references/mobile-accessibility.md) |
| Scroll verification | [verification.md](references/verification.md) |
| Continuous World / media / QA | [handoff.md](references/handoff.md) |

Do not read every reference on every request. Engine:
[scrollcraft.js](engine/scrollcraft.js), [scrollcraft.css](engine/scrollcraft.css).
The mechanism CSS is safe for an existing design system; the scoped
[starter theme](engine/scrollcraft-theme.css) is optional. Copy what the project
needs; do not edit the mechanism per page. Drive bespoke behaviour from
`--sc-p`. Attribution: [NOTICE.md](NOTICE.md).

## Hard rules

- One primary specialist. This skill owns the scroll story. Do not auto-load
  Impeccable for every build step.
- Ordinary scrollable UI stays Impeccable. Words like `premium`, `cinematic`,
  `interactive`, or `layered` alone are not enough.
- Continuous camera / fly-through / diorama / 3D world → hand off to
  `scroll-world` after a minimum brief. Do not implement worldflight here.
- Follow the project stack. Do not force a standalone HTML file onto React/Vue.
- Semantic HTML for headings, CTA, nav, and forms. Core content readable with
  JS off and with reduced motion.
- No scroll hijacking. No wheel/touch/keyboard traps.
- No KIE, Higgsfield, ffmpeg, Playwright, font CDN, or remote assets on the
  core path. Tier 1 is HTML/CSS/transforms/sticky/local assets/light JS.
- Do not invent brand facts, stats, testimonials, or user quotes.
- Live Surface controls must work. Label synthetic demos. Never fake a
  successful transaction.
- Design V2 is optional, offline, read-only. Empty bank does not block build.
- Store brief/fingerprint/evidence under `.scratch/scroll-craft/<slug>/` in the
  user project. Not in this skill folder. No new global home.

## Handoff

| Request | Owner |
|---|---|
| Scroll-led storytelling / scrollytelling | this skill |
| `/scroll-craft` plus Continuous World | this skill enters, then `scroll-world` |
| Continuous camera, diorama, 3D world (no slash) | `scroll-world` |
| Dashboard, ordinary landing, design system | `impeccable` |
| Hover/press/easing after the surface exists | `emil-design-eng` |
| Standalone photoreal / ads / identity | `visual-studio` |
| Exploratory QA | `browser-act` |
| Observed browser cause | `opencode-chromium-cdp` then `chrome-devtools-axi` |

## Run

1. Read PRODUCT.md, DESIGN.md, tokens, and existing assets. Reuse answers.
2. Lock the brief. Interview only missing decisions. Mark assumptions.
3. Write the visitor journey and feeling curve. One engineered peak.
4. Pick **one** page grammar. [grammars.md](references/grammars.md).
5. Invent one domain-relevant signature interaction with a static fallback.
6. Compare fingerprint if history exists; else record `NO_HISTORY`. Design V2
   retrieval is optional.
7. Assign a device per beat, with fallback. No quota of device families.
8. Build in the project stack. Copy the engine if the page uses `data-sc-*`.
9. Verify along the scroll: desktop, mobile portrait, reduced motion, reverse,
   anchor jump, keyboard. [verification.md](references/verification.md).
10. Fix, save evidence under `.scratch/scroll-craft/<slug>/`, record fingerprint.

`/scroll-craft` with an explicit Continuous World brief: write the story,
waypoints, and feeling curve, then hand off. Do not take the renderer.

## Media

- **Tier 1 (default):** no generation, no video. Complete experience offline.
- **Tier 2:** existing local images with clear license. No ffmpeg.
- **Tier 3:** video only if the brief needs it and native tooling exists.

A finished non-video path is normal, not `DEGRADED`. Use `DEGRADED` only when a
requested capability cannot be met. Do not invent tools.

## Output

The page (or mount into the existing site), the journey table, grammar and why
the others lost, signature move, fingerprint (`NO_HISTORY` or diffs), peak,
verification actually performed, and limits (emulation vs device). Do not dump
prompts or claim uniqueness without evidence.
