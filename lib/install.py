from __future__ import annotations

import os
import re
import shutil
import stat
import tarfile
import tempfile
import time
import urllib.request
from pathlib import Path

from . import jsonc
from .identity import EXPECTED_PRODUCT, EXPECTED_REPO, detect_legacy_overlay
from .integrity import build_integrity_manifest, verify_owned_runtime
from .paths import NAME_RE, assert_skill_name, resolve_backup_stamp, tar_member_ok
from .common import (
    backups_dir,
    bf_dir,
    bin_dir,
    claude_snapshot_path,
    compare_claude_snapshot,
    config_dir,
    copytree_filtered,
    die,
    home,
    info,
    load_json,
    load_policy,
    product_version,
    repo_root,
    run,
    sha256_file,
    share_dir,
    snapshot_claude,
    state_dir,
    warn,
    which,
    write_json,
)

OWNED_MCP = ("codebase-memory-mcp", "context7", "shadcn")
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?\n)---\n", re.DOTALL)
SHELL_BLOCK = (
    "\n# OPENCODEBESTFRIEND:BEGIN\n"
    "export OPENCODE_DISABLE_CLAUDE_CODE=1\n"
    "# OPENCODEBESTFRIEND:END\n"
)
CLAUDE_ACTIVE = (
    "~/.claude/",
    "$HOME/.claude/",
    "claude-gbf",
    "CLAUDE_CODE_",
    "CLAUDE_DESIGN_BANK",
    "grokbestfriend-claude",
    "claude mcp",
)
AGENTS_BEGIN = "<!-- OPENCODEBESTFRIEND:BEGIN -->"
AGENTS_END = "<!-- OPENCODEBESTFRIEND:END -->"
OWNED_COMMAND_MARKERS = (
    "OpenCode-adapted manual specialist",
    "OPENCODEBESTFRIEND:COMMAND",
)


def stage_dir() -> Path:
    return share_dir() / "cache" / "stage"


def transaction_path() -> Path:
    return state_dir() / "transaction.json"


def set_transaction(status: str, extra: dict | None = None) -> None:
    payload = {"status": status, "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if extra:
        payload.update(extra)
    write_json(transaction_path(), payload)


def detect_opencode() -> tuple[str, tuple[int, int, int], str]:
    oc = which("opencode")
    mock = os.environ.get("OPENCODE_BF_MOCK_OPENCODE")
    if mock:
        oc = mock
    if not oc:
        die("OPENCODE_MISSING: install OpenCode 1.18.x and put `opencode` on PATH")
    ver_out = run([oc, "--version"])
    text = (ver_out.stdout or ver_out.stderr or "").strip()
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", text)
    if not m:
        die(f"OPENCODE_VERSION_UNPARSABLE: {text!r}")
    ver = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    if ver[0] != 1 or ver[1] != 18:
        die(f"UNSUPPORTED_OPENCODE_VERSION {text} (need OpenCode stable 1.18.x)")
    schema = "mcp-name"
    return oc, ver, schema


def config_candidates() -> list[Path]:
    cfg = config_dir()
    return [cfg / "opencode.jsonc", cfg / "opencode.json"]


def existing_config_path() -> Path | None:
    for p in config_candidates():
        if p.is_file():
            return p
    return None


def target_config_path() -> Path:
    existing = existing_config_path()
    if existing:
        return existing
    return config_dir() / "opencode.jsonc"


def extract_agents_block(text: str) -> str:
    if AGENTS_BEGIN in text and AGENTS_END in text:
        start = text.index(AGENTS_BEGIN)
        end = text.index(AGENTS_END) + len(AGENTS_END)
        return text[start:end].strip() + "\n"
    return text.strip() + "\n"


def merge_agents_md(existing: str, block: str) -> str:
    block = extract_agents_block(block).rstrip() + "\n"
    if AGENTS_BEGIN in existing and AGENTS_END in existing:
        return re.sub(
            re.escape(AGENTS_BEGIN) + r".*?" + re.escape(AGENTS_END),
            block.strip(),
            existing,
            count=1,
            flags=re.DOTALL,
        )
    if not existing.strip():
        return block
    return existing.rstrip() + "\n\n" + block


def strip_agents_block(existing: str) -> str:
    if AGENTS_BEGIN not in existing:
        return existing
    out = re.sub(
        re.escape(AGENTS_BEGIN) + r".*?" + re.escape(AGENTS_END) + r"\n?",
        "",
        existing,
        count=1,
        flags=re.DOTALL,
    )
    return out.strip() + ("\n" if out.strip() else "")


def command_is_owned(path: Path) -> bool:
    if not path.is_file():
        return True
    text = path.read_text(encoding="utf-8")
    return any(m in text for m in OWNED_COMMAND_MARKERS)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    data: dict = {}
    for line in m.group(1).splitlines():
        mm = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not mm:
            continue
        data[mm.group(1)] = mm.group(2).strip().strip('"')
    return data, text[m.end() :]


def catalogs_ok(root: Path) -> bool:
    return (root / "Refero/bank/catalog.json").is_file() and (
        root / "motionsites/library/catalog.json"
    ).is_file()


def discover_design_bank() -> tuple[str, str] | None:
    candidates: list[tuple[str, str]] = []
    env = os.environ.get("OPENCODE_DESIGN_BANK") or os.environ.get("GROK_DESIGN_BANK")
    if env:
        candidates.append((env, "env"))
    pointer = bf_dir() / "config" / "design-bank.json"
    if pointer.is_file():
        try:
            root = load_json(pointer).get("root")
            if root:
                candidates.append((root, "existing-pointer"))
        except (OSError, ValueError):
            pass
    candidates.append((str(home() / "Design"), "home-Design"))
    candidates.append((str(share_dir() / "design-bank"), "owned"))
    seen = set()
    for raw, source in candidates:
        p = Path(raw).expanduser()
        key = str(p)
        if key in seen:
            continue
        seen.add(key)
        if catalogs_ok(p):
            return str(p), source
    return None


def _tar_target_ok(dest: Path, name: str) -> bool:
    return tar_member_ok(dest, name)


def safe_extract(tf: tarfile.TarFile, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    dest = dest.resolve()
    for member in tf.getmembers():
        if not _tar_target_ok(dest, member.name):
            die(f"ARCHIVE_PATH_TRAVERSAL {member.name}")
        if member.issym() or member.islnk():
            link = member.linkname or ""
            if not _tar_target_ok(dest, link) and not _tar_target_ok(dest, str(Path(member.name).parent / link)):
                die(f"ARCHIVE_PATH_TRAVERSAL {member.name} -> {link}")
    kwargs: dict = {"path": str(dest)}
    if "filter" in tarfile.TarFile.extractall.__code__.co_varnames:
        kwargs["filter"] = "data"
    try:
        tf.extractall(**kwargs)
    except SystemExit:
        raise
    except Exception as exc:
        die(f"ARCHIVE_PATH_TRAVERSAL {exc}")


def download_design_bank() -> tuple[str, str]:
    sources = load_json(repo_root() / "vendor" / "sources.json")["sources"]["design-bank"]
    url = sources["artifactUrl"]
    expected = sources["artifactSha256"]
    dest = share_dir() / "design-bank"
    cache = share_dir() / "cache" / "downloads"
    cache.mkdir(parents=True, exist_ok=True)
    archive = cache / "Design-bank.tgz"
    info(f"downloading Design Bank {url}")
    try:
        urllib.request.urlretrieve(url, archive)
    except Exception as exc:
        die(f"DESIGN_BANK_DOWNLOAD_FAILED: {exc}")
    got = sha256_file(archive)
    if got != expected:
        archive.unlink(missing_ok=True)
        die(f"DESIGN_BANK_CHECKSUM_FAILED expected={expected} got={got}")
    tmp = share_dir() / "cache" / "design-bank-extract"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    with tarfile.open(archive, "r:*") as tf:
        safe_extract(tf, tmp)
    root = tmp
    if not catalogs_ok(root):
        found = None
        for cand in tmp.rglob("Refero"):
            parent = cand.parent
            if catalogs_ok(parent):
                found = parent
                break
        if not found:
            die("DESIGN_BANK_CORRUPT_OR_MISSING after extract")
        root = found
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(root, dest)
    shutil.rmtree(tmp, ignore_errors=True)
    if not catalogs_ok(dest):
        die("DESIGN_BANK_CORRUPT_OR_MISSING after commit")
    return str(dest), "download"


def resolve_design_bank(skip: bool, offline: bool) -> tuple[str | None, str, str]:
    found = discover_design_bank()
    if found:
        return found[0], found[1], "reuse-read-only"
    if skip:
        return None, "skipped", "DEGRADED_DESIGN_BANK"
    if offline:
        return None, "offline", "DEGRADED_DESIGN_BANK"
    root, source = download_design_bank()
    return root, source, "owned-download"


def download_codebase_memory(offline: bool = False) -> Path:
    sources = load_json(repo_root() / "vendor" / "sources.json")["sources"]["codebase-memory"]
    url = sources["artifactUrl"]
    expected = sources["artifactSha256"]
    version = sources["version"]
    target_dir = share_dir() / "components" / "codebase-memory" / "bin"
    target = target_dir / "codebase-memory-mcp"
    fixture = os.environ.get("OPENCODE_BF_TEST_CBM")
    if fixture:
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(fixture, target)
        target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        info(f"codebase-memory fixture -> {target}")
        return target
    if target.is_file() and os.access(target, os.X_OK):
        got = run([str(target), "--version"])
        if got.returncode == 0 and version in (got.stdout + got.stderr):
            info(f"codebase-memory {version} already installed")
            return target
        if offline:
            die("CODEBASE_MEMORY_OFFLINE_UNUSABLE")
    elif offline:
        die("CODEBASE_MEMORY_OFFLINE_MISSING")
    machine = os.uname().machine
    if machine not in {"x86_64", "amd64"}:
        die(f"codebase-memory pinned artifact is Linux x86_64 only (got {machine})")
    cache = share_dir() / "cache" / "downloads"
    cache.mkdir(parents=True, exist_ok=True)
    archive = cache / "codebase-memory-mcp-linux-amd64-portable.tar.gz"
    info(f"downloading {url}")
    try:
        urllib.request.urlretrieve(url, archive)
    except Exception as exc:
        die(f"CODEBASE_MEMORY_DOWNLOAD_FAILED: {exc}")
    got = sha256_file(archive)
    if got != expected:
        archive.unlink(missing_ok=True)
        die(f"CODEBASE_MEMORY_CHECKSUM_FAILED expected={expected} got={got}")
    with tempfile.TemporaryDirectory() as td:
        tdir = Path(td)
        with tarfile.open(archive, "r:gz") as tf:
            safe_extract(tf, tdir)
        bin_path = tdir / "codebase-memory-mcp"
        if not bin_path.is_file():
            found = list(tdir.rglob("codebase-memory-mcp"))
            if not found:
                die("codebase-memory binary missing from archive")
            bin_path = found[0]
        bin_path.chmod(bin_path.stat().st_mode | stat.S_IXUSR)
        ver = run([str(bin_path), "--version"])
        if ver.returncode != 0 or version not in (ver.stdout + ver.stderr):
            die(f"codebase-memory version mismatch {ver.stdout!r} {ver.stderr!r}")
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(bin_path, target)
        target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    info(f"codebase-memory {version} installed")
    return target


def owned_mcp_spec(cbm_bin: Path) -> dict:
    return {
        "codebase-memory-mcp": {
            "type": "local",
            "command": [str(cbm_bin)],
            "enabled": True,
            "timeout": 30000,
        },
        "context7": {
            "type": "remote",
            "url": "https://mcp.context7.com/mcp",
            "enabled": True,
        },
        "shadcn": {
            "type": "local",
            "command": ["npx", "-y", "shadcn@4.18.0", "mcp"],
            "enabled": True,
        },
    }


def merge_opencode_config(cbm_bin: Path, dry_run: bool = False) -> dict:
    path = target_config_path()
    raw = path.read_text(encoding="utf-8") if path.is_file() else "{}"
    try:
        data = jsonc.loads(raw)
    except Exception as exc:
        die(f"OPENCODE_CONFIG_INVALID: {exc}")
    if not isinstance(data, dict):
        die("OPENCODE_CONFIG_INVALID: root is not an object")
    data.setdefault("$schema", "https://opencode.ai/config.json")
    mcp = data.get("mcp")
    if mcp is None:
        mcp = {}
        data["mcp"] = mcp
    if not isinstance(mcp, dict):
        die("OPENCODE_CONFIG_INVALID mcp")
    owned = owned_mcp_spec(cbm_bin)
    plan = {"path": str(path), "add": [], "update": [], "preserve": []}
    man_path = bf_dir() / "manifests" / "ownership.json"
    we_own: set[str] = set()
    if man_path.is_file():
        we_own = set(load_json(man_path).get("ownedMcp") or [])
    for name, spec in owned.items():
        existing = mcp.get(name)
        if existing is None:
            mcp[name] = spec
            plan["add"].append(name)
            continue
        if name in we_own or existing == spec:
            mcp[name] = spec
            plan["update"].append(name)
        else:
            plan["preserve"].append(name)
            info(f"preserving foreign mcp {name}")
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        to_write = {name: owned[name] for name in (plan["add"] + plan["update"])}
        if not path.is_file() or not jsonc.contains_comments(raw):
            path.write_text(jsonc.dumps(data), encoding="utf-8")
        else:
            try:
                merged = jsonc.upsert_mcp_servers(raw, to_write) if to_write else raw
                jsonc.loads(merged)
                path.write_text(merged if merged.endswith("\n") else merged + "\n", encoding="utf-8")
            except Exception as exc:
                die(f"OPENCODE_CONFIG_JSONC_SURGICAL_FAILED: {exc}")
        info(f"merged {path}")
    return plan


def ensure_shell_isolation(dry_run: bool = False) -> list[str]:
    written = []
    for name in (".bashrc", ".zshrc"):
        path = home() / name
        if not path.is_file() and name == ".zshrc":
            continue
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        if "# OPENCODEBESTFRIEND:BEGIN" in text:
            continue
        if dry_run:
            written.append(str(path))
            continue
        if path.is_file():
            stamp = backups_dir() / time.strftime("%Y%m%dT%H%M%SZ")
            stamp.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, stamp / name.lstrip("."))
        path.write_text(text.rstrip() + SHELL_BLOCK, encoding="utf-8")
        written.append(str(path))
        info(f"wrote isolation block {path}")
    return written


def strip_shell_isolation() -> None:
    for name in (".bashrc", ".zshrc"):
        path = home() / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if "# OPENCODEBESTFRIEND:BEGIN" not in text:
            continue
        new = re.sub(
            r"\n?# OPENCODEBESTFRIEND:BEGIN\nexport OPENCODE_DISABLE_CLAUDE_CODE=1\n# OPENCODEBESTFRIEND:END\n?",
            "\n",
            text,
        )
        path.write_text(new, encoding="utf-8")
        info(f"removed isolation block {path}")


def _copy_if(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
    elif src.is_file():
        shutil.copy2(src, dest)


def capture_preinstall(meta: dict | None = None) -> dict:
    cfg = existing_config_path()
    helpers = {
        name: ("present" if (bin_dir() / name).is_file() else "absent")
        for name in ("opencode-bf", "opencode-chromium-cdp")
    }
    skills: dict[str, str] = {}
    if meta:
        root = config_dir() / "skills"
        for name in meta.get("model") or []:
            skills[name] = "present" if (root / name).is_dir() else "absent"
    return {
        "config": "present" if cfg else "absent",
        "configName": cfg.name if cfg else None,
        "agents": "present" if (config_dir() / "AGENTS.md").is_file() else "absent",
        "commands": "present" if (config_dir() / "commands").is_dir() else "absent",
        "bestfriend": "present" if bf_dir().is_dir() else "absent",
        "bashrc": "present" if (home() / ".bashrc").is_file() else "absent",
        "zshrc": "present" if (home() / ".zshrc").is_file() else "absent",
        "shareProduct": "present" if (share_dir() / "product").is_dir() else "absent",
        "shareComponents": "present" if (share_dir() / "components").is_dir() else "absent",
        "helpers": helpers,
        "skills": skills,
    }


def backup_relevant(stamp: str, meta: dict | None = None) -> Path:
    dest = backups_dir() / stamp
    dest.mkdir(parents=True, exist_ok=True)
    pre = capture_preinstall(meta)
    cfg = existing_config_path()
    copied = []
    if cfg and cfg.is_file():
        shutil.copy2(cfg, dest / cfg.name)
        copied.append(cfg.name)
    agents = config_dir() / "AGENTS.md"
    if agents.is_file():
        shutil.copy2(agents, dest / "AGENTS.md")
        copied.append("AGENTS.md")
    commands = config_dir() / "commands"
    if commands.is_dir():
        _copy_if(commands, dest / "commands")
        copied.append("commands")
    if bf_dir().is_dir():
        _copy_if(bf_dir(), dest / "bestfriend")
        copied.append("bestfriend")
    skills_root = config_dir() / "skills"
    if skills_root.is_dir() and meta:
        skill_bak = dest / "skills"
        skill_bak.mkdir(exist_ok=True)
        for name in meta.get("model") or []:
            src = skills_root / name
            if src.is_dir():
                _copy_if(src, skill_bak / name)
        copied.append("skills")
    for helper in ("opencode-bf", "opencode-chromium-cdp"):
        src = bin_dir() / helper
        if src.is_file():
            _copy_if(src, dest / "bin" / helper)
            copied.append(f"bin/{helper}")
    product = share_dir() / "product"
    if product.is_dir():
        _copy_if(product, dest / "product")
        copied.append("product")
    components = share_dir() / "components"
    if components.is_dir():
        _copy_if(components, dest / "components")
        copied.append("components")
    for rc in (".bashrc", ".zshrc"):
        src = home() / rc
        if src.is_file():
            shutil.copy2(src, dest / rc.lstrip("."))
            copied.append(rc)
    claude = snapshot_claude()
    write_json(claude_snapshot_path(), claude)
    write_json(dest / "claude.json", claude)
    write_json(
        dest / "meta.json",
        {
            "stamp": stamp,
            "config": str(cfg) if cfg else None,
            "copied": copied,
            "claude": claude,
            "preInstall": pre,
        },
    )
    return dest


def stage(meta_only: bool = False) -> dict:
    root = repo_root()
    allow, skills, model, manual = load_policy(root)
    stagep = stage_dir()
    if stagep.exists():
        shutil.rmtree(stagep)
    skills_model = stagep / "skills"
    skills_manual = stagep / "bestfriend" / "skills"
    rules_dir = stagep / "bestfriend" / "rules"
    commands_dir = stagep / "commands"
    cfg_dir = stagep / "bestfriend" / "config"
    di_vendor = stagep / "bestfriend" / "design-intelligence"
    docs = stagep / "bestfriend" / "docs"
    for d in (skills_model, skills_manual, rules_dir, commands_dir, cfg_dir, di_vendor, docs):
        d.mkdir(parents=True, exist_ok=True)
    for name in model:
        src = root / "skills" / name
        if not src.is_dir():
            die(f"missing model skill {name}")
        copytree_filtered(src, skills_model / name)
        write_json(
            skills_model / name / ".opencode-bestfriend.json",
            {"owned": True, "name": name, "invocation": "model", "product": "opencode-bestfriend"},
        )
    for name in manual:
        src = root / "manual-skills" / name
        if not src.is_dir():
            die(f"missing manual skill {name}")
        copytree_filtered(src, skills_manual / name)
        write_json(
            skills_manual / name / ".opencode-bestfriend.json",
            {"owned": True, "name": name, "invocation": "manual", "product": "opencode-bestfriend"},
        )
        cmd = root / "commands" / f"{name}.md"
        if not cmd.is_file():
            die(f"missing command {name}")
        shutil.copy2(cmd, commands_dir / f"{name}.md")
    copytree_filtered(root / "rules", rules_dir)
    if (rules_dir / "04-context-guard.md").exists():
        die("context guard rule must not be staged")
    shutil.copy2(root / "templates" / "AGENTS.md", stagep / "AGENTS.md")
    copytree_filtered(root / "design-intelligence", di_vendor)
    notices = root / "THIRD_PARTY_NOTICES.md"
    if notices.is_file():
        shutil.copy2(notices, docs / "THIRD_PARTY_NOTICES.md")
    if (root / "vendor" / "licenses").is_dir():
        copytree_filtered(root / "vendor" / "licenses", docs / "licenses")
    for extra in (
        "provenance.json",
        "sources.json",
        "skill-allowlist.txt",
        "skill-policy.json",
        "mcp-policy.json",
        "mcp-wanted.json",
        "rule-allowlist.txt",
        "license-audit.json",
    ):
        src = root / "vendor" / extra
        if src.is_file():
            shutil.copy2(src, cfg_dir / extra)
    meta = {
        "productVersion": product_version(),
        "allow": allow,
        "model": model,
        "manual": manual,
        "portableRules": sorted(p.name for p in rules_dir.glob("*.md")),
        "excludedRules": ["04-context-guard.md"],
    }
    write_json(stagep / "stage-meta.json", meta)
    info(f"staged model={len(model)} manual={len(manual)} rules={len(meta['portableRules'])}")
    return meta


def validate_stage(meta: dict) -> None:
    errors = []
    stagep = stage_dir()
    for name in meta["model"]:
        p = stagep / "skills" / name / "SKILL.md"
        if not p.is_file():
            errors.append(f"missing model skill {name}")
            continue
        data, _ = parse_frontmatter(p.read_text(encoding="utf-8"))
        if data.get("name") and data.get("name") != name:
            errors.append(f"name mismatch {name}")
        if not NAME_RE.match(name):
            errors.append(f"bad name {name}")
        fm = p.read_text(encoding="utf-8").split("---", 2)
        if len(fm) > 1 and "disable-model-invocation" in fm[1]:
            errors.append(f"claude field leaked {name}")
        desc = data.get("description") or ""
        if desc and not (1 <= len(desc) <= 1024):
            errors.append(f"bad description length {name}={len(desc)}")
        if (stagep / "bestfriend" / "skills" / name / "SKILL.md").is_file():
            errors.append(f"model skill also in manual {name}")
    for name in meta["manual"]:
        p = stagep / "bestfriend" / "skills" / name / "SKILL.md"
        c = stagep / "commands" / f"{name}.md"
        if not p.is_file():
            errors.append(f"missing manual skill {name}")
        if not c.is_file():
            errors.append(f"missing command {name}")
        if (stagep / "skills" / name).exists():
            errors.append(f"manual skill leaked into discovery {name}")
    agents = (stagep / "AGENTS.md").read_text(encoding="utf-8")
    if "@~/" in agents or "@~/.config" in agents:
        errors.append("AGENTS.md contains @ import")
    if agents.count("\n") > 120:
        errors.append(f"AGENTS.md too thick {agents.count(chr(10))} lines")
    if "04-context-guard" in agents or "Context Guard" in agents:
        errors.append("AGENTS.md mentions Context Guard")
    for path in stagep.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in {".md", ".mjs", ".js", ".py", ".json", ".sh", ""}:
            continue
        rel = str(path.relative_to(stagep))
        if "THIRD_PARTY_NOTICES" in rel or rel.endswith("provenance.json") or rel.endswith("sources.json"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for pat in CLAUDE_ACTIVE:
            if pat in text:
                errors.append(f"claude runtime ref in staged {rel}: {pat}")
                break
        if "04-context-guard.md" in rel:
            errors.append(f"context guard staged {rel}")
    if errors:
        die("validation failed:\n  " + "\n  ".join(errors[:40]))
    info("stage validation PASS")


def owned_ok(path: Path) -> bool:
    marker = path / ".opencode-bestfriend.json"
    if marker.is_file():
        return True
    if not path.exists():
        return True
    return False


def preflight_install(meta: dict) -> None:
    cfg = config_dir()
    for name in meta["model"]:
        dest = cfg / "skills" / name
        if dest.exists() and not owned_ok(dest):
            die(f"FOREIGN skill collision {dest}")
        if dest.exists() and dest.is_file():
            die(f"TARGET_NOT_DIRECTORY {dest}")
    for name in meta["manual"]:
        dest = cfg / "commands" / f"{name}.md"
        if dest.exists() and not command_is_owned(dest):
            die(f"FOREIGN command collision {dest}")
        if dest.exists() and dest.is_dir():
            die(f"TARGET_NOT_FILE {dest}")
    for helper in ("opencode-bf", "opencode-chromium-cdp"):
        dest = bin_dir() / helper
        if dest.exists() and not helper_replaceable(dest):
            die(f"FOREIGN helper collision {dest}")
    path = existing_config_path()
    if path:
        try:
            data = jsonc.load_path(path)
        except Exception as exc:
            die(f"OPENCODE_CONFIG_INVALID: {exc}")
        if not isinstance(data, dict):
            die("OPENCODE_CONFIG_INVALID: root is not an object")
    agents = cfg / "AGENTS.md"
    if agents.exists() and not agents.is_file():
        die(f"AGENTS_TARGET_INVALID {agents}")
    for d in (cfg, bin_dir(), share_dir()):
        probe = d if d.exists() else d.parent
        if probe.exists() and not os.access(probe, os.W_OK):
            die(f"TARGET_NOT_WRITABLE {probe}")
    info("preflight PASS")


def helper_is_owned(path: Path) -> bool:
    if not path.is_file():
        return True
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False
    name = path.name
    if name == "opencode-bf":
        return "opencode-bestfriend/product" in text and "lib/cli.py" in text
    if name == "opencode-chromium-cdp":
        return "OpenCodeBestFriend" in text
    return False


def helper_is_legacy_owned(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False
    return any(
        needle in text
        for needle in (
            "opencode_bf.py",
            "OPENCODE_BF_INSTALLER",
            "ClaudeBestFriend",
            "source/ClaudeBestFriend",
        )
    )


def helper_replaceable(path: Path) -> bool:
    return helper_is_owned(path) or helper_is_legacy_owned(path) or not path.exists()


def remove_legacy_installer() -> None:
    inst = share_dir() / "components" / "installer"
    if (inst / "opencode_bf.py").is_file():
        shutil.rmtree(inst)
        info(f"removed leftover ClaudeBestFriend installer {inst}")


def git_head() -> str | None:
    r = run(["git", "rev-parse", "HEAD"], cwd=repo_root())
    if r.returncode == 0:
        return (r.stdout or "").strip() or None
    return None


def install_helpers() -> dict[str, str]:
    bdir = bin_dir()
    bdir.mkdir(parents=True, exist_ok=True)
    dest_cdp = bdir / "opencode-chromium-cdp"
    if dest_cdp.exists() and not helper_replaceable(dest_cdp):
        die(f"FOREIGN helper collision {dest_cdp}")
    shutil.copy2(repo_root() / "bin" / "opencode-chromium-cdp", dest_cdp)
    dest_cdp.chmod(dest_cdp.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    product = share_dir() / "product"
    if product.exists():
        shutil.rmtree(product)
    copytree_filtered(repo_root() / "lib", product / "lib")
    shutil.copy2(repo_root() / "VERSION", product / "VERSION")
    copytree_filtered(repo_root() / "vendor", product / "vendor")
    (product / "bin").mkdir(parents=True, exist_ok=True)
    shutil.copy2(repo_root() / "bin" / "opencode-chromium-cdp", product / "bin" / "opencode-chromium-cdp")
    wrapper = bdir / "opencode-bf"
    if wrapper.exists() and not helper_replaceable(wrapper):
        die(f"FOREIGN helper collision {wrapper}")
    wrapper.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        'ROOT="${OPENCODE_BF_ROOT:-$HOME/.local/share/opencode-bestfriend/product}"\n'
        'exec python3 "$ROOT/lib/cli.py" "$@"\n',
        encoding="utf-8",
    )
    wrapper.chmod(wrapper.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return {"opencode-bf": str(wrapper), "opencode-chromium-cdp": str(dest_cdp)}


def apply(meta: dict, cbm_bin: Path, bank: tuple[str | None, str, str]) -> list[str]:
    owned: list[str] = []
    stagep = stage_dir()
    cfg = config_dir()
    bf = bf_dir()

    def take(src: Path, dest: Path) -> None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.is_dir():
            shutil.rmtree(dest)
        if src.is_dir():
            shutil.copytree(src, dest)
        else:
            shutil.copy2(src, dest)
        owned.append(str(dest))

    for name in meta["model"]:
        dest = cfg / "skills" / name
        if dest.exists() and not owned_ok(dest):
            die(f"FOREIGN skill collision {dest}")
        take(stagep / "skills" / name, dest)
    skills_root = cfg / "skills"
    if skills_root.is_dir():
        for child in skills_root.iterdir():
            if child.is_dir() and (child / ".opencode-bestfriend.json").is_file():
                if child.name not in meta["model"]:
                    shutil.rmtree(child)
    for name in meta["manual"]:
        take(stagep / "bestfriend" / "skills" / name, bf / "skills" / name)
    commands_root = cfg / "commands"
    commands_root.mkdir(parents=True, exist_ok=True)
    for name in meta["manual"]:
        dest = commands_root / f"{name}.md"
        if dest.exists() and not command_is_owned(dest):
            die(f"FOREIGN command collision {dest}")
        take(stagep / "commands" / f"{name}.md", dest)
    for child in commands_root.glob("*.md"):
        if not command_is_owned(child):
            continue
        if child.stem not in meta["manual"]:
            child.unlink()
    agents_dest = cfg / "AGENTS.md"
    existing_agents = agents_dest.read_text(encoding="utf-8") if agents_dest.is_file() else ""
    block = (stagep / "AGENTS.md").read_text(encoding="utf-8")
    agents_dest.parent.mkdir(parents=True, exist_ok=True)
    agents_dest.write_text(merge_agents_md(existing_agents, block), encoding="utf-8")
    owned.append(str(agents_dest))
    take(stagep / "bestfriend" / "rules", bf / "rules")
    take(stagep / "bestfriend" / "design-intelligence", bf / "design-intelligence")
    take(stagep / "bestfriend" / "docs", bf / "docs")
    take(stagep / "bestfriend" / "config", bf / "config")
    impec_di = cfg / "skills" / "impeccable" / "scripts" / "design_intelligence"
    if impec_di.is_dir():
        take(impec_di, share_dir() / "components" / "design-intelligence")
    bank_root, bank_source, bank_mode = bank
    if bank_root:
        ownership = "owned-download" if bank_mode == "owned-download" else "foreign-read-only"
        write_json(
            bf / "config" / "design-bank.json",
            {
                "root": bank_root,
                "catalogs": ["Refero/bank/catalog.json", "motionsites/library/catalog.json"],
                "discoveredAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "source": bank_source,
                "ownership": ownership,
            },
        )
        owned.append(str(bf / "config" / "design-bank.json"))
    write_json(
        bf / "config" / "chromium.json",
        {
            "host": "127.0.0.1",
            "port": 9223,
            "engine": "chromium",
            "refuse": "google-chrome",
            "helper": str(bin_dir() / "opencode-chromium-cdp"),
        },
    )
    helpers = install_helpers()
    owned.extend(helpers.values())
    remove_legacy_installer()
    merge_opencode_config(cbm_bin)
    ensure_shell_isolation()
    oc = which("opencode") or os.environ.get("OPENCODE_BF_MOCK_OPENCODE") or "opencode"
    ver = run([oc, "--version"]).stdout.strip()
    legacy = meta.get("legacy")
    man = {
        "schemaVersion": 1,
        "product": EXPECTED_PRODUCT,
        "productVersion": meta["productVersion"],
        "sourceRepository": EXPECTED_REPO,
        "adaptedFrom": {
            "product": "ClaudeBestFriend",
            "version": "1.4.2-claude.1",
            "commit": "05e6fdcdb70fe7f4420827e4df1a360f2152700c",
        },
        "installedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sourceCommit": git_head(),
        "opencodeVersion": ver,
        "schema": "opencode-1.18 mcp.<name>",
        "ownedFiles": owned,
        "ownedDirectories": [str(cfg / "skills"), str(cfg / "commands"), str(bf), str(share_dir())],
        "skills": meta["allow"],
        "modelInvokedSkills": meta["model"],
        "manualSkills": meta["manual"],
        "ownedMcp": list(OWNED_MCP),
        "optionalMcp": ["serena", "exa"],
        "designBank": {
            "root": bank_root,
            "source": bank_source,
            "mode": bank_mode,
            "ownership": "owned-download" if bank_mode == "owned-download" else "foreign-read-only",
        },
        "helpers": helpers | {"codebase-memory-mcp": str(cbm_bin)},
        "exclusions": {
            "contextGuard": "NOT_PORTED_BY_DESIGN",
            "claudeHooks": "NOT_PORTED",
            "claudeRuntimeConfig": "NOT_IMPORTED",
            "opencodeCompaction": "UNCHANGED",
        },
    }
    if legacy:
        man["migration"] = {
            "fromProduct": legacy.get("fromProduct"),
            "fromVersion": legacy.get("fromVersion"),
        }
    write_json(bf / "manifests" / "ownership.json", man)
    build_integrity_manifest()
    write_json(state_dir() / "install.json", {"status": "APPLIED", "manifest": str(bf / "manifests" / "ownership.json")})
    return owned


def plan_text(meta: dict, mcp_plan: dict, bank: tuple, cbm: str) -> str:
    lines = [
        "=== OpenCodeBestFriend dry-run ===",
        f"product {meta['productVersion']}",
        f"skills TOTAL {len(meta['allow'])} MODEL {len(meta['model'])} MANUAL {len(meta['manual'])}",
        f"rules {len(meta['portableRules'])} (04-context-guard EXCLUDED_BY_DESIGN)",
        f"MCP add={mcp_plan['add']} update={mcp_plan['update']} preserve={mcp_plan['preserve']}",
        f"Codebase Memory -> {cbm}",
        f"Design Bank {bank[2]} source={bank[1]} root={bank[0]}",
        "owned mutations: skills, commands, AGENTS.md, rules, Design Intelligence, helpers, isolation env",
        "never: provider/model/auth/compaction, ~/.claude, Exa, foreign MCP",
    ]
    return "\n".join(lines)


def verify_install() -> int:
    from .doctor import cmd_design_intelligence, cmd_skills_verify, isolation_check

    if os.environ.get("OPENCODE_BF_FORCE_VERIFY_FAIL") == "1":
        warn("VERIFY_FAILED forced")
        return 1
    failed = 0
    if verify_owned_runtime() != 0:
        failed += 1
        warn("owned runtime identity/integrity failed")
    if cmd_skills_verify() != 0:
        failed += 1
        warn("skills verify failed")
    path = existing_config_path()
    if not path:
        warn("opencode config missing after apply")
        failed += 1
    else:
        try:
            data = jsonc.load_path(path)
        except Exception as exc:
            warn(f"config parse failed: {exc}")
            failed += 1
            data = {}
        mcp = data.get("mcp") or {}
        for name in OWNED_MCP:
            if name not in mcp:
                warn(f"mcp {name} missing")
                failed += 1
    agents = config_dir() / "AGENTS.md"
    if not agents.is_file() or AGENTS_BEGIN not in agents.read_text(encoding="utf-8"):
        warn("AGENTS.md missing owned marker block")
        failed += 1
    failed += cmd_design_intelligence()
    failed += isolation_check()
    snap_path = claude_snapshot_path()
    snap = load_json(snap_path) if snap_path.is_file() else {}
    status, evidence, _n = compare_claude_snapshot(snap)
    if status == "FAIL":
        warn(f"claude mutations {evidence}")
        failed += 1
    return 1 if failed else 0


def cmd_install(dry_run: bool = False, skip_design_bank: bool = False, offline: bool = False, recover: bool = False) -> int:
    if recover:
        return cmd_recover()
    oc, ver, schema = detect_opencode()
    info(f"OpenCode {ver[0]}.{ver[1]}.{ver[2]} schema={schema} bin={oc}")
    if dry_run:
        allow, _, model, manual = load_policy()
        meta = {
            "productVersion": product_version(),
            "allow": allow,
            "model": model,
            "manual": manual,
            "portableRules": [p.name for p in (repo_root() / "rules").glob("*.md")],
        }
        found = discover_design_bank()
        if found:
            bank = (found[0], found[1], "reuse-read-only")
        elif skip_design_bank:
            bank = (None, "skipped", "DEGRADED_DESIGN_BANK")
        elif offline:
            bank = (None, "offline", "DEGRADED_DESIGN_BANK")
        else:
            bank = ("(would download upstream Design-bank.tgz)", "download", "owned-download")
        cbm = Path(os.environ.get("OPENCODE_BF_TEST_CBM") or "/nonexistent/codebase-memory-mcp")
        mcp_plan = merge_opencode_config(cbm, dry_run=True)
        print(plan_text(meta, mcp_plan, bank, "download-or-reuse 0.9.0"))
        print("DRY_RUN_NO_MUTATION")
        return 0
    set_transaction("PREPARING")
    legacy = detect_legacy_overlay()
    if legacy:
        info(
            f"MIGRATION_DETECTED {legacy.get('fromProduct')} {legacy.get('fromVersion')} "
            f"→ OpenCodeBestFriend {product_version()}"
        )
    meta = stage()
    meta["legacy"] = legacy
    set_transaction("STAGED", {"skills": len(meta["allow"])})
    validate_stage(meta)
    set_transaction("VALIDATED")
    preflight_install(meta)
    stamp = time.strftime("%Y%m%dT%H%M%SZ")
    backup_relevant(stamp, meta)
    set_transaction("BACKED_UP", {"stamp": stamp})
    cbm = download_codebase_memory(offline=offline)
    bank = resolve_design_bank(skip=skip_design_bank, offline=offline)
    apply(meta, cbm, bank)
    set_transaction("APPLIED", {"stamp": stamp})
    if verify_install() != 0:
        warn("VERIFY_FAILED — transaction stays APPLIED. Run ./install.sh --recover")
        return 1
    set_transaction("VERIFIED", {"stamp": stamp})
    write_json(state_dir() / "install.json", {"status": "COMMITTED", "manifest": str(bf_dir() / "manifests" / "ownership.json")})
    set_transaction("COMMITTED", {"stamp": stamp})
    info("APPLY_DONE")
    if bank[2] == "DEGRADED_DESIGN_BANK":
        warn("DEGRADED_DESIGN_BANK — core install complete; Design Bank catalogs missing")
    info("Restart OpenCode (config is not hot-reloaded). New shells pick up OPENCODE_DISABLE_CLAUDE_CODE=1.")
    return 0


def cmd_recover() -> int:
    path = transaction_path()
    if not path.is_file():
        info("no transaction")
        return 0
    data = load_json(path)
    if data.get("status") == "COMMITTED":
        info("transaction already COMMITTED")
        return 0
    stamp = data.get("stamp")
    if stamp:
        cmd_restore(stamp)
    else:
        warn("STALE_TRANSACTION without backup stamp; refusing blind rollback")
        return 1
    set_transaction("ROLLED_BACK")
    return 0


def cmd_uninstall(purge_owned_bank: bool = False, yes: bool = False) -> int:
    man_path = bf_dir() / "manifests" / "ownership.json"
    if not man_path.is_file():
        die("no ownership manifest; refusing to uninstall")
    man = load_json(man_path)
    cfg_path = existing_config_path()
    if cfg_path and cfg_path.is_file():
        raw = cfg_path.read_text(encoding="utf-8")
        names: list[str] = list(man.get("ownedMcp") or list(OWNED_MCP))
        if jsonc.contains_comments(raw):
            try:
                merged = jsonc.remove_mcp_servers(raw, names)
                jsonc.loads(merged)
                cfg_path.write_text(merged if merged.endswith("\n") else merged + "\n", encoding="utf-8")
            except Exception as exc:
                die(f"OPENCODE_CONFIG_JSONC_SURGICAL_FAILED: {exc}")
        else:
            data = jsonc.loads(raw)
            mcp = data.get("mcp") or {}
            for name in names:
                mcp.pop(name, None)
            data["mcp"] = mcp
            cfg_path.write_text(jsonc.dumps(data), encoding="utf-8")
    cfg = config_dir()
    for name in man.get("modelInvokedSkills") or []:
        if not NAME_RE.fullmatch(str(name)):
            warn(f"skipping invalid owned skill name {name!r}")
            continue
        d = cfg / "skills" / name
        if d.is_dir() and (d / ".opencode-bestfriend.json").is_file():
            shutil.rmtree(d)
    for name in man.get("manualSkills") or []:
        if not NAME_RE.fullmatch(str(name)):
            warn(f"skipping invalid owned skill name {name!r}")
            continue
        d = bf_dir() / "skills" / name
        if d.is_dir():
            shutil.rmtree(d)
        c = cfg / "commands" / f"{name}.md"
        if c.is_file() and command_is_owned(c):
            c.unlink()
    agents = cfg / "AGENTS.md"
    if agents.is_file() and AGENTS_BEGIN in agents.read_text(encoding="utf-8"):
        leftover = strip_agents_block(agents.read_text(encoding="utf-8"))
        if leftover.strip():
            agents.write_text(leftover, encoding="utf-8")
        else:
            agents.unlink()
    if bf_dir().is_dir():
        shutil.rmtree(bf_dir())
    for helper in ("opencode-bf", "opencode-chromium-cdp"):
        p = bin_dir() / helper
        if p.is_file() and helper_is_owned(p):
            p.unlink()
    product = share_dir() / "product"
    if product.is_dir():
        shutil.rmtree(product)
    components = share_dir() / "components"
    if components.is_dir():
        shutil.rmtree(components)
    bank = man.get("designBank") or {}
    owned_bank = share_dir() / "design-bank"
    if bank.get("mode") == "owned-download" and owned_bank.is_dir():
        if purge_owned_bank:
            shutil.rmtree(owned_bank)
        else:
            warn(f"leaving owned Design Bank at {owned_bank} (pass --purge-owned-design-bank to delete)")
    strip_shell_isolation()
    info("UNINSTALL_DONE (foreign MCP, provider, models, user Design trees preserved)")
    return 0


def cmd_restore_list() -> int:
    root = backups_dir()
    if not root.is_dir():
        print("no backups")
        return 0
    for p in sorted(root.iterdir()):
        if p.is_dir():
            print(p.name)
    return 0


def _remove_created(live: Path, backup: Path, is_dir: bool = False) -> None:
    if backup.exists() or not live.exists():
        return
    if is_dir:
        shutil.rmtree(live)
    else:
        live.unlink()
    info(f"removed installer-created {live}")


def cmd_restore(stamp: str) -> int:
    src = resolve_backup_stamp(stamp, backups_dir())
    meta_path = src / "meta.json"
    pre = load_json(meta_path).get("preInstall") or {} if meta_path.is_file() else {}
    cfg = config_dir()
    cfg.mkdir(parents=True, exist_ok=True)
    for name in ("opencode.jsonc", "opencode.json", "AGENTS.md"):
        s = src / name
        if s.is_file():
            shutil.copy2(s, cfg / name)
            info(f"restored {name}")
    if (src / "commands").is_dir():
        dest = cfg / "commands"
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src / "commands", dest)
        info("restored commands")
    if (src / "bestfriend").is_dir():
        dest = bf_dir()
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src / "bestfriend", dest)
        info("restored bestfriend")
    elif bf_dir().is_dir():
        shutil.rmtree(bf_dir())
    bak_skills = src / "skills"
    live_skills = cfg / "skills"
    if live_skills.is_dir():
        for child in list(live_skills.iterdir()):
            if child.is_dir() and (child / ".opencode-bestfriend.json").is_file():
                if bak_skills.is_dir() and (bak_skills / child.name).is_dir():
                    if child.exists():
                        shutil.rmtree(child)
                    shutil.copytree(bak_skills / child.name, child)
                else:
                    shutil.rmtree(child)
    if bak_skills.is_dir():
        live_skills.mkdir(parents=True, exist_ok=True)
        for child in bak_skills.iterdir():
            if child.is_dir() and not (live_skills / child.name).exists():
                shutil.copytree(child, live_skills / child.name)
    for helper in ("opencode-bf", "opencode-chromium-cdp"):
        s = src / "bin" / helper
        dest = bin_dir() / helper
        if s.is_file():
            shutil.copy2(s, dest)
            dest.chmod(dest.stat().st_mode | stat.S_IXUSR)
        elif dest.is_file() and dest.read_text(encoding="utf-8", errors="ignore").find("opencode-bestfriend") != -1:
            dest.unlink()
    for rc in ("bashrc", "zshrc"):
        s = src / rc
        if s.is_file():
            shutil.copy2(s, home() / f".{rc}")
            info(f"restored .{rc}")
    if pre.get("config") == "absent":
        for name in ("opencode.jsonc", "opencode.json"):
            _remove_created(cfg / name, src / name)
    if pre.get("agents") == "absent":
        _remove_created(cfg / "AGENTS.md", src / "AGENTS.md")
    if pre.get("commands") == "absent":
        _remove_created(cfg / "commands", src / "commands", is_dir=True)
    if pre.get("bestfriend") == "absent":
        _remove_created(bf_dir(), src / "bestfriend", is_dir=True)
    if pre.get("bashrc") == "absent":
        _remove_created(home() / ".bashrc", src / "bashrc")
    if pre.get("zshrc") == "absent":
        _remove_created(home() / ".zshrc", src / "zshrc")
    helpers_pre = pre.get("helpers") or {}
    for helper in ("opencode-bf", "opencode-chromium-cdp"):
        if helpers_pre.get(helper) == "absent":
            _remove_created(bin_dir() / helper, src / "bin" / helper)
    if (src / "product").is_dir():
        dest_p = share_dir() / "product"
        if dest_p.exists():
            shutil.rmtree(dest_p)
        shutil.copytree(src / "product", dest_p)
        info("restored product")
    elif pre.get("shareProduct") == "absent":
        product = share_dir() / "product"
        if product.is_dir():
            shutil.rmtree(product)
            info(f"removed installer-created {product}")
    if (src / "components").is_dir():
        dest_c = share_dir() / "components"
        if dest_c.exists():
            shutil.rmtree(dest_c)
        shutil.copytree(src / "components", dest_c)
        info("restored components")
    elif pre.get("shareComponents") == "absent":
        components = share_dir() / "components"
        if components.is_dir():
            shutil.rmtree(components)
            info(f"removed installer-created {components}")
    info(f"RESTORE_DONE {stamp}")
    return 0


def cmd_serena_enable() -> int:
    serena = which("serena")
    if not serena:
        die("serena not on PATH")
    spec = {
        "type": "local",
        "command": [serena, "start-mcp-server", "--context", "agent", "--project-from-cwd"],
        "enabled": True,
    }
    path = target_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.is_file():
        path.write_text(
            jsonc.dumps({"$schema": "https://opencode.ai/config.json", "mcp": {"serena": spec}}),
            encoding="utf-8",
        )
        info(f"enabled serena MCP in {path}")
        return 0
    raw = path.read_text(encoding="utf-8")
    try:
        data = jsonc.loads(raw)
    except Exception as exc:
        die(f"OPENCODE_CONFIG_INVALID: {exc}")
    if not isinstance(data, dict):
        die("OPENCODE_CONFIG_INVALID: root is not an object")
    mcp = data.get("mcp") or {}
    if not isinstance(mcp, dict):
        die("OPENCODE_CONFIG_INVALID mcp")
    if "serena" in mcp:
        info("serena MCP already present; not overwriting")
        return 0
    if jsonc.contains_comments(raw):
        try:
            merged = jsonc.upsert_mcp_servers(raw, {"serena": spec})
            jsonc.loads(merged)
            path.write_text(merged if merged.endswith("\n") else merged + "\n", encoding="utf-8")
        except Exception as exc:
            die(f"OPENCODE_CONFIG_JSONC_SURGICAL_FAILED: {exc}")
    else:
        data.setdefault("mcp", {})["serena"] = spec
        path.write_text(jsonc.dumps(data), encoding="utf-8")
    info(f"enabled serena MCP in {path}")
    return 0
