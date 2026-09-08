# Diagram Accessibility & Visual Ergonomics

Standards for accessible and legible technical diagrams.

## Color & Contrast

- **WCAG 2.1 AA Compliance:** Minimum 4.5:1 contrast ratio for all text against card fills. Minimum 3:1 contrast for graphical borders and directional arrows.
- **Do not rely solely on color:** Distinguish statuses or boundaries using stroke styles (dashed vs. solid), icons, or explicit badge labels (`[Active]`, `[Deprecated]`, `[External]`).
- **Dark & Light Mode Harmony:** Use CSS variables for canvas background, card background, border, and text so the diagram renders legibly in any theme.

## SVG Semantic Markup

- Root `<svg>` must include `role="img"` and an `<aria-labelledby>` reference.
- Include a descriptive `<title>` and `<desc>` element inside the `<svg>`:
  ```xml
  <svg role="img" aria-labelledby="diagram-title diagram-desc" viewBox="0 0 1200 800">
    <title id="diagram-title">System Architecture Overview</title>
    <desc id="diagram-desc">Microservices topology showing Auth, Payment, and Order services connected via gRPC.</desc>
    <!-- graphical elements -->
  </svg>
  ```

## Responsive Viewport

- Always declare `viewBox="0 0 W H"` and omit fixed `width` and `height` attributes on the root `<svg>` tag, controlling sizing via container CSS (`width: 100%; max-width: 1200px; height: auto;`).
