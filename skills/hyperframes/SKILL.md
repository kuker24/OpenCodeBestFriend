---
name: hyperframes
description: Deterministic video composition from HTML, CSS, and seekable animations rendered to MP4 via headless Chrome and FFmpeg. Use for programmatic video creation, motion graphics, animated explainers, and HTML-to-video rendering. Not for photoreal/cinematic media (visual-studio), UI interaction feel (emil-design-eng), scroll-led storytelling (scroll-craft), or 3D camera worlds (scroll-world).
compatibility: opencode
license: Apache-2.0
---

# HyperFrames

Production specialist for **deterministic HTML-to-video composition**.

Unlike generative video models that hallucinate frames, HyperFrames builds videos as web documents: HTML for structure, CSS and Canvas/SVG for visuals, and seekable time-driven animation. Headless Chrome steps through the timeline deterministically while FFmpeg encodes each frame into crisp, reproducible MP4 video.

## Handoff & Boundaries

| Request | Primary Route |
|---|---|
| Photoreal product stills, UGC ads, cinematic VFX, identity packs | `visual-studio` |
| In-app micro-interactions, hover/press, easing on interactive UI | `emil-design-eng` (after `impeccable`) |
| Scroll-driven narrative storytelling website (scrollytelling) | `scroll-craft` |
| Continuous 3D fly-through, camera-scrub diorama page | `scroll-world` |
| **Deterministic HTML composition rendered to video** | **`hyperframes`** |

## Environment & Availability

HyperFrames executes locally:
1. **Local CLI:** `npx hyperframes` or local project rendering script.
2. **Runtime Prerequisites:** Headless Chromium/Chrome and FFmpeg.

If local rendering tools or FFmpeg are absent:
- Mark execution as `NOT_CONFIGURED` or `DEGRADED`.
- Output the self-contained HTML/CSS composition files and precise rendering CLI commands.
- **Never** make silent remote HeyGen API calls or request confidential API keys. Hosted services remain opt-in only.

## References

Load the specific reference required for the task:

- [references/composition.md](references/composition.md) — HTML composition layout, aspect ratios, seekable timeline contracts.
- [references/render.md](references/render.md) — Headless Chrome capture, frame stepping, FFmpeg encoding parameters.
- [references/workflows.md](references/workflows.md) — Workflow archetypes (product launch, animated explainer, motion graphics, data video).

## Hard Rules

1. **Deterministic Timelines:** Animations must be scrubbable/seekable by a master time parameter (`t` in seconds or frame number `f`). Avoid non-deterministic `Math.random()` or real-time `setInterval` that drifts during frame capture.
2. **Exact Dimensions:** Explicitly set viewport and canvas dimensions matching standard video resolutions (e.g. 1920x1080 for 16:9 landscape, 1080x1920 for 9:16 vertical/shorts).
3. **Local Assets First:** Prefer SVG, Canvas, embedded fonts, and local images over external CDN links to guarantee offline reproducibility.
4. **Clean Handoff:** If audio tracks (voiceover, BGM) are provided, synchronize cue points in the timeline and multiplex audio during the FFmpeg pass.
