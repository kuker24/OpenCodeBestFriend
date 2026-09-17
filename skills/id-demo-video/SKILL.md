---
name: id-demo-video
description: Use when the user wants an application demo video, product walkthrough recording, lomba/contest demo, Indonesian voiceover for a screen demo, or a ~10 minute narrated app tour. Orchestrates beat sheet, Indonesian narration, Edge TTS, Playwright/Chromium scene capture, ffmpeg concat, optional HyperFrames title cards. Not for functional browser QA (playwright-qa), UI motion inside the product (emil-design-eng), still/ad art (visual-studio), file+line developer tours (code-tour), or a single HTML composition standing in for a 10 minute video (hyperframes handles title/end cards only).
compatibility: opencode
license: MIT
---

# Indonesian Application Demo Video (`id-demo-video`)

Director and orchestrator for multi-scene application walkthrough videos with natural Indonesian narration, screen recording, synchronized subtitles, and zero-cost local tooling.

## Boundaries & Handoffs

| Request / Requirement | Primary Specialist |
|---|---|
| Functional browser QA, regression assertions, testing form flows | `playwright-qa` |
| In-app UI micro-interactions, CSS transitions, easing curves | `emil-design-eng` (after `impeccable`) |
| Photoreal product stills, marketing ad creative packs, non-UI surfaces | `visual-studio` |
| Developer onboarding and interactive CodeTour `.tour` file walkthroughs | `code-tour` |
| Deterministic HTML title cards, lower-thirds, or short (<90s) motion cards | `hyperframes` (handoff for intro/outro cards) |
| **Full application demo video, screen walkthrough, and Indonesian narration** | **`id-demo-video`** |

## Core Architecture & Fences

1. **Pipeline Director**: `id-demo-video` coordinates the demo creation pipeline. It is not an image generator or a single-composition renderer.
2. **HyperFrames Boundary**: HyperFrames handles short HTML-to-MP4 title/end cards (sweet spot 30–90s). Never attempt a single 600s monolithic HTML composition for a 10-minute demo.
3. **Free & Local Default (Rp0)**: Edge TTS with voices `id-ID-GadisNeural` (female) or `id-ID-ArdiNeural` (male). No paid API keys required. Kokoro is prohibited for Indonesian text. ElevenLabs is strictly OFF by default (if explicitly turned on by user, warn about ~10k free credit limits and non-commercial restrictions).
4. **App Availability Gate**: If the target application cannot be contacted, fail immediately and instruct the user to run the app start command. Never render a fake dummy screen or blank placeholder video.
5. **Session & Browser Rules**: Record by launching a dedicated, standalone Playwright Chromium process with an isolated profile. Never bind to personal Google Chrome profiles. Do not connect to or interfere with port 9223 (reserved for `chrome-devtools-axi` QA sessions; recording must run its own independent browser process).
6. **No Secrets on Screen**: Only seed and demo data may be typed or displayed. Mask or clear all private keys, passwords, and tokens.

## Ten-Minute Demo Rules

- **Modular Scene Architecture**: Split a ~10-minute (600s) target into 8–12 discrete scenes (40–90 seconds each). One continuous 10-minute take is strictly prohibited.
- **Pacing & Cadence**: Speaking rate is 130–150 words per minute. A 10-minute video contains ~1,300–1,500 spoken words.
- **Natural Spoken Indonesian**: Write conversational Indonesian with short sentences (8–16 words).
- **Anti-Slop Buzzword Prohibition**: Do not use empty corporate jargon:
  - Banned terms: *"era digital"*, *"solusi inovatif"*, *"memanfaatkan AI"*, *"seamless"*, *"cutting-edge"*, *"game changer"*.
  - Focus on what the user does, what appears on screen, and why it matters.

## Artifact Contract

All demo assets reside in the project's `demos/<slug>/` directory (must be gitignored):

```text
demos/<slug>/
  brief.md                  # Scope, URL, feature checklist, target duration
  beats.md                  # Timed scene outline (total seconds = target ±15s)
  naskah.md                 # Per-scene spoken Indonesian voiceover script
  storyboard.json           # Machine-executable scene actions & audio mapping
  audio/scene-NN.mp3        # Synthesized voiceover per scene (content-cached)
  recordings/scene-NN.webm  # Raw Playwright screen capture per scene
  captions/scene-NN.srt     # Synchronized Indonesian subtitle per scene
  scenes/scene-NN.mp4       # Composed per-scene video (audio + video + subs)
  demo-preview-90s.mp4      # 90-second executive cut (intro + core + outro)
  demo-final.mp4            # Full concatenated walkthrough
  QC.md                     # Quality checklist and duration report
```

## Nine-Step Execution Pipeline

1. **Brief**: Extract app purpose, target audience, local URL (e.g. `http://localhost:3000`), and mandatory features from repo files or user prompt into `brief.md`.
2. **Beat Sheet**: Design timed scene beats in `beats.md`. Ensure `sum(scene_durations) == target_duration ± 15s`. Consult [references/beats.md](references/beats.md).
3. **Naskah Indonesia**: Write natural spoken Indonesian voiceover per scene in `naskah.md` (130–150 wpm, 8–16 words/sentence).
4. **Storyboard**: Structure actions into `storyboard.json`. Consult [references/storyboard.schema.md](references/storyboard.schema.md).
5. **Edge TTS Synthesis**: Run `python3 scripts/tts_edge.py` to synthesize `audio/scene-NN.mp3` with content-hashing. Measure exact audio duration with `ffprobe` before recording. Consult [references/tts-id.md](references/tts-id.md).
6. **Scene Recording**: Drive browser via Playwright CLI with 1920x1080 viewport, visible cursor, and human typing cadence. Capture raw video into `recordings/scene-NN.webm`. Consult [references/record-compose.md](references/record-compose.md).
7. **Subtitle Generation**: Generate synchronized Indonesian subtitles (`captions/scene-NN.srt`) matching speech segments.
8. **Compose & Concat**: Run `scripts/compose.sh` to trim idle gaps (>1.2s), mux audio, burn subtitles, and concatenate scenes into `demo-final.mp4`.
9. **Preview & QC**: Generate `demo-preview-90s.mp4` containing representative scenes and record verification results in `QC.md`.

## Runtime Prerequisites

Verify environment tools before running scripts:
```bash
ffmpeg -version >/dev/null 2>&1 || { echo "MISSING: ffmpeg"; exit 1; }
ffprobe -version >/dev/null 2>&1 || { echo "MISSING: ffprobe"; exit 1; }
python3 -c "import edge_tts" >/dev/null 2>&1 || { echo "MISSING: edge-tts (install via: pip install edge-tts)"; exit 1; }
```
