from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
PROMPT_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SUMS_LINE_RE = re.compile(r"^([0-9a-f]{64})  (.+)$")
SPDX_ID_RE = re.compile(r"^SPDXRef-[A-Za-z0-9.-]+$")
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
FORBIDDEN_NAMES = {
    ".env",
    "credentials",
    "tokens",
    "credentials.json",
    "auth.json",
}
FORBIDDEN_SUFFIXES = {".pem", ".key"}
FORBIDDEN_DIR_PARTS = {
    ".git",
    "dist",
    ".scratch",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "DesignV2",
    "SmartDoc",
    ".home-fixture",
}
CORE_PATHS = (
    "VERSION",
    "skills/scroll-craft/SKILL.md",
    "skills/scroll-world/SKILL.md",
    "skills/scroll-craft/engine/scrollcraft.js",
    "vendor/provenance.json",
    "vendor/licenses/NATEHERK-SCROLL-CRAFT-MIT.txt",
    "vendor/release-contract.json",
    "scripts/make-release-artifacts.sh",
    "scripts/verify-release-artifacts.sh",
    "lib/release.py",
)


class ReleaseError(Exception):
    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        super().__init__(f"{code}: {detail}".strip() if detail else code)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReleaseError("INVALID_JSON", f"{path.name}: {exc}") from exc


def load_contract(root: Path | None = None) -> dict:
    path = (root or ROOT) / "vendor" / "release-contract.json"
    data = load_json(path)
    prompt = data.get("promptSha256")
    if not isinstance(prompt, str) or not PROMPT_SHA256_RE.fullmatch(prompt):
        raise ReleaseError("INVALID_PROMPT_SHA256", "contract")
    return data


def tarball_name(version: str) -> str:
    return f"OpenCodeBestFriend-v{version}.tar.gz"


def expected_artifacts(version: str) -> tuple[str, ...]:
    return (tarball_name(version), "SBOM.spdx.json", "release-provenance.json")


def parse_sha256sums(text: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip("\n")
        if not line or line.startswith("#"):
            continue
        if line.lower().startswith(("sha256 ", "sha256(", "sha512 ")):
            raise ReleaseError("UNKNOWN_ALGORITHM", line)
        match = SUMS_LINE_RE.fullmatch(line)
        if not match:
            raise ReleaseError("MALFORMED_CHECKSUM", line)
        digest, name = match.group(1), match.group(2)
        if name in mapping:
            raise ReleaseError("DUPLICATE_CHECKSUM", name)
        if name == "SHA256SUMS":
            raise ReleaseError("MALFORMED_CHECKSUM", "self-hash")
        mapping[name] = digest
    return mapping


def require_checksums(mapping: dict[str, str], version: str) -> None:
    expected = expected_artifacts(version)
    for name in expected:
        if name not in mapping:
            raise ReleaseError("MISSING_RELEASE_CHECKSUM", name)


def member_rel(name: str) -> str:
    cleaned = name.replace("\\", "/").lstrip("/")
    parts = [part for part in cleaned.split("/") if part not in (".", "")]
    if any(part == ".." for part in parts):
        raise ReleaseError("FORBIDDEN_RELEASE_MEMBER", name)
    if parts and parts[0].startswith("OpenCodeBestFriend-v"):
        parts = parts[1:]
    return "/".join(parts)


def forbidden_reason(rel: str) -> str | None:
    if not rel:
        return None
    parts = rel.split("/")
    name = parts[-1]
    if name in FORBIDDEN_NAMES:
        return rel
    if name.startswith(".env.") and name != ".env.example":
        return rel
    if Path(name).suffix in FORBIDDEN_SUFFIXES:
        return rel
    if any(part in FORBIDDEN_DIR_PARTS for part in parts):
        return rel
    if parts[:1] == ["Design"]:
        return rel
    return None


def inspect_tar(path: Path, version: str) -> list[str]:
    members: list[str] = []
    prefix = f"OpenCodeBestFriend-v{version}/"
    try:
        archive = tarfile.open(path, mode="r:gz")
    except (OSError, tarfile.TarError) as exc:
        raise ReleaseError("FORBIDDEN_RELEASE_MEMBER", str(exc)) from exc
    with archive:
        for info in archive.getmembers():
            rel = member_rel(info.name)
            members.append(rel)
            if info.name.startswith("/") or info.name.startswith("\\"):
                raise ReleaseError("FORBIDDEN_RELEASE_MEMBER", info.name)
            if info.issym() or info.islnk():
                target = info.linkname.replace("\\", "/")
                if target.startswith("/") or ".." in Path(target).parts:
                    raise ReleaseError("FORBIDDEN_RELEASE_MEMBER", info.name)
            reason = forbidden_reason(rel)
            if reason:
                raise ReleaseError("FORBIDDEN_RELEASE_MEMBER", reason)
            if info.isdir():
                continue
            if not info.name.startswith(prefix):
                raise ReleaseError("FORBIDDEN_RELEASE_MEMBER", info.name)
    return members


def validate_prompt_sha256(value: object) -> str:
    if not isinstance(value, str) or not PROMPT_SHA256_RE.fullmatch(value):
        raise ReleaseError("INVALID_PROMPT_SHA256", str(value))
    return value


def validate_sbom(doc: object, version: str, tarball_sha256: str | None = None) -> dict:
    if not isinstance(doc, dict):
        raise ReleaseError("INVALID_SBOM", "not an object")
    if doc.get("spdxVersion") != "SPDX-2.3":
        raise ReleaseError("INVALID_SBOM", "spdxVersion")
    packages = doc.get("packages")
    relationships = doc.get("relationships")
    if not isinstance(packages, list) or not packages:
        raise ReleaseError("INVALID_SBOM", "packages")
    if not isinstance(relationships, list) or not relationships:
        raise ReleaseError("INVALID_SBOM", "relationships")
    ids: set[str] = set()
    root = packages[0]
    if root.get("SPDXID") != "SPDXRef-Package-OpenCodeBestFriend":
        raise ReleaseError("INVALID_SBOM", "root SPDXID")
    if root.get("versionInfo") != version:
        raise ReleaseError("INVALID_SBOM", "root version")
    if tarball_sha256:
        checksums = root.get("checksums") or []
        if not any(
            isinstance(item, dict)
            and item.get("algorithm") == "SHA256"
            and item.get("checksumValue") == tarball_sha256
            for item in checksums
        ):
            raise ReleaseError("INVALID_SBOM", "root checksum")
    for package in packages:
        if not isinstance(package, dict):
            raise ReleaseError("INVALID_SBOM", "package")
        spdx_id = package.get("SPDXID")
        if not isinstance(spdx_id, str) or not SPDX_ID_RE.fullmatch(spdx_id):
            raise ReleaseError("INVALID_SBOM", f"SPDXID {spdx_id}")
        if spdx_id in ids:
            raise ReleaseError("INVALID_SBOM", f"duplicate {spdx_id}")
        ids.add(spdx_id)
        for key in ("name", "licenseDeclared", "downloadLocation"):
            if not package.get(key):
                raise ReleaseError("INVALID_SBOM", f"{spdx_id} {key}")
    described = False
    contained: set[str] = set()
    for rel in relationships:
        if not isinstance(rel, dict):
            raise ReleaseError("INVALID_SBOM", "relationship")
        left = rel.get("spdxElementId")
        right = rel.get("relatedSpdxElement")
        kind = rel.get("relationshipType")
        if kind == "DESCRIBES" and right == "SPDXRef-Package-OpenCodeBestFriend":
            described = True
        if (
            kind == "CONTAINS"
            and left == "SPDXRef-Package-OpenCodeBestFriend"
            and isinstance(right, str)
        ):
            contained.add(right)
    if not described:
        raise ReleaseError("INVALID_SBOM", "DESCRIBES")
    extras = {pkg_id for pkg_id in ids if pkg_id != "SPDXRef-Package-OpenCodeBestFriend"}
    if extras - contained:
        raise ReleaseError("INVALID_SBOM", "missing CONTAINS")
    return doc


def validate_provenance(doc: object, version: str, expected_commit: str | None = None) -> dict:
    if not isinstance(doc, dict):
        raise ReleaseError("PROVENANCE_MISMATCH", "not an object")
    if doc.get("schemaVersion") != 1:
        raise ReleaseError("PROVENANCE_MISMATCH", "schemaVersion")
    if doc.get("product") != "OpenCodeBestFriend":
        raise ReleaseError("PROVENANCE_MISMATCH", "product")
    if doc.get("version") != version:
        raise ReleaseError("VERSION_TAG_MISMATCH", str(doc.get("version")))
    if doc.get("sourceRepository") != "https://github.com/kuker24/OpenCodeBestFriend":
        raise ReleaseError("PROVENANCE_MISMATCH", "sourceRepository")
    commit = doc.get("sourceCommit")
    if not isinstance(commit, str) or not COMMIT_RE.fullmatch(commit):
        raise ReleaseError("PROVENANCE_MISMATCH", "sourceCommit")
    if expected_commit and commit != expected_commit:
        raise ReleaseError("PROVENANCE_MISMATCH", "sourceCommit")
    tag = doc.get("sourceTag")
    if tag is not None:
        if tag != f"v{version}":
            raise ReleaseError("VERSION_TAG_MISMATCH", str(tag))
    validate_prompt_sha256(doc.get("promptSha256"))
    artifacts = doc.get("artifactSha256")
    name = tarball_name(version)
    if not isinstance(artifacts, dict) or name not in artifacts:
        raise ReleaseError("PROVENANCE_MISMATCH", "artifactSha256")
    if "SBOM.spdx.json" in artifacts:
        raise ReleaseError("PROVENANCE_MISMATCH", "circular SBOM hash")
    return doc


def utc_from_unix(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_sbom(root: Path, version: str, tarball_sha256: str, created: str) -> dict:
    vendor = load_json(root / "vendor" / "provenance.json")
    packages = [
        {
            "SPDXID": "SPDXRef-Package-OpenCodeBestFriend",
            "name": "OpenCodeBestFriend",
            "versionInfo": version,
            "downloadLocation": "https://github.com/kuker24/OpenCodeBestFriend",
            "licenseDeclared": vendor.get("firstPartyLicense") or "MIT",
            "checksums": [{"algorithm": "SHA256", "checksumValue": tarball_sha256}],
        }
    ]
    relationships = [
        {
            "spdxElementId": "SPDXRef-DOCUMENT",
            "relationshipType": "DESCRIBES",
            "relatedSpdxElement": "SPDXRef-Package-OpenCodeBestFriend",
        }
    ]
    for component in vendor.get("components") or []:
        name = component.get("component")
        if not name:
            continue
        spdx_id = f"SPDXRef-Component-{name}"
        upstream = component.get("upstream")
        download = upstream if isinstance(upstream, str) and upstream.startswith("https://") else "NOASSERTION"
        version_info = component.get("version") or component.get("commit") or "NOASSERTION"
        package = {
            "SPDXID": spdx_id,
            "name": name,
            "versionInfo": version_info,
            "downloadLocation": download,
            "licenseDeclared": component.get("license") or "NOASSERTION",
        }
        if component.get("commit"):
            package["comment"] = f"upstream commit {component['commit']}"
        packages.append(package)
        relationships.append(
            {
                "spdxElementId": "SPDXRef-Package-OpenCodeBestFriend",
                "relationshipType": "CONTAINS",
                "relatedSpdxElement": spdx_id,
            }
        )
    return {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": f"OpenCodeBestFriend-{version}",
        "documentNamespace": f"https://github.com/kuker24/OpenCodeBestFriend/spdx/{version}",
        "creationInfo": {
            "created": created,
            "creators": ["Tool: opencode-bestfriend-release"],
        },
        "packages": packages,
        "relationships": relationships,
    }


def build_provenance(
    version: str,
    source_commit: str,
    source_tag: str | None,
    prompt_sha256: str,
    tarball_sha256: str,
) -> dict:
    payload = {
        "schemaVersion": 1,
        "product": "OpenCodeBestFriend",
        "version": version,
        "sourceRepository": "https://github.com/kuker24/OpenCodeBestFriend",
        "sourceCommit": source_commit,
        "sourceTag": source_tag,
        "promptSha256": prompt_sha256,
        "artifactSha256": {tarball_name(version): tarball_sha256},
        "signedTag": "DEFERRED",
    }
    validate_provenance(payload, version, source_commit)
    return payload


def write_sha256sums(out: Path, files: Iterable[Path]) -> None:
    lines = []
    for path in sorted(files, key=lambda item: item.name):
        lines.append(f"{sha256_file(path)}  {path.name}")
    (out / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")


def pack(out: Path, root: Path, version: str, source_commit: str, source_tag: str | None, created: str) -> None:
    tarball = out / tarball_name(version)
    inspect_tar(tarball, version)
    tarball_sha = sha256_file(tarball)
    contract = load_contract(root)
    sbom = build_sbom(root, version, tarball_sha, created)
    validate_sbom(sbom, version, tarball_sha)
    provenance = build_provenance(
        version,
        source_commit,
        source_tag,
        contract["promptSha256"],
        tarball_sha,
    )
    (out / "SBOM.spdx.json").write_text(json.dumps(sbom, indent=2) + "\n", encoding="utf-8")
    (out / "release-provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    write_sha256sums(out, (tarball, out / "SBOM.spdx.json", out / "release-provenance.json"))


def git_rev_parse(args: list[str], cwd: Path) -> str | None:
    import subprocess

    proc = subprocess.run(["git", "rev-parse", *args], cwd=cwd, capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def verify_dir(out: Path, root: Path | None = None, expected_commit: str | None = None) -> list[tuple[str, str]]:
    results: list[tuple[str, str]] = []

    def record(status: str, name: str) -> None:
        results.append((status, name))
        print(f"{status} {name}")

    try:
        sums_path = out / "SHA256SUMS"
        if not sums_path.is_file():
            raise ReleaseError("MISSING_RELEASE_CHECKSUM", "SHA256SUMS")
        mapping = parse_sha256sums(sums_path.read_text(encoding="utf-8"))
        provenance = load_json(out / "release-provenance.json")
        version = provenance.get("version")
        if not isinstance(version, str) or not VERSION_RE.fullmatch(version):
            raise ReleaseError("VERSION_TAG_MISMATCH", str(version))
        require_checksums(mapping, version)
        for name, digest in mapping.items():
            path = out / name
            if not path.is_file():
                raise ReleaseError("MISSING_RELEASE_CHECKSUM", name)
            if sha256_file(path) != digest:
                raise ReleaseError("CHECKSUM_MISMATCH", name)
        record("VERIFIED", "checksums")
        tarball = out / tarball_name(version)
        tarball_sha = sha256_file(tarball)
        inspect_tar(tarball, version)
        record("VERIFIED", "tarball-policy")
        sbom = load_json(out / "SBOM.spdx.json")
        validate_sbom(sbom, version, tarball_sha)
        record("VERIFIED", "sbom")
        validate_provenance(provenance, version, expected_commit)
        if provenance.get("artifactSha256", {}).get(tarball_name(version)) != tarball_sha:
            raise ReleaseError("PROVENANCE_MISMATCH", "artifactSha256")
        record("VERIFIED", "provenance")
        contract_root = root if root and (root / "vendor" / "release-contract.json").is_file() else None
        if contract_root:
            contract = load_contract(contract_root)
            if provenance.get("promptSha256") != contract["promptSha256"]:
                raise ReleaseError("INVALID_PROMPT_SHA256", "contract mismatch")
            record("VERIFIED", "prompt-sha256")
        else:
            validate_prompt_sha256(provenance.get("promptSha256"))
            record("NOT_AVAILABLE", "prompt-sha256-contract")
        tag = provenance.get("sourceTag")
        git_root = root if root and (root / ".git").exists() else None
        if not tag:
            record("NOT_APPLICABLE", "git-tag")
        elif not git_root:
            record("NOT_AVAILABLE", "git-tag")
        else:
            resolved = git_rev_parse([f"{tag}^{{commit}}"], git_root)
            if resolved is None:
                record("NOT_AVAILABLE", "git-tag")
            elif resolved != provenance.get("sourceCommit"):
                raise ReleaseError("PROVENANCE_MISMATCH", "tag commit")
            else:
                record("VERIFIED", "git-tag")
        if expected_commit:
            record("VERIFIED", "source-commit")
        elif git_root:
            head = git_rev_parse(["HEAD"], git_root)
            if head is None:
                record("NOT_AVAILABLE", "source-commit")
            elif head != provenance.get("sourceCommit"):
                raise ReleaseError("PROVENANCE_MISMATCH", "HEAD")
            else:
                record("VERIFIED", "source-commit")
        else:
            record("NOT_AVAILABLE", "source-commit")
    except ReleaseError as exc:
        record("FAILED", exc.code)
        raise
    return results


def smoke_extract(out: Path, dest: Path, version: str) -> None:
    tarball = out / tarball_name(version)
    prefix = f"OpenCodeBestFriend-v{version}"
    dest.mkdir(parents=True, exist_ok=True)
    with tarfile.open(tarball, mode="r:gz") as archive:
        if sys.version_info >= (3, 12):
            archive.extractall(dest, filter="data")
        else:
            archive.extractall(dest)
    extracted = dest / prefix
    if not extracted.is_dir():
        raise ReleaseError("FORBIDDEN_RELEASE_MEMBER", "missing prefix")
    version_text = (extracted / "VERSION").read_text(encoding="utf-8").strip()
    if version_text != version:
        raise ReleaseError("VERSION_TAG_MISMATCH", version_text)
    for rel in CORE_PATHS:
        if not (extracted / rel).exists():
            raise ReleaseError("MISSING_RELEASE_CHECKSUM", rel)
    if (extracted / ".git").exists() or (extracted / "dist").exists():
        raise ReleaseError("FORBIDDEN_RELEASE_MEMBER", "nested vcs or dist")
    inspect_tar(tarball, version)


def cmd_pack(args: argparse.Namespace) -> int:
    try:
        pack(
            Path(args.out),
            Path(args.root),
            args.version,
            args.sha,
            args.tag or None,
            args.created,
        )
    except ReleaseError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    try:
        verify_dir(Path(args.dir), Path(args.root) if args.root else None, args.expected_commit)
    except ReleaseError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


def cmd_inspect(args: argparse.Namespace) -> int:
    try:
        inspect_tar(Path(args.tarball), args.version)
    except ReleaseError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


def cmd_smoke(args: argparse.Namespace) -> int:
    try:
        smoke_extract(Path(args.dir), Path(args.dest), args.version)
    except ReleaseError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print("VERIFIED extract-smoke")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="lib.release")
    sub = parser.add_subparsers(dest="cmd", required=True)
    pack_p = sub.add_parser("pack")
    pack_p.add_argument("--root", required=True)
    pack_p.add_argument("--out", required=True)
    pack_p.add_argument("--version", required=True)
    pack_p.add_argument("--sha", required=True)
    pack_p.add_argument("--tag", default="")
    pack_p.add_argument("--created", required=True)
    pack_p.set_defaults(func=cmd_pack)
    verify_p = sub.add_parser("verify")
    verify_p.add_argument("dir")
    verify_p.add_argument("--root", default=str(ROOT))
    verify_p.add_argument("--expected-commit", default=None)
    verify_p.set_defaults(func=cmd_verify)
    inspect_p = sub.add_parser("inspect-tar")
    inspect_p.add_argument("tarball")
    inspect_p.add_argument("--version", required=True)
    inspect_p.set_defaults(func=cmd_inspect)
    smoke_p = sub.add_parser("smoke-extract")
    smoke_p.add_argument("dir")
    smoke_p.add_argument("--dest", required=True)
    smoke_p.add_argument("--version", required=True)
    smoke_p.set_defaults(func=cmd_smoke)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
