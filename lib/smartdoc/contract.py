from __future__ import annotations

import copy
import hashlib
import json
from typing import Any

ROLES = frozenset(
    {
        "instruction",
        "source",
        "draft",
        "template",
        "style_reference",
        "data",
        "audit_report",
        "output_reference",
    }
)
MODES = frozenset(
    {
        "ANSWER",
        "CREATE",
        "TRANSFORM",
        "SUMMARIZE_STUDY",
        "EXTRACT",
        "ANALYZE",
        "SYNTHESIZE",
        "VERIFY",
    }
)
FIDELITY = frozenset({"STRICT", "BALANCED", "ADAPTIVE"})
CONFIDENCE = frozenset({"HIGH", "MEDIUM", "LOW"})
LOCKED_GOAL_FIELDS = ("intent", "goal", "audience", "language", "source_policy", "fidelity", "output")


class ContractError(Exception):
    code = "CONTRACT"


def empty_contract() -> dict[str, Any]:
    return {
        "intent": None,
        "goal": {"description": ""},
        "inputs": [],
        "audience": {},
        "language": {},
        "source_policy": {"attached": True, "smartbook": False, "web": False},
        "fidelity": {"level": "BALANCED"},
        "identity": {"profile": None},
        "output": {"format": None, "renderer": None},
        "citations": {"required": False},
        "originality": {"mode": "OFF", "corpus": []},
        "verification": {},
        "confidence": None,
        "locks": {"goal": False, "content": False},
        "content_sha256": None,
    }


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def normalize_contract(data: dict[str, Any] | None) -> dict[str, Any]:
    base = empty_contract()
    incoming = data if isinstance(data, dict) else {}
    out = copy.deepcopy(base)
    out.update({k: copy.deepcopy(v) for k, v in incoming.items() if k in base or k in incoming})
    intent = out.get("intent")
    if isinstance(intent, str):
        out["intent"] = intent.strip().upper() or None
    fidelity = _as_dict(out.get("fidelity"))
    level = str(fidelity.get("level") or "BALANCED").upper()
    fidelity["level"] = level if level in FIDELITY else "BALANCED"
    out["fidelity"] = fidelity
    policy = _as_dict(out.get("source_policy"))
    out["source_policy"] = {
        "attached": bool(policy.get("attached", True)),
        "smartbook": bool(policy.get("smartbook", False)),
        "web": bool(policy.get("web", False)),
    }
    orig = _as_dict(out.get("originality"))
    mode = str(orig.get("mode") or "OFF").upper()
    if mode not in {"OFF", "LOCAL_AUDIT", "REPORT_ASSISTED"}:
        mode = "OFF"
    raw_corpus = orig.get("corpus")
    corpus_list = raw_corpus if isinstance(raw_corpus, list) else []
    out["originality"] = {"mode": mode, "corpus": [str(x) for x in corpus_list]}
    inputs = out.get("inputs")
    out["inputs"] = inputs if isinstance(inputs, list) else []
    locks = _as_dict(out.get("locks"))
    out["locks"] = {"goal": bool(locks.get("goal")), "content": bool(locks.get("content"))}
    return out


def validate_contract(data: dict[str, Any] | None) -> list[str]:
    c = normalize_contract(data)
    errors: list[str] = []
    intent = c.get("intent")
    if intent is not None and intent not in MODES:
        errors.append(f"intent:{intent}")
    for item in c.get("inputs") or []:
        if not isinstance(item, dict):
            errors.append("input:not-object")
            continue
        roles = item.get("roles") or item.get("role")
        if isinstance(roles, str):
            roles = [roles]
        if not isinstance(roles, list) or not roles:
            errors.append("input:missing-role")
            continue
        for role in roles:
            if role not in ROLES:
                errors.append(f"role:{role}")
    if c["fidelity"]["level"] not in FIDELITY:
        errors.append("fidelity")
    if c.get("confidence") is not None and c.get("confidence") not in CONFIDENCE:
        errors.append("confidence")
    return errors


def compute_confidence(data: dict[str, Any] | None) -> str:
    c = normalize_contract(data)
    goal = str(_as_dict(c.get("goal")).get("description") or "").strip()
    fmt = _as_dict(c.get("output")).get("format")
    language = _as_dict(c.get("language")).get("primary")
    if not goal:
        return "LOW"
    if fmt and language:
        return "HIGH"
    if fmt or language:
        return "MEDIUM"
    return "MEDIUM"


def goal_lock(data: dict[str, Any]) -> dict[str, Any]:
    c = normalize_contract(data)
    if validate_contract(c):
        raise ContractError("invalid contract")
    if not str(_as_dict(c.get("goal")).get("description") or "").strip():
        raise ContractError("goal missing")
    if not c.get("intent"):
        raise ContractError("intent missing")
    c["confidence"] = compute_confidence(c)
    c["locks"]["goal"] = True
    return c


def assert_goal_unlocked_or_same(current: dict[str, Any], incoming: dict[str, Any]) -> None:
    cur = normalize_contract(current)
    if not cur["locks"]["goal"]:
        return
    nxt = normalize_contract(incoming)
    for field in LOCKED_GOAL_FIELDS:
        if json.dumps(cur.get(field), sort_keys=True) != json.dumps(nxt.get(field), sort_keys=True):
            raise ContractError(f"GOAL_LOCKED {field}")


def content_lock(data: dict[str, Any], content: str) -> dict[str, Any]:
    c = normalize_contract(data)
    if not c["locks"]["goal"]:
        raise ContractError("goal not locked")
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    c["content_sha256"] = digest
    c["locks"]["content"] = True
    return c


def assert_content_unchanged(data: dict[str, Any], content: str) -> None:
    c = normalize_contract(data)
    if not c["locks"]["content"]:
        raise ContractError("content not locked")
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    if digest != c.get("content_sha256"):
        raise ContractError("CONTENT_LOCKED")


def source_policy_allows_web(data: dict[str, Any] | None) -> bool:
    return bool(normalize_contract(data)["source_policy"]["web"])
