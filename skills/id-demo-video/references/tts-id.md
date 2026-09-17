# Indonesian Text-to-Speech Engine (`tts-id.md`)

Voice synthesis specifications, voice selection, caching, and rate limiting rules for Indonesian demo narration.

## Voice Engines & Priority

### 1. Default (Free / Rp0): Edge TTS
- **Engine**: Microsoft Edge Neural TTS via `edge-tts` Python library.
- **Voices**:
  - `id-ID-GadisNeural` (Female, natural warm tone, default)
  - `id-ID-ArdiNeural` (Male, authoritative presenter tone)
- **Voice Rate**: Default `+0%` (natural 130–150 wpm). Use `+5%` or `-5%` to fine-tune scene timings.
- **Pitch**: Default `+0Hz`.

### 2. Forbidden Engine: Kokoro
- Kokoro models currently do not have native Indonesian phoneme support. Kokoro is strictly prohibited for Indonesian narration as it mangles pronunciation.

### 3. Optional Engine: ElevenLabs (Strictly OFF by default)
- **Status**: OFF by default.
- **Activation**: Requires explicit user instruction and user-provided API key.
- **Mandatory User Warning**: Before synthesizing via ElevenLabs, warn the user:
  > *"Peringatan kuota: Paket gratis ElevenLabs dibatasi ~10.000 kredit/bulan (sekitar 8–10 menit audio total) dan memiliki batasan lisensi non-komersial. Default sistem adalah Edge TTS (gratis, tanpa kuota)."*

## Content-Addressed Caching

To avoid re-synthesizing identical text across test runs and edits:
1. Compute SHA-256 hash over normalized input: `hash = sha256(text.strip() + "|" + voice + "|" + rate)`.
2. Save cache in `demos/<slug>/.cache/tts/<hash>.mp3`.
3. If `<hash>.mp3` exists and file size > 0, copy from cache instead of issuing network calls.

## Rate Limiting & 429 Handling

1. **Exponential Backoff**: If Edge TTS returns HTTP 429 (Too Many Requests), wait:
   - Attempt 1: wait 2 seconds
   - Attempt 2: wait 5 seconds
   - Attempt 3: wait 10 seconds
2. **Never Silent Failover**: Never silently route traffic to paid cloud APIs or fall back to robotic TTS without user knowledge.
3. **Graceful Failure**: If retries fail, exit with code 429 and inform the user to pause before re-running.

## Duration Measurement (`ffprobe`)

Before screen recording begins, each generated MP3 must be measured:
```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 audio/scene-NN.mp3
```
This measured audio duration defines the required screen capture duration (+1.0 to 1.5 seconds tail padding) for that scene.
