from __future__ import annotations

import json
import os
from pathlib import Path

from .common import run, share_dir, which
from .status import Findings

PROJECT_MARKERS = (
    ".git",
    "package.json",
    "pyproject.toml",
    "go.mod",
    "Cargo.toml",
    "opencode.json",
    "opencode.jsonc",
)


def cbm_bin() -> Path | None:
    fixture = os.environ.get("OPENCODE_BF_TEST_CBM")
    if fixture and Path(fixture).is_file():
        return Path(fixture)
    path = share_dir() / "components" / "codebase-memory" / "bin" / "codebase-memory-mcp"
    if path.is_file() and os.access(path, os.X_OK):
        return path
    found = which("codebase-memory-mcp")
    return Path(found) if found else None


def looks_like_project(cwd: Path) -> bool:
    for name in PROJECT_MARKERS:
        if (cwd / name).exists():
            return True
    return False


def _last_json(text: str):
    dec = json.JSONDecoder()
    blob = text.strip()
    for i, ch in enumerate(blob):
        if ch not in "{[":
            continue
        try:
            obj, _end = dec.raw_decode(blob, i)
        except json.JSONDecodeError:
            continue
        return obj
    raise ValueError("no json")


def cbm_cli(args: list[str]) -> tuple[int, object | None, str]:
    bin_path = cbm_bin()
    if not bin_path:
        return 2, None, "missing"
    r = run([str(bin_path), "cli", *args])
    text = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0:
        try:
            return r.returncode, _last_json(text), text
        except (ValueError, json.JSONDecodeError):
            return r.returncode, None, text
    try:
        return 0, _last_json(text), text
    except (ValueError, json.JSONDecodeError):
        return 0, None, text


def match_project(cwd: Path, payload) -> dict | None:
    if not isinstance(payload, dict):
        return None
    projects = payload.get("projects") or []
    want = str(cwd.resolve())
    for proj in projects:
        if not isinstance(proj, dict):
            continue
        root = str(proj.get("root_path") or "")
        if root and Path(root).resolve() == Path(want):
            return proj
    return None


def project_status(cwd: Path | None = None) -> list[tuple[str, str, str]]:
    cwd = (cwd or Path.cwd()).resolve()
    if not looks_like_project(cwd):
        return [("NOT_APPLICABLE", "CBM project", "not a repository/project")]
    bin_path = cbm_bin()
    if not bin_path:
        return [("FAIL", "CBM binary", "missing")]
    rc, payload, _text = cbm_cli(["list_projects"])
    if rc != 0 or payload is None:
        return [("DEGRADED", "CBM project", "NOT_CHECKED")]
    proj = match_project(cwd, payload)
    if proj is None:
        return [("DEGRADED", "CBM project", "CURRENT_REPO_NOT_INDEXED")]
    out = [("PASS", "CBM project", "registered")]
    name = str(proj.get("name") or "")
    if name:
        src, status_payload, _ = cbm_cli(["index_status", "--project", name])
        if src == 0 and isinstance(status_payload, dict) and not status_payload.get("error"):
            out.append(("PASS", "CBM index", "FRESH"))
        else:
            out.append(("DEGRADED", "CBM index", "NOT_CHECKED"))
    return out


def cmd_cbm_status() -> int:
    f = Findings()
    bin_path = cbm_bin()
    if bin_path:
        ver = run([str(bin_path), "--version"])
        f.add("PASS", "CBM binary", (ver.stdout + ver.stderr).strip())
    else:
        f.add("FAIL", "CBM binary", "missing")
    for item in project_status():
        f.add(*item)
    return f.exit_code()


def cmd_cbm_index(path: str) -> int:
    target = Path(path).expanduser().resolve()
    if not target.exists():
        print(f"FAIL CBM index missing path {target}")
        return 1
    bin_path = cbm_bin()
    if not bin_path:
        print("FAIL CBM binary missing")
        return 1
    r = run([str(bin_path), "cli", "index_repository", "--repo-path", str(target), "--mode", "fast"])
    text = (r.stdout or "") + (r.stderr or "")
    print(text.strip())
    return 0 if r.returncode == 0 else 1
