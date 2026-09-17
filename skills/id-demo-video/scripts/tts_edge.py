#!/usr/bin/env python3
"""
Edge TTS synthesis wrapper with content caching and 429 backoff for Indonesian narration.
Part of OpenCodeBestFriend id-demo-video specialist.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import shutil
import sys
import time
from pathlib import Path

ALLOWED_VOICES = {
    "id-ID-GadisNeural": "Female Indonesian warm natural tone",
    "id-ID-ArdiNeural": "Male Indonesian authoritative tone",
}


def compute_content_hash(text: str, voice: str, rate: str) -> str:
    norm = text.strip()
    raw = f"{norm}|{voice}|{rate}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


async def synthesize(text: str, voice: str, rate: str, output_path: Path, max_retries: int = 3) -> None:
    try:
        import edge_tts  # type: ignore
    except ImportError:
        sys.stderr.write("ERROR: 'edge-tts' library is not installed. Install via: pip install edge-tts\n")
        sys.exit(1)

    delays = [2, 5, 10]
    for attempt in range(max_retries):
        try:
            communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
            await communicate.save(str(output_path))
            return
        except Exception as exc:
            err_msg = str(exc)
            if "429" in err_msg or "Too Many Requests" in err_msg:
                wait_sec = delays[attempt] if attempt < len(delays) else 10
                sys.stderr.write(f"WARNING: Rate limited (429). Retrying in {wait_sec}s (attempt {attempt + 1}/{max_retries})...\n")
                await asyncio.sleep(wait_sec)
            else:
                sys.stderr.write(f"ERROR: Edge TTS synthesis failed: {exc}\n")
                sys.exit(1)

    sys.stderr.write("ERROR: Edge TTS failed after retries due to rate limiting (429).\n")
    sys.exit(42)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Synthesize Indonesian voiceover using Edge TTS with content caching.")
    parser.add_argument("--text", type=str, help="Text to synthesize")
    parser.add_argument("--text-file", type=Path, help="Path to text file containing narration")
    parser.add_argument("--output", type=Path, required=True, help="Path to output MP3 file")
    parser.add_argument("--voice", type=str, default="id-ID-GadisNeural", choices=list(ALLOWED_VOICES.keys()), help="Voice name")
    parser.add_argument("--rate", type=str, default="+0%", help="Speed rate modifier (e.g. +0%%, +5%%, -5%%)")
    parser.add_argument("--cache-dir", type=Path, default=None, help="Directory to store and check audio cache")
    parser.add_argument("--dry-run", action="store_true", help="Validate input and exit without network synthesis")

    args = parser.parse_args(argv)

    # 1. Resolve text input
    text = ""
    if args.text:
        text = args.text
    elif args.text_file:
        if not args.text_file.is_file():
            sys.stderr.write(f"ERROR: Text file not found: {args.text_file}\n")
            return 1
        text = args.text_file.read_text(encoding="utf-8")
    elif not sys.stdin.isatty():
        text = sys.stdin.read()

    text = text.strip()
    if not text:
        sys.stderr.write("ERROR: Input narration text is empty.\n")
        return 1

    # 2. Validate voice
    if args.voice not in ALLOWED_VOICES:
        sys.stderr.write(f"ERROR: Unsupported voice '{args.voice}'. Allowed Indonesian voices: {', '.join(ALLOWED_VOICES.keys())}\n")
        return 1

    # 3. Cache lookup
    cache_key = compute_content_hash(text, args.voice, args.rate)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    if args.cache_dir:
        args.cache_dir.mkdir(parents=True, exist_ok=True)
        cached_file = args.cache_dir / f"{cache_key}.mp3"
        if cached_file.is_file() and cached_file.stat().st_size > 0:
            shutil.copy2(cached_file, args.output)
            sys.stdout.write(f"[CACHE HIT] {args.output.name} (hash: {cache_key[:12]})\n")
            return 0

    # 4. Dry-run mode
    if args.dry_run:
        # Create a 0-byte or placeholder file for verification if requested
        args.output.write_bytes(b"")
        sys.stdout.write(f"[DRY-RUN VALID] Text length: {len(text)} chars, voice: {args.voice}, key: {cache_key[:12]}\n")
        return 0

    # 5. Synthesize via network
    asyncio.run(synthesize(text, args.voice, args.rate, args.output))

    # 6. Cache write-back
    if args.cache_dir:
        cached_file = args.cache_dir / f"{cache_key}.mp3"
        shutil.copy2(args.output, cached_file)

    sys.stdout.write(f"[SYNTHESIZED] {args.output} (hash: {cache_key[:12]})\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
