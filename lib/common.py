from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def home() -> Path:
    return Path(os.environ.get("HOME") or str(Path.home())).expanduser()


def repo_root() -> Path:
    env = os.environ.get("OPENCODE_BF_ROOT")
    if env:
        return Path(env).resolve()
    return Path(__file__).resolve().parent.parent


def config_dir() -> Path:
    return home() / ".config" / "opencode"


def bf_dir() -> Path:
    return config_dir() / "bestfriend"


def share_dir() -> Path:
    return home() / ".local" / "share" / "opencode-bestfriend"


def bin_dir() -> Path:
    return home() / ".local" / "bin"


def backups_dir() -> Path:
    return share_dir() / "backups"


def state_dir() -> Path:
    return share_dir() / "state"


def product_version() -> str:
    return (repo_root() / "VERSION").read_text(encoding="utf-8").strip()


def die(msg: str) -> None:
    print(f"FAIL {msg}", file=sys.stderr)
    raise SystemExit(1)


def info(msg: str) -> None:
    print(f"INFO {msg}")


def warn(msg: str) -> None:
    print(f"WARN {msg}")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def which(name: str) -> str | None:
    return shutil.which(name)


def run(cmd: list[str], env: dict | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess:
    e = os.environ.copy()
    if env:
        e.update(env)
    e.setdefault("OPENCODE_DISABLE_CLAUDE_CODE", "1")
    return subprocess.run(cmd, capture_output=True, text=True, env=e, cwd=cwd)


def copytree_filtered(src: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in {"__pycache__", ".git", "node_modules"}]
        rel = Path(root).relative_to(src)
        target = dest / rel
        target.mkdir(parents=True, exist_ok=True)
        for name in files:
            if name.endswith(".pyc"):
                continue
            shutil.copy2(Path(root) / name, target / name)


def load_policy(root: Path | None = None):
    root = root or repo_root()
    allow_path = root / "vendor" / "skill-allowlist.txt"
    policy_path = root / "vendor" / "skill-policy.json"
    allow = [ln.strip() for ln in allow_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    skills = load_json(policy_path)["skills"]
    if set(allow) != set(skills):
        die("skill-allowlist and skill-policy disagree")
    model = sorted(k for k, v in skills.items() if v["invocation"] == "model")
    manual = sorted(k for k, v in skills.items() if v["invocation"] == "manual")
    return allow, skills, model, manual
