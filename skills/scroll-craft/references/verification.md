# Verification along the scroll

Use the OCBF browser contract. Do not install `playwright-core`, launch Google
Chrome, or use `chrome-direct`.

- Exploratory QA: load `browser-act`, then run it.
- Observed cause: `opencode-chromium-cdp start` on `127.0.0.1:9223`, then
  `chrome-devtools-axi`.
- Project Playwright only if the project already has it.

If browser tooling is missing, finish every other job and record the blocked
checks. Do not fake screenshots or treat static tests as QA. Do not weaken a
required gate to claim done.

## Sampling

For each moving act: opening, at least four in-between positions, ending.
Add samples just before/after act boundaries and the signature state. Use
**act progress**, not only whole-page percent.

Repeat on desktop, mobile portrait, reduced motion, reverse scroll, and anchor
jump. Record actual viewport size.

## Hunt

Dead scroll, frozen stage, blank pin, cues that never reach full opacity,
overlap, hard seams, failed assets, console errors, horizontal overflow, weak
contrast, unreachable rail/CTA.

Wait for a stable DOM/CSS state. If video is in play (tier 3), wait for the
target frame after seek with a real timeout — timeout fails that mode. Do not
screenshot after a fixed sleep and claim the playhead.

## Evidence

Save under `.scratch/scroll-craft/<slug>/` in the user project: fixture, viewport,
motion mode, act/progress, result, fixes. Look at the images. Screenshots do not
prove smooth motion; test real interaction and report limits.

Preflight matches the chosen tier: HTML/CSS needs no ffmpeg; layered images need
no video stack; a media provider is never a general requirement.
