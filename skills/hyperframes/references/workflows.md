# HyperFrames Workflow Archetypes

Specialized workflows for common video compositions.

## 1. Product Launch Video
- **Focus:** Sharp product mockups, typography reveals, metric counters, feature highlight zooms.
- **Timeline:**
  - 0-2s: Minimalist typography entrance (product name + one-line thesis).
  - 2-6s: Core UI mockup slide-in with subtle 3D perspective transform (`rotateY`, `scale`).
  - 6-10s: Three key bullet features highlighted sequentially with accent glows.
  - 10-12s: Call-to-action and repository/product URL.

## 2. Animated Explainer / Concept Breakdown
- **Focus:** Diagrams, node graphs, data movement along SVG paths, sequence steps.
- **Visuals:** Use SVG path dashoffset animations indexed to frame time:
  ```css
  stroke-dashoffset: calc(var(--path-length) * (1 - var(--progress)));
  ```
- Clear visual contrast between active components and background topology.

## 3. Motion Graphics & Metric Showcases
- **Focus:** Animated bar charts, line graphs plotting across time, animated counters.
- **Interpolation:** Easing functions (cubic-bezier) calculated in JavaScript or CSS custom properties mapped to `--frame-time`.

## 4. Slideshow / Teaser
- **Focus:** Clean card transitions, kinetic typography, subtle ken burns effect on local background imagery.
