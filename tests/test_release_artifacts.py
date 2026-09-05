#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT))
from lib.release import (  # noqa: E402
    ReleaseError,
    build_provenance,
    build_sbom,
    inspect_tar,
    load_contract,
    parse_sha256sums,
    require_checksums,
    sha256_file,
    tarball_name,
    validate_prompt_sha256,
    validate_provenance,
    validate_sbom,
    verify_dir,
    write_sha256sums,
)

KNOWN_PROMPT = "93b05df84606b96472ecdb54306e8a5586d0b968940f81575c18097be29913db"
SCRIPT = ROOT / "scripts" / "make-release-artifacts.sh"


def _run_builder(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def _tiny_tar(path: Path, version: str, members: dict[str, bytes], prefix: bool = True) -> None:
    with tarfile.open(path, mode="w:gz") as archive:
        for rel, data in members.items():
            name = f"OpenCodeBestFriend-v{version}/{rel}" if prefix else rel
            info = tarfile.TarInfo(name)
            info.size = len(data)
            archive.addfile(info, io.BytesIO(data))


def _valid_dist(tmp: Path, version: str = "1.7.1", commit: str = "a" * 40) -> Path:
    out = tmp / "dist"
    out.mkdir()
    tarball = out / tarball_name(version)
    _tiny_tar(tarball, version, {"VERSION": f"{version}\n".encode()})
    digest = sha256_file(tarball)
    sbom = build_sbom(ROOT, version, digest, "2026-09-05T00:00:00Z")
    provenance = build_provenance(version, commit, f"v{version}", KNOWN_PROMPT, digest)
    (out / "SBOM.spdx.json").write_text(json.dumps(sbom, indent=2) + "\n", encoding="utf-8")
    (out / "release-provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    write_sha256sums(out, (tarball, out / "SBOM.spdx.json", out / "release-provenance.json"))
    return out


class ReleaseArtifactTests(unittest.TestCase):
    def test_prompt_hash_contract(self):
        contract = load_contract(ROOT)
        self.assertEqual(contract["promptSha256"], KNOWN_PROMPT)
        self.assertEqual(contract["signedTag"], "DEFERRED")
        self.assertEqual(contract["releaseImmutability"], "NOT_CONFIGURED")
        self.assertEqual(validate_prompt_sha256(KNOWN_PROMPT), KNOWN_PROMPT)

    def test_sha256sums_parser_rejects_bad_input(self):
        mapping = parse_sha256sums(f"{'a' * 64}  one.tar.gz\n{'b' * 64}  SBOM.spdx.json\n")
        self.assertEqual(set(mapping), {"one.tar.gz", "SBOM.spdx.json"})
        with self.assertRaises(ReleaseError) as duplicate:
            parse_sha256sums(f"{'a' * 64}  one.tar.gz\n{'b' * 64}  one.tar.gz\n")
        self.assertEqual(duplicate.exception.code, "DUPLICATE_CHECKSUM")
        with self.assertRaises(ReleaseError) as malformed:
            parse_sha256sums("not-a-hash  file\n")
        self.assertEqual(malformed.exception.code, "MALFORMED_CHECKSUM")
        with self.assertRaises(ReleaseError) as algo:
            parse_sha256sums("SHA256 (file) = " + "a" * 64 + "\n")
        self.assertEqual(algo.exception.code, "UNKNOWN_ALGORITHM")
        with self.assertRaises(ReleaseError) as missing:
            require_checksums({"SBOM.spdx.json": "a" * 64}, "1.7.1")
        self.assertEqual(missing.exception.code, "MISSING_RELEASE_CHECKSUM")

    def test_forbidden_env_member(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "bad.tar.gz"
            _tiny_tar(path, "1.7.1", {".env": b"SECRET=1\n"})
            with self.assertRaises(ReleaseError) as err:
                inspect_tar(path, "1.7.1")
            self.assertEqual(err.exception.code, "FORBIDDEN_RELEASE_MEMBER")

    def test_attack_checksum_mismatch(self):
        with tempfile.TemporaryDirectory() as raw:
            out = _valid_dist(Path(raw))
            tarball = next(out.glob("*.tar.gz"))
            tarball.write_bytes(tarball.read_bytes() + b"x")
            with self.assertRaises(ReleaseError) as err:
                verify_dir(out, ROOT, "a" * 40)
            self.assertEqual(err.exception.code, "CHECKSUM_MISMATCH")

    def test_attack_provenance_mismatch(self):
        with tempfile.TemporaryDirectory() as raw:
            out = _valid_dist(Path(raw))
            path = out / "release-provenance.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["sourceCommit"] = "b" * 40
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            write_sha256sums(
                out,
                (out / tarball_name("1.7.1"), out / "SBOM.spdx.json", path),
            )
            with self.assertRaises(ReleaseError) as err:
                verify_dir(out, ROOT, "a" * 40)
            self.assertEqual(err.exception.code, "PROVENANCE_MISMATCH")

    def test_attack_invalid_prompt_sha256(self):
        with self.assertRaises(ReleaseError) as err:
            validate_prompt_sha256(KNOWN_PROMPT[:63])
        self.assertEqual(err.exception.code, "INVALID_PROMPT_SHA256")

    def test_attack_missing_checksum_line(self):
        with tempfile.TemporaryDirectory() as raw:
            out = _valid_dist(Path(raw))
            sums = (out / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
            kept = [line for line in sums if not line.endswith(".tar.gz")]
            (out / "SHA256SUMS").write_text("\n".join(kept) + "\n", encoding="utf-8")
            with self.assertRaises(ReleaseError) as err:
                verify_dir(out, ROOT, "a" * 40)
            self.assertEqual(err.exception.code, "MISSING_RELEASE_CHECKSUM")

    def test_attack_invalid_sbom(self):
        with tempfile.TemporaryDirectory() as raw:
            out = _valid_dist(Path(raw))
            (out / "SBOM.spdx.json").write_text("{}\n", encoding="utf-8")
            write_sha256sums(
                out,
                (out / tarball_name("1.7.1"), out / "SBOM.spdx.json", out / "release-provenance.json"),
            )
            with self.assertRaises(ReleaseError) as err:
                verify_dir(out, ROOT, "a" * 40)
            self.assertEqual(err.exception.code, "INVALID_SBOM")

    def test_sbom_relationships_from_vendor_provenance(self):
        digest = "c" * 64
        sbom = build_sbom(ROOT, "1.7.1", digest, "2026-09-05T00:00:00Z")
        validate_sbom(sbom, "1.7.1", digest)
        names = {pkg["name"] for pkg in sbom["packages"]}
        self.assertIn("scroll-craft", names)
        scroll = next(pkg for pkg in sbom["packages"] if pkg["name"] == "scroll-craft")
        self.assertEqual(scroll["versionInfo"], "0b816225945e45380397d6a0487efa3c98916858")

    def test_builder_source_ref_mismatch(self):
        proc = _run_builder("--sha", "0" * 40)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("SOURCE_REF_MISMATCH", proc.stderr)

    def test_builder_version_tag_mismatch(self):
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        proc = _run_builder("--sha", head, "--tag", "v0.0.0", "--allow-untagged")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("VERSION_TAG_MISMATCH", proc.stderr)

    def test_builder_missing_release_tag_fails_closed(self):
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        proc = _run_builder("--sha", head)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("SOURCE_REF_MISMATCH", proc.stderr)

    def test_ci_and_scripts_are_wired(self):
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertIn("release-artifact:", workflow)
        self.assertIn("scripts/make-release-artifacts.sh", workflow)
        self.assertIn("scripts/verify-release-artifacts.sh", workflow)
        self.assertIn("--allow-untagged", workflow)
        helper = (ROOT / "scripts" / "make-release-artifacts.sh").read_text(encoding="utf-8")
        self.assertIn('gzip -n', helper)
        self.assertNotIn("git archive --format=tar.gz", helper)
        self.assertIn('"$RELEASE_SHA"', helper)


if __name__ == "__main__":
    unittest.main()
