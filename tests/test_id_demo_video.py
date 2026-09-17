#!/usr/bin/env python3
"""
Tests for Indonesian application demo video specialist (id-demo-video and /demo-video).
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate_storyboard_duration(data: dict) -> tuple[bool, str]:
    target = data.get("target_duration_s", 0)
    scenes = data.get("scenes", [])
    total = sum(s.get("duration_s", 0) for s in scenes)
    diff = abs(total - target)
    if diff > 15:
        return False, f"Sum of scene durations ({total}s) differs from target ({target}s) by {diff}s (tolerance: ±15s)"
    return True, f"OK ({total}s vs target {target}s, diff {diff}s)"


class IdDemoVideoContractTests(unittest.TestCase):
    def setUp(self):
        self.agents = (ROOT / "templates" / "AGENTS.md").read_text(encoding="utf-8")
        self.routing = (ROOT / "rules" / "00-routing.md").read_text(encoding="utf-8")
        self.tts_script = ROOT / "skills" / "id-demo-video" / "scripts" / "tts_edge.py"
        self.compose_script = ROOT / "skills" / "id-demo-video" / "scripts" / "compose.sh"

    def test_router_contains_id_demo_video(self):
        self.assertIn("id-demo-video", self.agents)
        self.assertIn(
            "Demo video aplikasi / walkthrough layar / narasi Indonesia / demo lomba → skill `id-demo-video` (bukan `hyperframes` untuk durasi panjang utuh, bukan `playwright-qa`, bukan `visual-studio`). Kartu judul HTML→MP4 tetap `hyperframes`.",
            self.agents,
        )
        self.assertIn("/demo-video", self.agents)
        self.assertIn("skill `id-demo-video`", self.routing)
        self.assertIn("/demo-video", self.routing)

    def test_required_files_exist(self):
        expected_files = [
            ROOT / "skills" / "id-demo-video" / "SKILL.md",
            ROOT / "skills" / "id-demo-video" / "references" / "beats.md",
            ROOT / "skills" / "id-demo-video" / "references" / "tts-id.md",
            ROOT / "skills" / "id-demo-video" / "references" / "record-compose.md",
            ROOT / "skills" / "id-demo-video" / "references" / "storyboard.schema.md",
            ROOT / "skills" / "id-demo-video" / "scripts" / "tts_edge.py",
            ROOT / "skills" / "id-demo-video" / "scripts" / "compose.sh",
            ROOT / "commands" / "demo-video.md",
            ROOT / "manual-skills" / "demo-video" / "SKILL.md",
        ]
        for path in expected_files:
            self.assertTrue(path.is_file(), f"Missing file: {path}")

    def test_storyboard_duration_validation_logic(self):
        valid_path = ROOT / "tests" / "fixtures" / "id_demo_video" / "storyboard.valid.json"
        invalid_path = ROOT / "tests" / "fixtures" / "id_demo_video" / "storyboard.invalid.json"

        valid_data = json.loads(valid_path.read_text(encoding="utf-8"))
        ok, msg = validate_storyboard_duration(valid_data)
        self.assertTrue(ok, msg)
        self.assertEqual(valid_data["target_duration_s"], 600)
        total_valid = sum(s["duration_s"] for s in valid_data["scenes"])
        self.assertTrue(abs(total_valid - 600) <= 15, f"Valid total {total_valid} not in 600±15s")

        invalid_data = json.loads(invalid_path.read_text(encoding="utf-8"))
        ok_inv, msg_inv = validate_storyboard_duration(invalid_data)
        self.assertFalse(ok_inv, "Invalid storyboard should fail duration check")
        self.assertIn("differs from target", msg_inv)

    def test_tts_script_rejects_empty_input(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = Path(tmpdir) / "test.mp3"
            proc = subprocess.run(
                [sys.executable, str(self.tts_script), "--text", "   ", "--output", str(out_file), "--dry-run"],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("empty", proc.stderr.lower())

    def test_tts_script_rejects_unsupported_voice(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = Path(tmpdir) / "test.mp3"
            proc = subprocess.run(
                [sys.executable, str(self.tts_script), "--text", "Halo dunia", "--voice", "kokoro", "--output", str(out_file), "--dry-run"],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(proc.returncode, 0)

    def test_tts_script_dry_run_offline(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = Path(tmpdir) / "test.mp3"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(self.tts_script),
                    "--text",
                    "Selamat datang di demonstrasi aplikasi.",
                    "--voice",
                    "id-ID-GadisNeural",
                    "--output",
                    str(out_file),
                    "--dry-run",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("[DRY-RUN VALID]", proc.stdout)
            self.assertTrue(out_file.exists())

    def test_compose_script_syntax_and_validation(self):
        # Verify bash syntax without executing
        proc = subprocess.run(["bash", "-n", str(self.compose_script)], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)

        # Fails gracefully if target demo directory does not exist
        proc_run = subprocess.run(["bash", str(self.compose_script), "/nonexistent/demo/path"], capture_output=True, text=True)
        self.assertNotEqual(proc_run.returncode, 0)
        self.assertIn("does not exist", proc_run.stderr)


if __name__ == "__main__":
    unittest.main()
