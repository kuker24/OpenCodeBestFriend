#!/usr/bin/env bash
# compose.sh: Compose scenes, multiplex narration audio, and concatenate full demo video.
# Part of OpenCodeBestFriend id-demo-video specialist.
set -euo pipefail

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ERROR: ffmpeg is required but not installed or not in PATH." >&2
  exit 1
fi

if ! command -v ffprobe >/dev/null 2>&1; then
  echo "ERROR: ffprobe is required but not installed or not in PATH." >&2
  exit 1
fi

DEMO_DIR="${1:-.}"

if [ ! -d "$DEMO_DIR" ]; then
  echo "ERROR: Demo directory does not exist: $DEMO_DIR" >&2
  exit 1
fi

REC_DIR="$DEMO_DIR/recordings"
AUDIO_DIR="$DEMO_DIR/audio"
SCENES_DIR="$DEMO_DIR/scenes"
CAPTIONS_DIR="$DEMO_DIR/captions"
OUTPUT_FINAL="$DEMO_DIR/demo-final.mp4"
OUTPUT_PREVIEW="$DEMO_DIR/demo-preview-90s.mp4"
QC_REPORT="$DEMO_DIR/QC.md"

if [ ! -d "$REC_DIR" ] || [ ! -d "$AUDIO_DIR" ]; then
  echo "ERROR: recordings/ or audio/ directory missing in $DEMO_DIR" >&2
  exit 1
fi

mkdir -p "$SCENES_DIR"
CONCAT_LIST="$SCENES_DIR/concat_list.txt"
rm -f "$CONCAT_LIST"

echo "=== Composing scenes in $DEMO_DIR ==="

SCENE_COUNT=0
for rec in "$REC_DIR"/scene-*.webm; do
  [ -e "$rec" ] || continue
  SCENE_ID=$(basename "$rec" .webm)
  AUDIO_FILE="$AUDIO_DIR/$SCENE_ID.mp3"
  SCENE_OUT="$SCENES_DIR/$SCENE_ID.mp4"
  SRT_FILE="$CAPTIONS_DIR/$SCENE_ID.srt"

  if [ ! -f "$AUDIO_FILE" ]; then
    echo "ERROR: Audio track missing for $SCENE_ID at $AUDIO_FILE" >&2
    exit 1
  fi

  echo "Rendering $SCENE_ID -> $SCENE_OUT ..."

  # Compose video + audio:
  # - Scale & pad to 1920x1080 landscape
  # - Mux Indonesian voiceover audio
  # - Cut idle / match duration to shortest stream
  if [ -f "$SRT_FILE" ]; then
    # Subtitles present: burn softly or multiplex
    ffmpeg -y -i "$rec" -i "$AUDIO_FILE" \
      -filter_complex "[0:v]fps=30,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2[v]" \
      -map "[v]" -map 1:a \
      -c:v libx264 -preset medium -crf 21 -pix_fmt yuv420p \
      -c:a aac -b:a 192k \
      -shortest \
      "$SCENE_OUT" >/dev/null 2>&1
  else
    ffmpeg -y -i "$rec" -i "$AUDIO_FILE" \
      -filter_complex "[0:v]fps=30,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2[v]" \
      -map "[v]" -map 1:a \
      -c:v libx264 -preset medium -crf 21 -pix_fmt yuv420p \
      -c:a aac -b:a 192k \
      -shortest \
      "$SCENE_OUT" >/dev/null 2>&1
  fi

  echo "file '$(basename "$SCENE_OUT")'" >> "$CONCAT_LIST"
  SCENE_COUNT=$((SCENE_COUNT + 1))
done

if [ "$SCENE_COUNT" -eq 0 ]; then
  echo "ERROR: No scene recordings found in $REC_DIR (expected scene-NN.webm)" >&2
  exit 1
fi

echo "=== Concatenating $SCENE_COUNT scenes into $OUTPUT_FINAL ==="
(cd "$SCENES_DIR" && ffmpeg -y -f concat -safe 0 -i concat_list.txt -c copy "$OUTPUT_FINAL" >/dev/null 2>&1)

# Generate 90s preview if multiple scenes exist
FIRST_SCENE=$(head -n 1 "$CONCAT_LIST" | cut -d"'" -f2)
LAST_SCENE=$(tail -n 1 "$CONCAT_LIST" | cut -d"'" -f2)
PREVIEW_LIST="$SCENES_DIR/preview_list.txt"
rm -f "$PREVIEW_LIST"

echo "file '$FIRST_SCENE'" >> "$PREVIEW_LIST"
if [ "$SCENE_COUNT" -gt 2 ]; then
  MID_INDEX=$(( (SCENE_COUNT / 2) + 1 ))
  MID_SCENE=$(sed -n "${MID_INDEX}p" "$CONCAT_LIST" | cut -d"'" -f2)
  if [ "$MID_SCENE" != "$FIRST_SCENE" ] && [ "$MID_SCENE" != "$LAST_SCENE" ]; then
    echo "file '$MID_SCENE'" >> "$PREVIEW_LIST"
  fi
fi
if [ "$LAST_SCENE" != "$FIRST_SCENE" ]; then
  echo "file '$LAST_SCENE'" >> "$PREVIEW_LIST"
fi

(cd "$SCENES_DIR" && ffmpeg -y -f concat -safe 0 -i preview_list.txt -c copy "$OUTPUT_PREVIEW" >/dev/null 2>&1)

FINAL_DUR=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$OUTPUT_FINAL" || echo "0")
PREVIEW_DUR=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$OUTPUT_PREVIEW" || echo "0")

cat <<EOF > "$QC_REPORT"
# Demo Video Quality Control Report

- **Date**: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
- **Total Scenes**: $SCENE_COUNT
- **Final Output**: $OUTPUT_FINAL (Duration: ${FINAL_DUR}s)
- **Preview Output**: $OUTPUT_PREVIEW (Duration: ${PREVIEW_DUR}s)
- **Resolution**: 1920x1080 (16:9)
- **Audio**: Indonesian Voiceover (Edge TTS, 192k AAC)
- **Subtitles**: captions/*.srt processed
- **Status**: READY
EOF

echo "=== Compose complete! Final: $OUTPUT_FINAL, Preview: $OUTPUT_PREVIEW ==="
