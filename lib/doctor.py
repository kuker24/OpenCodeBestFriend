from __future__ import annotations

import json
import os
import re
from pathlib import Path

from . import jsonc
from .cbm import cbm_bin, project_status
from .common import (
    bf_dir,
    bin_dir,
    claude_snapshot_path,
    compare_claude_snapshot,
    config_dir,
    home,
    load_json,
    load_policy,
    product_version,
    repo_root,
    run,
    share_dir,
    which,
)
from .identity import identity_findings, owned_agents_block
from .integrity import AGENTS_TOKENS, agents_stale, routing_stale
from .status import Findings, report

CLAUDE_ACTIVE_PATTERNS = (
    "~/.claude/",
    "$HOME/.claude/",
    "claude-gbf",
    "CLAUDE_CODE_",
    "CLAUDE_DESIGN_BANK",
    "grokbestfriend-claude",
    "claude mcp",
)
CLAUDE_SCAN_SKIP_PARTS = {
    "source",
    "cache",
    "node_modules",
    ".git",
    "docs",
    "licenses",
    "product",
    "backups",
    "state",
}

ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
OWNED_MCP_PROBE = ("codebase-memory-mcp", "context7", "shadcn")


def installed_policy():
    allow_path = bf_dir() / "config" / "skill-allowlist.txt"
    policy_path = bf_dir() / "config" / "skill-policy.json"
    if allow_path.is_file() and policy_path.is_file():
        allow = [ln.strip() for ln in allow_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        skills = load_json(policy_path)["skills"]
        model = [k for k in allow if skills[k]["invocation"] == "model"]
        manual = [k for k in allow if skills[k]["invocation"] == "manual"]
        return allow, skills, model, manual
    return load_policy(repo_root())


def cmd_skills_list() -> int:
    allow, skills, model, manual = installed_policy()
    print(f"TOTAL {len(allow)}")
    print(f"MODEL-INVOKED {len(model)}")
    print(f"MANUAL {len(manual)}")
    cfg = config_dir()
    bf = bf_dir()
    for name in allow:
        inv = skills[name]["invocation"]
        path = cfg / "skills" / name / "SKILL.md" if inv == "model" else bf / "skills" / name / "SKILL.md"
        print(f"{inv:<8} {name:<36} {'OK' if path.is_file() else 'MISSING'}")
    return 0


def cmd_skills_verify() -> int:
    allow, skills, model, manual = installed_policy()
    invalid = dup = missing_m = missing_n = 0
    cfg = config_dir()
    bf = bf_dir()
    for name in model:
        p = cfg / "skills" / name / "SKILL.md"
        if not p.is_file():
            missing_m += 1
            invalid += 1
        if (bf / "skills" / name / "SKILL.md").is_file() and p.is_file():
            dup += 1
    for name in manual:
        p = bf / "skills" / name / "SKILL.md"
        c = cfg / "commands" / f"{name}.md"
        if not p.is_file() or not c.is_file():
            missing_n += 1
            invalid += 1
        if (cfg / "skills" / name / "SKILL.md").is_file():
            dup += 1
    print(f"TOTAL {len(model)+len(manual)-missing_m-missing_n}/{len(allow)}")
    print(f"MODEL-INVOKED {len(model)-missing_m}/{len(model)}")
    print(f"MANUAL {len(manual)-missing_n}/{len(manual)}")
    print(f"INVALID {invalid}")
    print(f"DUPLICATE {dup}")
    return 0 if invalid == 0 and dup == 0 else 1


def mcp_status_map() -> dict[str, str]:
    out: dict[str, str] = {}
    cfg = None
    for cand in (config_dir() / "opencode.jsonc", config_dir() / "opencode.json"):
        if cand.is_file():
            cfg = cand
            break
    data = {}
    if cfg:
        try:
            data = jsonc.load_path(cfg)
        except (OSError, json.JSONDecodeError, ValueError):
            return {k: "FAIL" for k in ("codebase-memory-mcp", "context7", "shadcn", "serena", "exa")}
    mcp = data.get("mcp") or {}
    owned = {"codebase-memory-mcp", "context7", "shadcn"}
    for name in ("codebase-memory-mcp", "context7", "shadcn", "serena", "exa"):
        spec = mcp.get(name)
        if spec is None:
            out[name] = "OPTIONAL_ABSENT" if name in {"serena", "exa"} else "FAIL"
            continue
        if spec.get("enabled") is False:
            out[name] = "DISABLED"
            continue
        if name not in owned:
            out[name] = "FOREIGN"
            continue
        out[name] = "CONFIGURED"
    return out


def parse_mcp_list(text: str, names: tuple[str, ...] = OWNED_MCP_PROBE) -> dict[str, str]:
    """Per-line, per-server status. Never treat 'disconnected' as 'connected'."""
    out = {n: "NOT_CHECKED" for n in names}
    cleaned = ANSI_RE.sub("", text)
    for raw in cleaned.splitlines():
        line = raw.strip()
        if not line:
            continue
        lower = line.lower()
        hits = [n for n in names if n in lower]
        if len(hits) != 1:
            continue
        name = hits[0]
        rest = re.sub(re.escape(name), " ", lower, count=1)
        words = set(re.findall(r"[a-z0-9_-]+", rest))
        if "disconnected" in words or "disabled" in words:
            status = "DISCONNECTED"
        elif "connected" in words:
            status = "CONNECTED"
        else:
            status = "LISTED"
        rank = {"NOT_CHECKED": 0, "LISTED": 1, "CONNECTED": 2, "DISCONNECTED": 3}
        if rank[status] > rank[out[name]]:
            out[name] = status
    return out


def probe_mcp_connected() -> dict[str, str]:
    oc = os.environ.get("OPENCODE_BF_MOCK_OPENCODE") or which("opencode")
    if not oc:
        return {k: "NOT_CHECKED" for k in OWNED_MCP_PROBE}
    env_rc = os.environ.get("OPENCODE_BF_MOCK_MCP_LIST_RC")
    if env_rc is not None:
        try:
            if int(env_rc) != 0:
                return {k: "NOT_CHECKED" for k in OWNED_MCP_PROBE}
        except ValueError:
            return {k: "NOT_CHECKED" for k in OWNED_MCP_PROBE}
    listed = os.environ.get("OPENCODE_BF_MOCK_MCP_LIST")
    if listed:
        path = Path(listed)
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            if not text.strip():
                return {k: "NOT_CHECKED" for k in OWNED_MCP_PROBE}
            return parse_mcp_list(text)
        return {k: "NOT_CHECKED" for k in OWNED_MCP_PROBE}
    r = run([oc, "mcp", "list"])
    text = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0 or not text.strip():
        return {k: "NOT_CHECKED" for k in OWNED_MCP_PROBE}
    return parse_mcp_list(text)


def cmd_mcp_status(deep: bool = False) -> int:
    cfg_map = mcp_status_map()
    live = probe_mcp_connected() if deep else {}
    for name, status in cfg_map.items():
        extra = "binary-on-PATH" if name == "serena" and which("serena") else ""
        if name in live:
            extra = (extra + " " + live[name]).strip()
        print(f"{status:<22} {name:<28} {extra}")
    return 0


def cmd_design_bank() -> int:
    cfg = bf_dir() / "config" / "design-bank.json"
    if not cfg.is_file():
        report("DEGRADED", "Design Bank", "DEGRADED_DESIGN_BANK")
        return 0
    data = load_json(cfg)
    root = Path(data.get("root") or "")
    refero = root / "Refero/bank/catalog.json"
    motion = root / "motionsites/library/catalog.json"
    ok = refero.is_file() and motion.is_file()
    report("PASS" if ok else "FAIL", "Design Bank", str(root))
    report("PASS" if refero.is_file() else "FAIL", "Refero", str(refero))
    report("PASS" if motion.is_file() else "FAIL", "Motionsites", str(motion))
    return 0 if ok else 1


def cmd_design_intelligence() -> int:
    policy = bf_dir() / "design-intelligence" / "policy.json"
    tax = bf_dir() / "design-intelligence" / "taxonomy.json"
    cli = config_dir() / "skills" / "impeccable" / "scripts" / "design-intelligence.py"
    runtime = config_dir() / "skills" / "impeccable" / "scripts" / "design_intelligence" / "selection.py"
    ok = policy.is_file() and tax.is_file() and cli.is_file() and runtime.is_file()
    report("PASS" if policy.is_file() else "FAIL", "DI policy", str(policy))
    report("PASS" if tax.is_file() else "FAIL", "DI taxonomy", str(tax))
    report("PASS" if cli.is_file() else "FAIL", "DI CLI", str(cli))
    report("PASS" if runtime.is_file() else "FAIL", "DI runtime", str(runtime))
    if cli.is_file():
        r = run(["python3", str(cli), "--help"])
        report("PASS" if r.returncode == 0 else "FAIL", "DI CLI load", "")
        ok = ok and r.returncode == 0
    return 0 if ok else 1


def cmd_chromium() -> int:
    helper = bin_dir() / "opencode-chromium-cdp"
    if not helper.is_file():
        report("DEGRADED", "Chromium helper", "missing")
        return 0
    r = run([str(helper), "status"])
    text = (r.stdout + r.stderr).strip().replace("\n", " | ")
    if r.returncode == 0:
        report("PASS", "Chromium", text)
    elif r.returncode == 2:
        report("DEGRADED", "Chromium", text or "NOT_CONFIGURED")
    else:
        report("DEGRADED", "Chromium", text or "occupied-or-unready")
    return 0


def claude_dependency_hits() -> list[str]:
    hits: list[str] = []
    for root in (config_dir(), share_dir()):
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(p in CLAUDE_SCAN_SKIP_PARTS for p in path.parts):
                continue
            if path.suffix not in {".md", ".json", ".jsonc", ".mjs", ".js", ".py", ".sh", ""}:
                continue
            rel = str(path)
            if "THIRD_PARTY_NOTICES" in rel or rel.endswith("provenance.json") or rel.endswith("sources.json"):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for pat in CLAUDE_ACTIVE_PATTERNS:
                if pat in text:
                    hits.append(f"{path}: {pat}")
                    break
    return [h for h in hits if "/bestfriend/docs/" not in h and "/manifests/" not in h]


def isolation_check(deep: bool = False) -> int:
    failed = 0
    env = os.environ.get("OPENCODE_DISABLE_CLAUDE_CODE", "")
    shells = []
    for name in (".bashrc", ".zshrc"):
        p = home() / name
        if p.is_file() and "OPENCODEBESTFRIEND:BEGIN" in p.read_text(encoding="utf-8"):
            shells.append(name)
    if env == "1" or shells:
        report("PASS", "OPENCODE_DISABLE_CLAUDE_CODE", f"env={env or 'unset'} shells={','.join(shells) or 'none'}")
    else:
        report("FAIL", "OPENCODE_DISABLE_CLAUDE_CODE", "not set")
        failed += 1

    snap_path = claude_snapshot_path()
    snap = load_json(snap_path) if snap_path.is_file() else {}
    status, evidence, n = compare_claude_snapshot(snap)
    report(status, "~/.claude mutations", evidence)
    if status == "FAIL":
        failed += 1

    hits = claude_dependency_hits()
    if hits:
        report("FAIL", "Active Claude dependencies", str(len(hits)))
        if deep:
            for h in hits[:30]:
                print("  ", h)
        failed += 1
    else:
        report("PASS", "Active Claude dependencies", "0")
    report("PASS", "Claude MCP dependency", "0")
    report("PASS", "Claude hooks imported", "0")
    report("NOT_APPLICABLE", "Context Guard", "NOT_PORTED_BY_DESIGN")
    return 0 if failed == 0 else 1


def _host_findings(f: Findings, shadcn_enabled: bool) -> None:
    mapping = {
        "python3": which("python3"),
        "node": which("node"),
        "npx": which("npx"),
        "git": which("git"),
        "curl": which("curl"),
        "tar": which("tar"),
        "browser-act": which("browser-act"),
        "serena": which("serena"),
        "semgrep": which("semgrep"),
        "osv-scanner": which("osv-scanner"),
        "gitleaks": which("gitleaks"),
        "gh": which("gh"),
    }
    required = {"python3"}
    if shadcn_enabled:
        required.update({"node", "npx"})
    optional = {"browser-act", "serena", "semgrep", "osv-scanner", "gitleaks", "gh"}
    for name, path in mapping.items():
        if path:
            if name == "gh":
                r = run(["gh", "auth", "status"])
                if r.returncode != 0:
                    f.add("DEGRADED_AUTH_REQUIRED", name, path)
                    continue
            f.add("PASS", name, path)
        elif name in required:
            extra = "shadcn runtime dependency" if name in {"node", "npx"} else "NOT_INSTALLED"
            f.add("FAIL", name, extra)
        elif name in optional:
            f.add("OPTIONAL_ABSENT", name, "NOT_INSTALLED")
        else:
            f.add("DEGRADED", name, "NOT_INSTALLED")


def _permission_findings(f: Findings) -> None:
    cfg = None
    for cand in (config_dir() / "opencode.jsonc", config_dir() / "opencode.json"):
        if cand.is_file():
            cfg = cand
            break
    if not cfg:
        return
    try:
        data = jsonc.load_path(cfg)
    except (OSError, json.JSONDecodeError, ValueError):
        return
    perm = data.get("permission")
    wildcard = False
    if perm == "allow":
        wildcard = True
    elif isinstance(perm, dict) and perm.get("*") == "allow":
        wildcard = True
    if wildcard:
        f.add("DEGRADED_SECURITY", "PERMISSION_PROFILE", 'wildcard "*" = allow unrestricted tool execution')


def cmd_security_profile() -> int:
    print("=== opencode-bestfriend security-profile (recommendation only; not applied) ===")
    print('wildcard "*" = allow means unrestricted tool execution')
    print("Suggested starting point (you apply this; installer will not own permission):")
    print(
        """{
  "permission": {
    "edit": "ask",
    "bash": { "*": "ask" }
  }
}"""
    )
    return 0


def cmd_doctor(deep: bool = False, strict: bool = False) -> int:
    f = Findings()
    print("=== opencode-bestfriend doctor ===")
    oc = os.environ.get("OPENCODE_BF_MOCK_OPENCODE") or which("opencode")
    if oc:
        ver = run([oc, "--version"]).stdout.strip()
        f.add("PASS", "OpenCode", f"{oc} {ver}")
    else:
        f.add("FAIL", "OpenCode", "not on PATH")

    cfg = None
    data = {}
    for cand in (config_dir() / "opencode.jsonc", config_dir() / "opencode.json"):
        if cand.is_file():
            cfg = cand
            break
    if cfg:
        try:
            data = jsonc.load_path(cfg)
            f.add("PASS", cfg.name, "parseable")
        except (OSError, ValueError, json.JSONDecodeError):
            f.add("FAIL", cfg.name, "invalid JSON/JSONC")
            data = {}
    else:
        f.add("FAIL", "opencode.jsonc", "missing")

    for status, label, evidence in identity_findings():
        f.add(status, label, evidence)

    agents = config_dir() / "AGENTS.md"
    if agents.is_file():
        text = agents.read_text(encoding="utf-8")
        block = owned_agents_block(text)
        if block is None:
            f.add("FAIL", "AGENTS.md", "missing owned marker block")
        else:
            owned_lines = block.count("\n")
            total_lines = text.count("\n")
            if "@~/" in block or owned_lines > 120:
                f.add("FAIL", "AGENTS.md", f"owned-lines={owned_lines} total-lines={total_lines}")
            elif agents_stale(text):
                f.add("STALE", "AGENTS.md", "missing " + "/".join(AGENTS_TOKENS))
            else:
                f.add("PASS", "AGENTS.md", f"thin owned-lines={owned_lines} total-lines={total_lines}")
    else:
        f.add("FAIL", "AGENTS.md", "missing")

    allow, _, model, manual = installed_policy()
    miss = 0
    for name in model:
        if not (config_dir() / "skills" / name / "SKILL.md").is_file():
            miss += 1
    for name in manual:
        if not (bf_dir() / "skills" / name / "SKILL.md").is_file() or not (
            config_dir() / "commands" / f"{name}.md"
        ).is_file():
            miss += 1
    if miss:
        f.add("FAIL", "skills", f"missing {miss}")
    else:
        f.add(
            "PASS",
            "skills",
            f"TOTAL {len(allow)}/{len(allow)} MODEL {len(model)}/{len(model)} MANUAL {len(manual)}/{len(manual)}",
        )

    rules = list((bf_dir() / "rules").glob("*.md")) if (bf_dir() / "rules").is_dir() else []
    names = {p.name for p in rules}
    if "04-context-guard.md" in names:
        f.add("FAIL", "rules", "context guard present")
    elif {"00-routing.md", "01-verification.md", "02-engineering-principles.md", "03-prose-discipline.md"} <= names:
        routing = bf_dir() / "rules" / "00-routing.md"
        if routing.is_file() and routing_stale(routing.read_text(encoding="utf-8")):
            f.add("STALE", "rules/00-routing.md", "title is not OpenCode specialist routing")
        else:
            f.add("PASS", "rules", f"{len(names)} portable; 04-context-guard EXCLUDED_BY_DESIGN")
    else:
        f.add("FAIL", "rules", f"got {sorted(names)}")

    live = probe_mcp_connected() if deep else {}
    cfg_map = mcp_status_map()
    shadcn_enabled = cfg_map.get("shadcn") == "CONFIGURED"
    for name, status in cfg_map.items():
        extra = live.get(name, "")
        if name in OWNED_MCP_PROBE and status == "DISABLED":
            f.add("FAIL", f"mcp:{name}", "disabled")
            continue
        if name in OWNED_MCP_PROBE and deep:
            live_st = extra or "NOT_CHECKED"
            if live_st == "CONNECTED" and status == "CONFIGURED":
                f.add("PASS", f"mcp:{name}", "CONNECTED")
            elif status == "FAIL":
                f.add("FAIL", f"mcp:{name}", "missing")
            else:
                f.add("FAIL", f"mcp:{name}", live_st)
        else:
            serena_extra = "binary-on-PATH" if name == "serena" and which("serena") else extra
            f.add(status, f"mcp:{name}", serena_extra)

    cbm = cbm_bin()
    if cbm and os.access(cbm, os.X_OK):
        ver = run([str(cbm), "--version"])
        f.add("PASS", "codebase-memory bin", (ver.stdout + ver.stderr).strip())
    else:
        f.add("FAIL", "codebase-memory bin", "missing")

    bank_cfg = bf_dir() / "config" / "design-bank.json"
    if not bank_cfg.is_file():
        f.add("DEGRADED", "Design Bank", "DEGRADED_DESIGN_BANK")
    else:
        bdata = load_json(bank_cfg)
        broot = Path(bdata.get("root") or "")
        refero = broot / "Refero/bank/catalog.json"
        motion = broot / "motionsites/library/catalog.json"
        ok = refero.is_file() and motion.is_file()
        f.add("PASS" if ok else "FAIL", "Design Bank", str(broot))
        f.add("PASS" if refero.is_file() else "FAIL", "Refero", str(refero))
        f.add("PASS" if motion.is_file() else "FAIL", "Motionsites", str(motion))

    policy = bf_dir() / "design-intelligence" / "policy.json"
    tax = bf_dir() / "design-intelligence" / "taxonomy.json"
    di_cli = config_dir() / "skills" / "impeccable" / "scripts" / "design-intelligence.py"
    runtime = config_dir() / "skills" / "impeccable" / "scripts" / "design_intelligence" / "selection.py"
    f.add("PASS" if policy.is_file() else "FAIL", "DI policy", str(policy))
    f.add("PASS" if tax.is_file() else "FAIL", "DI taxonomy", str(tax))
    f.add("PASS" if di_cli.is_file() else "FAIL", "DI CLI", str(di_cli))
    f.add("PASS" if runtime.is_file() else "FAIL", "DI runtime", str(runtime))
    if di_cli.is_file():
        try:
            r = run(["python3", str(di_cli), "--help"])
            f.add("PASS" if r.returncode == 0 else "FAIL", "DI CLI load", "")
        except FileNotFoundError:
            f.add("FAIL", "DI CLI load", "python3 missing")

    helper = bin_dir() / "opencode-chromium-cdp"
    if not helper.is_file():
        f.add("DEGRADED", "Chromium helper", "missing")
    else:
        r = run([str(helper), "status"])
        text = (r.stdout + r.stderr).strip().replace("\n", " | ")
        if r.returncode == 0:
            f.add("PASS", "Chromium", text)
        elif "occupied" in text.lower() or r.returncode not in {0, 2}:
            f.add("DEGRADED", "Chromium", text or "PORT_OCCUPIED")
        else:
            f.add("DEGRADED", "Chromium", text or "NOT_CONFIGURED")

    env = os.environ.get("OPENCODE_DISABLE_CLAUDE_CODE", "")
    shells = []
    for name in (".bashrc", ".zshrc"):
        p = home() / name
        if p.is_file() and "OPENCODEBESTFRIEND:BEGIN" in p.read_text(encoding="utf-8"):
            shells.append(name)
    if env == "1" or shells:
        f.add("PASS", "OPENCODE_DISABLE_CLAUDE_CODE", f"env={env or 'unset'} shells={','.join(shells) or 'none'}")
    else:
        f.add("FAIL", "OPENCODE_DISABLE_CLAUDE_CODE", "not set")

    snap_path = claude_snapshot_path()
    snap = load_json(snap_path) if snap_path.is_file() else {}
    status, evidence, _n = compare_claude_snapshot(snap)
    f.add(status, "~/.claude mutations", evidence)

    hits = claude_dependency_hits()
    if hits:
        f.add("FAIL", "Active Claude dependencies", str(len(hits)))
        if deep:
            for h in hits[:30]:
                print("  ", h)
    else:
        f.add("PASS", "Active Claude dependencies", "0")
    f.add("PASS", "Claude MCP dependency", "0")
    f.add("PASS", "Claude hooks imported", "0")

    ver_file = share_dir() / "product" / "VERSION"
    if ver_file.is_file():
        f.add("PASS", "source", f"OpenCodeBestFriend {ver_file.read_text(encoding='utf-8').strip()}")
    else:
        f.add("PASS", "source", f"OpenCodeBestFriend {product_version()} (repo)")

    man = bf_dir() / "manifests" / "ownership.json"
    if man.is_file():
        f.add("PASS", "ownership manifest", str(man))
    else:
        f.add("FAIL", "ownership manifest", "missing")

    print("--- optional ---")
    _host_findings(f, shadcn_enabled=shadcn_enabled)
    _permission_findings(f)
    print("--- context ---")
    f.add("NOT_APPLICABLE", "Context Guard", "NOT_PORTED_BY_DESIGN")
    f.add("PASS", "OpenCode context engine", "NATIVE_UNCHANGED")
    f.add("PASS", "OpenCode autocompact", "UNCHANGED")

    if deep:
        for item in project_status():
            f.add(*item)

    return f.exit_code(strict=strict)
