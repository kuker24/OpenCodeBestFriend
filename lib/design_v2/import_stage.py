from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import tempfile
import uuid
import zipfile
from pathlib import Path
from typing import Any

from .bank import DesignV2Error, assert_under_v2, ensure_layout, load_policy
from .provenance import default_provenance
from .security import (
    allowed_extension,
    compile_secret_patterns,
    inspect_path,
    inspect_tree,
    inspect_zip,
    member_ok,
    scan_file_secrets,
)


class ImportRejected(DesignV2Error):
    code = "IMPORT_REJECTED"


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def _copy_file_nofollow(src: Path, dest: Path) -> None:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(src, flags)
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        with os.fdopen(fd, "rb") as reader, dest.open("wb") as writer:
            shutil.copyfileobj(reader, writer)
            fd = -1
    finally:
        if fd >= 0:
            os.close(fd)


def _materialize_tree(src: Path, dest: Path, policy: dict[str, Any]) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for dirpath, dirnames, filenames in os.walk(src, followlinks=False):
        current = Path(dirpath)
        rel = current.relative_to(src)
        target_dir = dest / rel if str(rel) != "." else dest
        if current.is_symlink():
            raise ImportRejected("symlink")
        kept: list[str] = []
        for name in dirnames:
            child = current / name
            st = child.lstat()
            if stat.S_ISLNK(st.st_mode):
                raise ImportRejected("symlink")
            kept.append(name)
            (target_dir / name).mkdir(parents=True, exist_ok=True)
        dirnames[:] = kept
        for name in filenames:
            child = current / name
            st = child.lstat()
            if stat.S_ISLNK(st.st_mode) or st.st_nlink > 1 or not stat.S_ISREG(st.st_mode):
                raise ImportRejected("unsafe_file")
            if not allowed_extension(name, policy) and name.lower() not in {"license", "copying"}:
                raise ImportRejected("type")
            _copy_file_nofollow(child, target_dir / name)


def _extract_zip(src: Path, dest: Path, policy: dict[str, Any]) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(src) as handle:
        for info in handle.infolist():
            name = info.filename.replace("\\", "/")
            if name.endswith("/"):
                continue
            if not member_ok(name):
                raise ImportRejected("zip_traversal")
            if not allowed_extension(Path(name).name, policy) and Path(name).name.lower() not in {
                "license",
                "copying",
            }:
                raise ImportRejected("type")
            target = dest / name
            assert_under_v2(dest, target)
            target.parent.mkdir(parents=True, exist_ok=True)
            with handle.open(info) as reader, target.open("wb") as writer:
                shutil.copyfileobj(reader, writer)


def _scan_staged(staged: Path, policy: dict[str, Any]) -> None:
    patterns = compile_secret_patterns(policy)
    for dirpath, _dirnames, filenames in os.walk(staged, followlinks=False):
        current = Path(dirpath)
        if current.is_symlink():
            raise ImportRejected("symlink")
        for name in filenames:
            child = current / name
            if child.is_symlink():
                raise ImportRejected("symlink")
            if scan_file_secrets(child, policy, patterns):
                raise ImportRejected("secret")


def _quarantine(root: Path, staged: Path, source_id: str, issues: list[str]) -> Path:
    dest = root / "quarantine" / source_id
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest)
    os.replace(staged, dest)
    report = {
        "source_id": source_id,
        "issues": issues,
        "status": "quarantined",
    }
    _atomic_write_json(root / "reports" / f"import-{source_id}.json", report)
    return dest


def import_stage(input_path: Path, root: Path, *, provider: str = "manual") -> dict[str, Any]:
    policy = load_policy()
    src = input_path.expanduser()
    if not src.exists():
        raise ImportRejected("missing")
    issues = inspect_path(src, policy)
    st = src.lstat()
    is_zip = src.suffix.lower() == ".zip" and stat.S_ISREG(st.st_mode)
    if stat.S_ISDIR(st.st_mode):
        issues = inspect_tree(src, policy)
    elif is_zip:
        issues = inspect_path(src, policy) + inspect_zip(src, policy)
    if issues:
        raise ImportRejected(",".join(issues))

    dirs = ensure_layout(root)
    source_id = uuid.uuid4().hex[:16]
    incoming = Path(tempfile.mkdtemp(prefix=f"incoming-{source_id}-", dir=str(dirs["tmp"])))
    assert_under_v2(root, incoming)
    staged = incoming / "payload"
    try:
        if is_zip:
            _extract_zip(src, staged, policy)
        elif stat.S_ISDIR(st.st_mode):
            _materialize_tree(src, staged, policy)
        else:
            if not allowed_extension(src.name, policy):
                raise ImportRejected("type")
            staged.mkdir(parents=True, exist_ok=True)
            _copy_file_nofollow(src, staged / src.name)
        _scan_staged(staged, policy)
        digest = _sha256_file(src) if stat.S_ISREG(st.st_mode) else source_id
        dest = dirs["sources"] / provider / source_id
        assert_under_v2(root, dest)
        if dest.exists():
            shutil.rmtree(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        os.replace(staged, dest)
        provenance = default_provenance(
            provider=provider,
            source_id=source_id,
            content_sha256=digest if len(digest) == 64 else None,
        )
        _atomic_write_json(dest / "provenance.json", provenance)
        report = {
            "status": "ok",
            "source_id": source_id,
            "provider": provider,
            "path": str(dest.relative_to(root)),
            "provenance": provenance,
        }
        _atomic_write_json(dirs["reports"] / f"import-{source_id}.json", report)
        return report
    except ImportRejected as exc:
        issues = [str(exc)]
        if incoming.exists():
            _quarantine(root, incoming, source_id, issues)
        raise
    finally:
        if incoming.exists():
            shutil.rmtree(incoming, ignore_errors=True)
