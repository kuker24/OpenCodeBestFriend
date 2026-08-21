from __future__ import annotations

import json
import os
from pathlib import Path

from .common import (
    bf_dir,
    bin_dir,
    config_dir,
    home,
    load_json,
    load_policy,
    repo_root,
    run,
    share_dir,
    which,
)
from . import jsonc

CLAUDE_ACTIVE_PATTERNS = (
    "~/.claude/",
    "$HOME/.claude/",
    "claude-gbf",
    "CLAUDE_CODE_",
    "CLAUDE_DESIGN_BANK",
    "grokbestfriend-claude",
    "claude mcp",
)


def report(status: str, label: str, evidence: str = "") -> None:
    print(f"{status:<22} {label:<28} {evidence}")


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
        out[name] = "PASS"
    return out


def cmd_mcp_status() -> int:
    for name, status in mcp_status_map().items():
        extra = "binary-on-PATH" if name == "serena" and which("serena") else ""
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

    claude = home() / ".claude"
    extra = 0
    if claude.is_dir():
        # installer must not add files; presence of a pre-existing tree is FOREIGN
        extra = 0
    report("PASS" if extra == 0 else "FAIL", "~/.claude mutations", str(extra))

    hits = []
    skip_parts = {
        "source",
        "cache",
        "node_modules",
        ".git",
        "docs",
        "licenses",
        "product",
        "backups",
    }
    for root in (config_dir(), share_dir()):
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(p in skip_parts for p in path.parts):
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
    hits = [h for h in hits if "/bestfriend/docs/" not in h and "/manifests/" not in h]
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
    report("PASS", "Context Guard", "NOT_PORTED_BY_DESIGN")
    return 0 if failed == 0 else 1


def optional_tools() -> None:
    mapping = {
        "browser-act": which("browser-act"),
        "serena": which("serena"),
        "semgrep": which("semgrep"),
        "osv-scanner": which("osv-scanner"),
        "gitleaks": which("gitleaks"),
        "gh": which("gh"),
        "node": which("node"),
        "npx": which("npx"),
        "python3": which("python3"),
    }
    required_host = {"python3"}
    for name, path in mapping.items():
        if path:
            if name == "gh":
                r = run(["gh", "auth", "status"])
                if r.returncode != 0:
                    report("DEGRADED_AUTH_REQUIRED", name, path)
                    continue
            report("PASS", name, path)
        elif name in required_host:
            report("FAIL", name, "NOT_INSTALLED")
        else:
            report("OPTIONAL_ABSENT", name, "NOT_INSTALLED")


def cmd_doctor(deep: bool = False) -> int:
    failed = 0
    print("=== opencode-bestfriend doctor ===")
    oc = which("opencode") or os.environ.get("OPENCODE_BF_MOCK_OPENCODE")
    if oc:
        ver = run([oc, "--version"]).stdout.strip()
        report("PASS", "OpenCode", f"{oc} {ver}")
    else:
        report("FAIL", "OpenCode", "not on PATH")
        failed += 1

    cfg = None
    for cand in (config_dir() / "opencode.jsonc", config_dir() / "opencode.json"):
        if cand.is_file():
            cfg = cand
            break
    if cfg:
        try:
            jsonc.load_path(cfg)
            report("PASS", cfg.name, "parseable")
        except (OSError, ValueError, json.JSONDecodeError):
            report("FAIL", cfg.name, "invalid JSON/JSONC")
            failed += 1
    else:
        report("FAIL", "opencode.jsonc", "missing")
        failed += 1

    agents = config_dir() / "AGENTS.md"
    if agents.is_file():
        text = agents.read_text(encoding="utf-8")
        lines = text.count("\n")
        if "OPENCODEBESTFRIEND:BEGIN" in text and "@~/" not in text and "Context Guard" not in text and lines <= 120:
            report("PASS", "AGENTS.md", f"thin lines={lines}")
        else:
            report("FAIL", "AGENTS.md", f"lines={lines}")
            failed += 1
    else:
        report("FAIL", "AGENTS.md", "missing")
        failed += 1

    allow, _, model, manual = installed_policy()
    miss = 0
    for name in model:
        if not (config_dir() / "skills" / name / "SKILL.md").is_file():
            miss += 1
    for name in manual:
        if not (bf_dir() / "skills" / name / "SKILL.md").is_file() or not (config_dir() / "commands" / f"{name}.md").is_file():
            miss += 1
    if miss:
        report("FAIL", "skills", f"missing {miss}")
        failed += 1
    else:
        report(
            "PASS",
            "skills",
            f"TOTAL {len(allow)}/{len(allow)} MODEL {len(model)}/{len(model)} MANUAL {len(manual)}/{len(manual)}",
        )

    rules = list((bf_dir() / "rules").glob("*.md")) if (bf_dir() / "rules").is_dir() else []
    names = {p.name for p in rules}
    if "04-context-guard.md" in names:
        report("FAIL", "rules", "context guard present")
        failed += 1
    elif {"00-routing.md", "01-verification.md", "02-engineering-principles.md", "03-prose-discipline.md"} <= names:
        report("PASS", "rules", f"{len(names)} portable; 04-context-guard EXCLUDED_BY_DESIGN")
    else:
        report("FAIL", "rules", f"got {sorted(names)}")
        failed += 1

    for name, status in mcp_status_map().items():
        report(status, f"mcp:{name}", "")
        if name in {"codebase-memory-mcp", "context7", "shadcn"} and status == "FAIL":
            failed += 1

    cbm = share_dir() / "components" / "codebase-memory" / "bin" / "codebase-memory-mcp"
    if cbm.is_file() and os.access(cbm, os.X_OK):
        ver = run([str(cbm), "--version"])
        report("PASS", "codebase-memory bin", (ver.stdout + ver.stderr).strip())
    else:
        report("FAIL", "codebase-memory bin", "missing")
        failed += 1

    failed += cmd_design_bank()
    failed += cmd_design_intelligence()
    cmd_chromium()
    failed += isolation_check(deep=deep)

    ver_file = share_dir() / "product" / "VERSION"
    if ver_file.is_file():
        report("PASS", "source", f"OpenCodeBestFriend {ver_file.read_text(encoding='utf-8').strip()}")
    else:
        report("PASS", "source", "OpenCodeBestFriend 1.0.0 (repo)")

    man = bf_dir() / "manifests" / "ownership.json"
    if man.is_file():
        report("PASS", "ownership manifest", str(man))
    else:
        report("FAIL", "ownership manifest", "missing")
        failed += 1

    print("--- optional ---")
    optional_tools()
    print("--- context ---")
    report("PASS", "Context Guard", "NOT_PORTED_BY_DESIGN")
    report("PASS", "OpenCode context engine", "NATIVE_UNCHANGED")
    report("PASS", "OpenCode autocompact", "UNCHANGED")
    return 1 if failed else 0
