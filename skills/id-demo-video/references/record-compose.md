# Recording & Video Composition (`record-compose.md`)

Browser capture parameters, silence trimming, subtitle burning, and FFmpeg concatenation.

## Browser Recording Standards

1. **Resolution & Viewport**: Fixed 1920x1080 landscape (`16:9`).
2. **Cursor Visibility**: Ensure mouse cursor is visible during browser interactions.
3. **Typing Cadence**: Use human-cadence delay (`delay: 40-75ms` per character) instead of instant value assignment so keystrokes appear on video.
4. **Isolated Profile**: Use an isolated browser context. Never attach to personal Google Chrome profiles.
5. **Port Safety & Process Isolation**: Launch a separate, dedicated Chromium process with an isolated temporary user-data-dir. Do not connect or bind to port 9223 (which is reserved for `chrome-devtools-axi` QA sessions); never hijack or attach to an existing QA browser.
6. **Pre-flight App Check**:
   - Query target URL before starting recording (e.g. `curl -s -o /dev/null -w "%{http_code}" http://localhost:3000`).
   - If connection fails: abort immediately.
   - Output message: *"Aplikasi belum berjalan di <URL>. Jalankan server aplikasi terlebih dahulu (misal: npm run dev atau python app.py) sebelum merekam demo."*
   - Never generate placeholder/color screens when the app is offline.

## Scene Composition Protocol

Each scene is processed independently before global concatenation:

```bash
# 1. Trim leading/trailing browser initialization latency and idle gaps (>1.2s)
# 2. Multiplex audio track (audio/scene-NN.mp3) with video (recordings/scene-NN.webm)
# 3. Burn subtitles from captions/scene-NN.srt (optional or embedded soft subs)
ffmpeg -y -i recordings/scene-NN.webm -i audio/scene-NN.mp3 \
  -filter_complex "[0:v]fps=30,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2[v]" \
  -map "[v]" -map 1:a \
  -c:v libx264 -preset medium -crf 21 -pix_fmt yuv420p \
  -c:a aac -b:a 192k \
  -shortest \
  scenes/scene-NN.mp4
```

## Global Concatenation (`demo-final.mp4`)

Using FFmpeg concat demuxer:

```text
# concat_list.txt
file 'scenes/scene-01.mp4'
file 'scenes/scene-02.mp4'
file 'scenes/scene-03.mp4'
...
```

```bash
ffmpeg -y -f concat -safe 0 -i concat_list.txt -c copy demo-final.mp4
```

## Short Preview Generation (`demo-preview-90s.mp4`)

Always export a 90-second executive summary alongside the final video:
- Scene 1 (Hook / Intro): ~25 seconds
- Scene 3 or 4 (Core differentiator feature): ~45 seconds
- Final Scene (Outro / Result): ~20 seconds

## Subtitle Guidelines (SRT)

- Maximum 2 lines per subtitle card.
- Maximum 38 characters per line.
- Font styling: Sans-serif (Inter / Roboto), white text with subtle black outline or semi-transparent background box.

## Background Music (BGM) Policy

- **Default**: Disabled (No background music).
- **User Music**: Only allowed if the user explicitly supplies a local audio file (e.g. `demos/<slug>/bgm.mp3`).
- **Volume**: If BGM is enabled, sidechain ducking or static volume at `-22dB` to prevent masking spoken narration.
