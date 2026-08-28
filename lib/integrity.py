from __future__ import annotations

import hashlib
from pathlib import Path

from .common import (
    bf_dir,
    bin_dir,
    config_dir,
    load_json,
    product_version,
    repo_root,
    sha256_file,
    write_json,
)
from .identity import identity_findings, owned_agents_block
from .status import Findings

AGENTS_TOKENS = ("USED", "CONSIDERED_NOT_USED", "MANUAL_NOT_INVOKED")
ROUTING_TITLE = "# OpenCode specialist routing (opencode-bestfriend)"


def expected_wrapper_text() -> str:
    return (
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        'ROOT="${OPENCODE_BF_ROOT:-$HOME/.local/share/opencode-bestfriend/product}"\n'
        'exec python3 "$ROOT/lib/cli.py" "$@"\n'
    )


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _agents_fingerprint(path: Path) -> str | None:
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    block = owned_agents_block(text)
    if block is None:
        return None
    return _sha256_text(block.strip() + "\n")


def source_tree_available(root: Path | None = None) -> bool:
    return ((root or repo_root()) / "templates" / "AGENTS.md").is_file()


def iter_skill_files(src: Path) -> list[Path]:
    out: list[Path] = []
    if not src.is_dir():
        return out
    for path in sorted(src.rglob("*")):
        if not path.is_file():
            continue
        if path.name.endswith(".pyc") or path.name == ".opencode-bestfriend.json":
            continue
        if "__pycache__" in path.parts:
            continue
        out.append(path)
    return out


def canonical_entries(root: Path | None = None) -> list[tuple[str, Path, Path, str]]:
    """Return (key, source, installed, kind)."""
    root = root or repo_root()
    cfg = config_dir()
    bf = bf_dir()
    entries: list[tuple[str, Path, Path, str]] = [
        ("agents.md", root / "templates" / "AGENTS.md", cfg / "AGENTS.md", "agents"),
        (
            "helpers/opencode-chromium-cdp",
            root / "bin" / "opencode-chromium-cdp",
            bin_dir() / "opencode-chromium-cdp",
            "helper",
        ),
        (
            "helpers/opencode-bf",
            root / "opencode-bf",
            bin_dir() / "opencode-bf",
            "wrapper",
        ),
        (
            "design-intelligence/policy.json",
            root / "design-intelligence" / "policy.json",
            bf / "design-intelligence" / "policy.json",
            "di",
        ),
        (
            "design-intelligence/taxonomy.json",
            root / "design-intelligence" / "taxonomy.json",
            bf / "design-intelligence" / "taxonomy.json",
            "di",
        ),
        (
            "design-intelligence/runtime/selection.py",
            root / "skills" / "impeccable" / "scripts" / "design_intelligence" / "selection.py",
            cfg / "skills" / "impeccable" / "scripts" / "design_intelligence" / "selection.py",
            "di",
        ),
        (
            "design-intelligence/cli.py",
            root / "skills" / "impeccable" / "scripts" / "design-intelligence.py",
            cfg / "skills" / "impeccable" / "scripts" / "design-intelligence.py",
            "di",
        ),
        (
            "config/skill-policy.json",
            root / "vendor" / "skill-policy.json",
            bf / "config" / "skill-policy.json",
            "owned-config",
        ),
        (
            "config/skill-allowlist.txt",
            root / "vendor" / "skill-allowlist.txt",
            bf / "config" / "skill-allowlist.txt",
            "owned-config",
        ),
    ]
    rules = root / "rules"
    if rules.is_dir():
        for path in sorted(rules.glob("*.md")):
            entries.append((f"rules/{path.name}", path, bf / "rules" / path.name, "rule"))
    from .common import load_policy

    _allow, _skills, model, manual = load_policy(root)
    for name in model:
        src = root / "skills" / name
        dest = cfg / "skills" / name
        for f in iter_skill_files(src):
            rel = f.relative_to(src).as_posix()
            entries.append((f"skills/{name}/{rel}", f, dest / rel, "model-skill"))
    for name in manual:
        src = root / "manual-skills" / name
        dest = bf / "skills" / name
        for f in iter_skill_files(src):
            rel = f.relative_to(src).as_posix()
            entries.append((f"manual-skills/{name}/{rel}", f, dest / rel, "manual-skill"))
        cmd = root / "commands" / f"{name}.md"
        entries.append((f"commands/{name}.md", cmd, cfg / "commands" / f"{name}.md", "command"))
    return entries


def fingerprint(path: Path, kind: str, source_text: str | None = None) -> str | None:
    if kind == "agents":
        if source_text is not None:
            return _sha256_text(source_text.strip() + "\n")
        return _agents_fingerprint(path)
    if kind == "wrapper":
        if path.is_file():
            return _sha256_text(path.read_text(encoding="utf-8"))
        return None
    if not path.is_file():
        return None
    return sha256_file(path)


def expected_fingerprint(source: Path, kind: str) -> str | None:
    if kind == "agents":
        if not source.is_file():
            return None
        return _sha256_text(source.read_text(encoding="utf-8").strip() + "\n")
    if kind == "wrapper":
        return _sha256_text(expected_wrapper_text())
    if not source.is_file():
        return None
    return sha256_file(source)


def build_integrity_manifest() -> dict:
    files: dict[str, dict] = {}
    root = repo_root()
    for key, source, installed, kind in canonical_entries(root):
        digest = fingerprint(installed, kind)
        expected = expected_fingerprint(source, kind) if source_tree_available(root) else digest
        files[key] = {
            "sha256": digest or "",
            "kind": kind,
            "expected": expected or "",
        }
    payload = {"schemaVersion": 1, "productVersion": product_version(), "files": files}
    dest = bf_dir() / "manifests" / "integrity.json"
    write_json(dest, payload)
    return payload


def agents_stale(text: str) -> bool:
    block = owned_agents_block(text) or text
    return any(tok not in block for tok in AGENTS_TOKENS)


def routing_stale(text: str) -> bool:
    first = text.lstrip().splitlines()[0] if text.strip() else ""
    return first != ROUTING_TITLE


def verify_owned_runtime() -> int:
    f = Findings()
    for status, label, evidence in identity_findings():
        f.add(status, label, evidence)
    agents = config_dir() / "AGENTS.md"
    if not agents.is_file():
        f.add("MISSING", "AGENTS.md", "missing")
        f.add("FAIL", "AGENTS.md", "missing")
    else:
        text = agents.read_text(encoding="utf-8")
        if agents_stale(text):
            f.add("STALE", "AGENTS.md", "missing USED/CONSIDERED_NOT_USED/MANUAL_NOT_INVOKED")
        else:
            f.add("PASS", "AGENTS.md", "canonical tokens")
    routing = bf_dir() / "rules" / "00-routing.md"
    if not routing.is_file():
        f.add("FAIL", "rules/00-routing.md", "missing")
    else:
        text = routing.read_text(encoding="utf-8")
        if routing_stale(text):
            f.add("STALE", "rules/00-routing.md", "title is not OpenCode specialist routing")
        else:
            f.add("PASS", "rules", "OpenCode specialist routing")
    root = repo_root()
    use_source = source_tree_available(root)
    stored = None
    stored_path = bf_dir() / "manifests" / "integrity.json"
    if stored_path.is_file():
        try:
            stored = load_json(stored_path)
        except (OSError, ValueError):
            stored = None
    missing_skills = 0
    skill_total = 0
    cmd_ok = 0
    cmd_total = 0
    helper_ok = 0
    for key, source, installed, kind in canonical_entries(root):
        live = fingerprint(installed, kind)
        if kind == "model-skill" and key.endswith("/SKILL.md"):
            skill_total += 1
            if live is None:
                missing_skills += 1
                f.add("MISSING", key, str(installed))
        if kind == "command":
            cmd_total += 1
            if live is not None:
                cmd_ok += 1
            else:
                f.add("MISSING", key, str(installed))
        if kind in {"helper", "wrapper"}:
            if live is None:
                f.add("MISSING", key, str(installed))
            else:
                helper_ok += 1
        expected = expected_fingerprint(source, kind) if use_source and source.exists() else None
        if expected is None and stored and isinstance(stored.get("files"), dict):
            expected = (stored["files"].get(key) or {}).get("expected") or (stored["files"].get(key) or {}).get(
                "sha256"
            )
        if live is None:
            continue
        if expected and live != expected:
            status = "STALE" if kind in {"agents", "rule"} else "DRIFT"
            f.add(status, key, "hash mismatch")
    if skill_total:
        f.add(
            "PASS" if missing_skills == 0 else "FAIL",
            "skills",
            f"{skill_total - missing_skills}/{skill_total}",
        )
    if cmd_total:
        f.add("PASS" if cmd_ok == cmd_total else "FAIL", "commands", f"{cmd_ok}/{cmd_total}")
    f.add("PASS" if helper_ok >= 2 else "FAIL", "helpers", f"{helper_ok}/2")
    return f.exit_code()


def cmd_verify() -> int:
    print("=== opencode-bestfriend verify ===")
    return verify_owned_runtime()
