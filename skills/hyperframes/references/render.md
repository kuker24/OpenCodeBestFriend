# HyperFrames Rendering Pipeline

Capturing frames from Headless Chromium and encoding with FFmpeg.

## Local Prerequisites

Check local system capabilities:
```bash
which ffmpeg
which google-chrome || which chromium || which chromium-browser
```
If missing: report `NOT_CONFIGURED`.

## Frame Stepping Protocol

Chromium DevTools Protocol (CDP) `Page.captureScreenshot` or Puppeteer / Playwright script steps through each frame:

```bash
# Example frame stepping parameter calculation:
FPS=30
DURATION_SECONDS=10
TOTAL_FRAMES=$((FPS * DURATION_SECONDS))
```

## Canonical FFmpeg Encoding

After PNG frames are saved to a directory (e.g. `./frames/frame_%05d.png`):

```bash
# High quality H.264 MP4 encode:
ffmpeg -y -framerate 30 -i frames/frame_%05d.png \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p \
  output.mp4

# With audio multiplexing:
ffmpeg -y -framerate 30 -i frames/frame_%05d.png -i audio.mp3 \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -shortest \
  output.mp4
```

## Quality Optimization
- Use `-pix_fmt yuv420p` for universal hardware/browser playback.
- Use `-crf 18` for visually lossless composition.
- If alpha transparency is required (WebM overlay):
  `ffmpeg -y -framerate 30 -i frames/frame_%05d.png -c:v libvpx-vp9 -pix_fmt yuva420p output.webm`
