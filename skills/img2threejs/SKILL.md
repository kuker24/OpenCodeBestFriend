---
name: img2threejs
description: Use when the user wants a code-only procedural Three.js model reconstructed from a reference object image (factory Group, editable primitives, lighting, animation). Not for scroll-led pages (scroll-craft), camera/diorama worlds (scroll-world), HTML-to-MP4 (hyperframes), photoreal/image generation (visual-studio), or product UI (impeccable / found-this-design).
compatibility: opencode
license: MIT
---

# img2threejs

Procedural 3D reconstruction specialist generating clean, editable TypeScript Three.js `Group` factories from a single reference object image.

Unlike downloaded GLTF/OBJ mesh blobs or heavy photogrammetry pipelines, img2threejs creates human-readable, parametric code using Three.js primitives (`BoxGeometry`, `CylinderGeometry`, `ExtrudeGeometry`, shaders/materials, lights).

## Boundaries & Handoffs

| Need | Primary Route |
|---|---|
| Reconstruct isolated object as procedural Three.js code | **`img2threejs`** |
| Continuous 3D fly-through, diorama, camera world landing | `scroll-world` |
| Scroll-driven timeline storytelling website | `scroll-craft` |
| Deterministic HTML composition rendered to MP4 video | `hyperframes` |
| Photoreal product stills, ads, VFX, or raster asset packs | `visual-studio` |
| Web landing page, dashboard, or application UI | `impeccable` / `found-this-design` |

## Progressive Pipeline

1. **Validate Image**: Inspect the reference image. The target must be a discrete object or prop (hardware, furniture, device, vehicle, stylized mascot), not an entire interactive landing page or panoramic scene.
2. **Written Spec (Visible vs. Inferred)**:
   - Identify visible geometry, proportions, materials, colors, and lighting.
   - Explicitly document **inferred hidden faces** (rear, underside, interior). A single viewpoint cannot reveal occluded sides.
   - Propose the hierarchical scene breakdown (`Group` root with named child components).
3. **Factory Pass**:
   - Author a standalone TypeScript module exporting a factory function `createModel(options?): THREE.Group`.
   - Use procedural primitives and standard materials (`MeshStandardMaterial`, `MeshPhysicalMaterial`).
   - Group logically for articulation or animation if requested (pivot points, rotators).
   - No downloaded mesh packs, external `.gltf`/`.obj` URLs, or opaque binary blobs. Output must be diffable TypeScript.
4. **Screenshot Compare & Loop Gate**:
   - Render the procedural model and visually inspect side-by-side with the reference image.
   - Step disposition must be one of:
     - `continue`: Visual parity acceptable; finalize and document inputs.
     - `refine-spec`: Proportions or structural hierarchy wrong; adjust written specification.
     - `refine-code`: Materials, alignments, or primitive parameters off; edit TypeScript.
     - `request-input`: Occluded or ambiguous details require user decision.
     - `stop`: Reached best procedural approximation, or model complexity exceeds procedural primitives.

## Hard Rules & Honesty Gates

1. **Honesty on Occlusion**: Never pretend a single image provides full 360-degree truth. Clearly mark unseen faces as inferred. If the user demands photogrammetric precision that procedural primitives cannot achieve, state "cannot reach requested fidelity" and stop.
2. **Token & Resource Discipline**: Procedural 3D code generation and screenshot verification are token-intensive. Never auto-run on generic website briefs or landing pages.
3. **No Heavy Toolchain**: Output is clean, dependency-light Three.js code. Do not introduce Python mesh reconstruction packages, neural rendering runtimes, or external API dependencies.
