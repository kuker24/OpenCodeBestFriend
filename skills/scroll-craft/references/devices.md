# Devices

Use a device because it serves a beat. There is no minimum family count. Not
every section is pinned. Repeat a family only with a narrative reason.

Every act publishes `--sc-p` (0..1) on its element. Prefer CSS against that
variable before inventing a new device.

Copy `engine/scrollcraft.js` and `engine/scrollcraft.css` into the project.
For a greenfield page, optionally copy `engine/scrollcraft-theme.css` and add
`class="sc-theme"` to the themed root. Existing design systems should keep only
the mechanism CSS and set the `--sc-*` tokens they need. Call
`ScrollCraft.mount(root)` and `instance.destroy()` on teardown/remount.

## Kit

| Device | Visitor's hand does | Notes |
|---|---|---|
| `scrub` | Scrubs a clip or sequence | Tier 3 / local sequence. At most two video scrubs. Clip time ≠ cue time. |
| `pin` | Holds the stage while copy advances | Avoid blank pinned states and dead scroll. |
| `pan` | Travels a horizontal rail | Whole rail must be reachable on mobile and reduced motion (list/grid or controls). |
| `reveal` | Wipe (`up\|down\|left\|right\|iris`) | Keep a static end state. |
| `kinetic` | Lines/words/chars assemble | Reduced motion: show full text, no split animation. |
| `flow` | Document flow + `data-sc-in` | Once-on-entry; do not re-hide on scroll-up. |
| `parallax` | Planes at different rates | Optional. Honor reduced motion (still composition). |
| `count` | Number bloom | **Only factual numbers already available.** |
| `drift` | Ground colour interpolates | Grammar 2 and 7 often forbid this. |

Cues: `data-sc-cue="from to"` with a plateau so copy reaches full opacity.
Pointer devices (`tilt`, `magnet`, `spotlight`) are optional, hover/fine-pointer
only, off under reduced motion, never the only way to get the information.

## Progress contract

- Local progress stays in `0..1`.
- Separate layout reads from style writes. One coordinated rAF, not heavy work
  on every scroll event.
- Skip expensive work offscreen and when the document is hidden.
- Handle resize, orientation, and late-loading assets.
- `destroy()` releases listeners, observers, animation frames, timers, pending
  clip fetches, image callbacks, and Blob URLs. It is idempotent and remountable.
- Support forward, reverse, anchor jump, and mid-page load.
- No global scroll hijack. No network on init (video `fetch` only if a clip is
  present and motion is allowed).

## Dead scroll vs pause

Dead scroll: the wheel turns and nothing meaningful changes. A short held frame
before a peak is a pause, not dead scroll. Do not pad with empty pins.

## Taste that is not law

Do not treat photographic-only worlds, a ban on all scroll cues/counters, or a
punctuation/colour house style as universal. Product context and accessibility
win. Counters still require real numbers. Do not invent statistics.
