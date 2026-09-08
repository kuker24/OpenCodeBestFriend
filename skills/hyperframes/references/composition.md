# HyperFrames Composition Architecture

HTML, CSS, and Canvas structure for seekable video scenes.

## The Seekable Timeline Contract

Deterministic frame capture requires that any frame at time `t` (or frame index `n` at FPS `r`) can be rendered instantaneously without continuous wall-clock playback.

```javascript
// Canonical seek interface
window.renderFrame = function(timeInSeconds, frameNumber) {
  // Update state, CSS variables, or canvas draw calls for exact timestamp
  document.documentElement.style.setProperty('--frame-time', `${timeInSeconds}s`);
  // Update canvas or SVG elements directly
  updateScene(timeInSeconds);
};
```

## Viewport & Aspect Ratio Presets

Configure root container to exact pixel dimensions:

- **16:9 Landscape (YouTube / Presentation):** `width: 1920px; height: 1080px;`
- **9:16 Vertical (Reels / TikTok / Shorts):** `width: 1080px; height: 1920px;`
- **1:1 Square (Feed):** `width: 1080px; height: 1080px;`

CSS resets:
```css
html, body {
  margin: 0;
  padding: 0;
  overflow: hidden;
  background: #000;
  -webkit-font-smoothing: antialiased;
}
#stage {
  position: relative;
  width: 1920px;
  height: 1080px;
  overflow: hidden;
}
```

## Scene Management

Divide longer videos into discrete scenes:
- `Scene 1 [0.0s - 3.5s]`: Hook & Title Card
- `Scene 2 [3.5s - 8.0s]`: Problem Statement / Key Graphic
- `Scene 3 [8.0s - 14.0s]`: Feature Demonstration / Architecture Callout
- `Scene 4 [14.0s - 17.0s]`: Outro / Call to Action
