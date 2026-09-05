# Mobile, reduced motion, accessibility

## Mobile

A separate composition, not a shrink. Recheck crop, subject, type size, pin
duration, rail behaviour, touch targets, and CTA. Emulated viewport is not a
physical device; say so.

Horizontal rails become a list/grid or stepped controls so every item is
reachable. No horizontal overflow.

## Reduced motion

Required structural fallback, not “less of the same”:

- Previously animated reveals stay visible.
- Rails become list/grid or reachable controls.
- Pinning/parallax/kinetic movement drop or collapse without losing information.
- Comparisons stay usable with alternative controls.
- Nav, focus, CTA, and forms keep working.
- If the runtime listens for preference changes, honor them live.

Engine: under reduced motion, video clips are not fetched; posters and copy
remain. Cues may still fade for comprehension; translation collapses.

## Semantics

Headings, CTA, navigation, and forms are real HTML, never only canvas/video/
image. Logical reading order and heading rank. Alt text matches function.
Focus visible. Keyboard can reach every action. Anchor jumps land on a state
where the target is actually readable (not opacity 0).

Do not hide essential content until a scroll animation runs. JS failure still
leaves the story readable.

Do not claim full accessibility compliance from screenshots alone.

## Contrast and overflow

Check contrast on the composited frame, light-on-dark and dark-on-light.
Fix overflow, sticky collision with chrome, and tap targets on portrait width.
