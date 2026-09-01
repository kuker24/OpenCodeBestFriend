from __future__ import annotations

import json
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from .capabilities import capability_matrix, status_payload
from .doctor import run_doctor
from .extract import ExtractError, extract_file
from .originality import local_similarity_audit
from .paths import PathEscape, resolve_smartdoc_root
from .profiles import create_profile, delete_profile, list_profiles, load_profile, select_profile, selected_name
from .smartbook import SmartBookError, ingest, inspect_book, list_books, retrieve, validate_book
from .styles import create_style, delete_style, list_styles, load_style


def _flags(child: ArgumentParser) -> ArgumentParser:
    child.add_argument("--root", help="SmartDoc root (default: OPENCODE_SMARTDOC or ~/SmartDoc)")
    child.add_argument("--json", action="store_true")
    return child


def add_smartdoc_cli(parser: ArgumentParser) -> None:
    parser.description = "SmartDoc profiles, extraction, and status"
    actions = parser.add_subparsers(dest="smartdoc_action", required=True)
    _flags(actions.add_parser("status", help="capability matrix and resolved root"))
    _flags(actions.add_parser("doctor", help="smoke-test SmartDoc runtime"))
    pre = _flags(actions.add_parser("preflight", help="extract metadata from a file"))
    pre.add_argument("path")
    pre.add_argument("--ocr", default="AUTO")
    pre.add_argument("--ocr-lang", action="append", default=[])
    ext = _flags(actions.add_parser("extract", help="extract text from a file"))
    ext.add_argument("path")
    ext.add_argument("--ocr", default="AUTO")
    ext.add_argument("--ocr-lang", action="append", default=[])
    orig = _flags(actions.add_parser("originality", help="Local Similarity Audit against files"))
    orig.add_argument("path")
    orig.add_argument("--against", action="append", default=[])
    prof = _flags(actions.add_parser("profile"))
    psub = prof.add_subparsers(dest="profile_action", required=True)
    psub.add_parser("list")
    pshow = psub.add_parser("show")
    pshow.add_argument("name")
    pcreate = psub.add_parser("create")
    pcreate.add_argument("name")
    pcreate.add_argument("--field", action="append", default=[], help="label=value")
    pdel = psub.add_parser("delete")
    pdel.add_argument("name")
    psel = psub.add_parser("select")
    psel.add_argument("name", nargs="?")
    psel.add_argument("--none", action="store_true")
    sty = _flags(actions.add_parser("style"))
    ssub = sty.add_subparsers(dest="style_action", required=True)
    ssub.add_parser("list")
    sshow = ssub.add_parser("show")
    sshow.add_argument("name")
    screate = ssub.add_parser("create")
    screate.add_argument("name")
    sdel = ssub.add_parser("delete")
    sdel.add_argument("name")


def add_smartbook_cli(parser: ArgumentParser) -> None:
    parser.description = "SmartBook ingest and retrieval"
    actions = parser.add_subparsers(dest="smartbook_action", required=True)
    _flags(actions.add_parser("status"))
    _flags(actions.add_parser("list"))
    insp = _flags(actions.add_parser("inspect"))
    insp.add_argument("slug")
    ing = _flags(actions.add_parser("ingest"))
    ing.add_argument("path")
    ing.add_argument("--slug", required=True)
    ing.add_argument("--ocr", default="AUTO")
    ing.add_argument("--ocr-lang", action="append", default=[])
    ret = _flags(actions.add_parser("retrieve"))
    ret.add_argument("slug")
    ret.add_argument("query")
    val = _flags(actions.add_parser("validate"))
    val.add_argument("slug")


def _emit(payload: object, *, as_json: bool) -> int:
    if as_json:
        json.dump(payload, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
        return 0
    if isinstance(payload, dict):
        for key, value in payload.items():
            if isinstance(value, (dict, list)):
                print(f"{key}: {json.dumps(value, ensure_ascii=False)}")
            else:
                print(f"{key} {value}")
        return 0
    if isinstance(payload, list):
        for item in payload:
            print(item if isinstance(item, str) else json.dumps(item, ensure_ascii=False))
        return 0
    print(payload)
    return 0


def _fields(pairs: list[str]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for raw in pairs:
        if "=" not in raw:
            raise PathEscape(f"INVALID_FIELD {raw}")
        label, value = raw.split("=", 1)
        out.append({"label": label, "value": value})
    return out


def _root(args: Namespace) -> Path:
    return resolve_smartdoc_root(explicit=getattr(args, "root", None))


def dispatch_smartdoc(args: Namespace) -> int:
    as_json = bool(getattr(args, "json", False))
    root = _root(args)
    action = args.smartdoc_action
    try:
        if action == "status":
            return _emit(status_payload(root=str(root)), as_json=as_json)
        if action == "doctor":
            payload = run_doctor(root=root)
            _emit(payload, as_json=True)
            return 0 if payload.get("ok") else 1
        if action in {"preflight", "extract"}:
            langs = [str(x) for x in (getattr(args, "ocr_lang", None) or [])]
            result = extract_file(Path(args.path), ocr=str(getattr(args, "ocr", "AUTO")), languages=langs or None)
            if action == "preflight":
                result = {
                    "status": result.get("status"),
                    "format": result.get("format"),
                    "capability": result.get("capability"),
                    "pages": result.get("pages"),
                    "has_text": bool(result.get("text")),
                    "methods": [r.get("method") for r in (result.get("page_records") or [])],
                }
            return _emit(result, as_json=True)
        if action == "originality":
            src = extract_file(Path(args.path))
            corpus = []
            for against in args.against:
                item = extract_file(Path(against))
                corpus.append({"id": against, "text": item.get("text") or ""})
            return _emit(local_similarity_audit(src.get("text") or "", corpus), as_json=True)
        if action == "profile":
            sub = args.profile_action
            if sub == "list":
                return _emit({"selected": selected_name(root), "profiles": list_profiles(root)}, as_json=as_json)
            if sub == "show":
                return _emit(load_profile(root, args.name), as_json=True)
            if sub == "create":
                return _emit(create_profile(root, args.name, _fields(args.field)), as_json=True)
            if sub == "delete":
                delete_profile(root, args.name)
                return 0
            if sub == "select":
                select_profile(root, None if args.none else args.name)
                return 0
        if action == "style":
            sub = args.style_action
            if sub == "list":
                return _emit(list_styles(root), as_json=as_json)
            if sub == "show":
                return _emit(load_style(root, args.name), as_json=True)
            if sub == "create":
                return _emit(create_style(root, args.name), as_json=True)
            if sub == "delete":
                delete_style(root, args.name)
                return 0
    except (PathEscape, ExtractError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1
    return 2


def dispatch_smartbook(args: Namespace) -> int:
    as_json = bool(getattr(args, "json", False))
    root = _root(args)
    action = args.smartbook_action
    try:
        if action == "status":
            return _emit({"root": str(root), "books": list_books(root)}, as_json=as_json)
        if action == "list":
            return _emit(list_books(root), as_json=as_json)
        if action == "inspect":
            return _emit(inspect_book(root, args.slug), as_json=True)
        if action == "ingest":
            path = Path(args.path)
            langs = [str(x) for x in (getattr(args, "ocr_lang", None) or [])]
            extracted = extract_file(path, ocr=str(getattr(args, "ocr", "AUTO")), languages=langs or None)
            if extracted.get("status") not in {"READY", "PARTIAL"}:
                return _emit(extracted, as_json=True)
            return _emit(
                ingest(root, slug=args.slug, source_name=path.name, text=extracted.get("text") or ""),
                as_json=True,
            )
        if action == "retrieve":
            return _emit(retrieve(root, args.slug, args.query), as_json=True)
        if action == "validate":
            errors = validate_book(root, args.slug)
            payload = {"ok": not errors, "errors": errors}
            _emit(payload, as_json=True)
            return 0 if not errors else 1
    except (PathEscape, ExtractError, SmartBookError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1
    return 2
