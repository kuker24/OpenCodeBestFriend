# Handoff

One owner per phase. Handoff is sequential, not loading every specialist.

## Continuous World

When the grammar is Continuous World (explicit `/scroll-craft` plus camera
flight, or a brief that is literally one unbroken journey through a place):

1. Stay in Scroll Craft long enough to write story, waypoints, feeling curve,
   peak, and creative direction into `.scratch/scroll-craft/<slug>/`.
2. Load `scroll-world` and stop implementing the world here.
3. Do not copy worldflight markup, chain pipeline, or video stitching.
4. Do not assume video is required; follow Scroll World's contract.

Without an explicit slash, a continuous camera / diorama / 3D-world request
routes to `scroll-world` even if the user said “scroll”.

## Other owners

| After | Then |
|---|---|
| Surface exists; chrome easing still wrong | `emil-design-eng` |
| Need standalone photoreal/video assets | `visual-studio`, then return to this page context |
| Exploratory QA | `browser-act` |
| Observed browser bug | CDP helper + `chrome-devtools-axi` |
| Auth/secrets/public API in the page | existing `full-audit-keamanan` trigger only |

Do not bounce the request in a loop. Record owner, why, what is carried, what
is handed off, and the done condition.

## Media return path

Asset production is not automatic circular routing. When assets land, resume
from the saved brief, not a new specialist pile.

## Design V2

Internal optional retrieval, never a second specialist.
