# HyperFrames Workflow Archetypes

Comprehensive workflows for deterministic HTML-to-MP4 video compositions.

## 1. Product Launch & Feature Highlight
- **Objective:** Reveal a new tool, feature, or service with dynamic UI mockups, metric counters, and typography punch.
- **Scene Breakdown:**
  - `Scene 1 (0-3s)`: Impactful title card with animated brand wordmark and subtitle.
  - `Scene 2 (3-7s)`: UI window container slides in with 3D perspective rotation (`perspective(1000px) rotateX(4deg)`).
  - `Scene 3 (7-12s)`: Sequential highlight boxes pop onto key UI controls with accent borders.
  - `Scene 4 (12-15s)`: Call-to-action lockup with repository command (`npm i ...`) and documentation link.

## 2. Technical Explainer & Architecture Walkthrough
- **Objective:** Explain a distributed system, protocol handshake, or complex data flow with animated SVG graphs.
- **Techniques:**
  - **Packet Travel:** Animate a circle or packet indicator along an SVG path using `stroke-dashoffset` or `path.getPointAtLength(t * len)`.
  - **Component Focus:** Dim inactive subsystems with `opacity: 0.3` while highlighting the active node with an animated pulse ring.
  - **Step Annotations:** Accompanying lower-third text cards that update in lockstep with packet transitions.

## 3. Pull Request / Code Walkthrough (`pr-to-video`)
- **Objective:** Convert a pull request diff or major refactor into an animated video walkthrough.
- **Techniques:**
  - **Terminal Typing:** Monospace terminal component simulating command invocation (`git diff`, `pytest`).
  - **Diff Highlighting:** Green additions (`+`) and red deletions (`-`) sliding into place sequentially with line numbers.
  - **Architecture Seam:** Split-screen showing code diff on the left and resulting architecture change diagram on the right.

## 4. Motion Graphics & Metric Showcases
- **Objective:** Display performance benchmarks, telemetry stats, or business growth.
- **Techniques:**
  - **Count-Up Numbers:** Eased numeric counter interpolating from `0` to target value using `Math.round(progress * target)`.
  - **Bar Chart Race / Growth:** CSS height transitions with spring or power2 easing curves.
  - **Radial Progress Rings:** SVG `stroke-dasharray` circle circumference fills.

## 5. Beat-Synced Video & Audio Transitions
- **Objective:** Align visual cuts and scene changes with an underlying audio track or sound effects.
- **Techniques:**
  - **Beat Grid:** Define timestamps array in milliseconds: `const BEATS = [0.0, 1.25, 2.50, 3.75, 5.0];`.
  - **Impact Frames:** Single-frame color flash (white background overlay for 0.05s) on major beat timestamps.
  - **Camera Shake:** Transient CSS translation matrix jitter for 2-3 frames following a heavy bass drop or impact point.

## 6. Captions & Lower-Thirds Overlay
- **Objective:** Add burned-in accessible captions or speaker identifying lower-thirds.
- **Techniques:**
  - **Word-Level Highlighting:** Karaoke-style text reveal where current spoken words highlight in accent color.
  - **Pill Badges:** Subdued semi-transparent dark pill background (`rgba(0,0,0,0.7)`) with high-contrast text (`#ffffff`).
  - **Safe Zones:** Keep all lower-thirds and captions at least 96px above bottom screen edge to avoid mobile player UI collision.
