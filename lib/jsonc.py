from __future__ import annotations

import json
import re
from pathlib import Path


def strip_jsonc(text: str) -> str:
    """Remove // and /* */ comments that are not inside strings."""
    out: list[str] = []
    i = 0
    n = len(text)
    in_str = False
    quote = ""
    escape = False
    while i < n:
        ch = text[i]
        if in_str:
            out.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == quote:
                in_str = False
            i += 1
            continue
        if ch in "\"'":
            in_str = True
            quote = ch
            out.append(ch)
            i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "/":
            i += 2
            while i < n and text[i] not in "\n\r":
                i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i = min(n, i + 2)
            continue
        out.append(ch)
        i += 1
    stripped = "".join(out)
    stripped = re.sub(r",(\s*[}\]])", r"\1", stripped)
    return stripped


def contains_comments(text: str) -> bool:
    i = 0
    n = len(text)
    in_str = False
    quote = ""
    escape = False
    while i < n:
        ch = text[i]
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == quote:
                in_str = False
            i += 1
            continue
        if ch in "\"'":
            in_str = True
            quote = ch
            i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] in "/*":
            return True
        i += 1
    return False


def loads(text: str):
    text = text.strip() or "{}"
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return json.loads(strip_jsonc(text))


def load_path(path: Path):
    if not path.is_file():
        return {}
    return loads(path.read_text(encoding="utf-8"))


def dumps(data) -> str:
    return json.dumps(data, indent=2) + "\n"


def _skip_ws_and_comments(text: str, i: int) -> int:
    n = len(text)
    while i < n:
        ch = text[i]
        if ch in " \t\r\n":
            i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "/":
            i += 2
            while i < n and text[i] not in "\n\r":
                i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i = min(n, i + 2)
            continue
        break
    return i


def _match_delimited(text: str, start: int) -> int:
    """start at '{' or '['. Return index of matching closer."""
    opener = text[start]
    closer = "}" if opener == "{" else "]"
    depth = 0
    i = start
    n = len(text)
    in_str = False
    quote = ""
    escape = False
    while i < n:
        ch = text[i]
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == quote:
                in_str = False
            i += 1
            continue
        if ch in "\"'":
            in_str = True
            quote = ch
            i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "/":
            i += 2
            while i < n and text[i] not in "\n\r":
                i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i = min(n, i + 2)
            continue
        if ch == opener:
            depth += 1
        elif ch == closer:
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ValueError("unbalanced JSONC object")


def _find_root_key(text: str, key: str) -> tuple[int, int, int] | None:
    """Return (key_quote_start, value_start, value_end_inclusive) for a root object key."""
    start = _skip_ws_and_comments(text, 0)
    if start >= len(text) or text[start] != "{":
        return None
    close = _match_delimited(text, start)
    i = start + 1
    needle = json.dumps(key)
    while i < close:
        i = _skip_ws_and_comments(text, i)
        if i >= close or text[i] == "}":
            break
        if text[i] != '"':
            return None
        # parse key string
        j = i + 1
        esc = False
        while j < close:
            ch = text[j]
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                break
            j += 1
        found = text[i : j + 1]
        k = _skip_ws_and_comments(text, j + 1)
        if k >= close or text[k] != ":":
            return None
        val = _skip_ws_and_comments(text, k + 1)
        if val >= close:
            return None
        if text[val] in "{[":
            end = _match_delimited(text, val)
        elif text[val] in "\"'":
            end = val + 1
            esc = False
            while end < close:
                ch = text[end]
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == text[val]:
                    break
                end += 1
        else:
            end = val
            while end < close and text[end] not in ",}":
                end += 1
            end -= 1
        if found == needle:
            return i, val, end
        nxt = _skip_ws_and_comments(text, end + 1)
        if nxt < close and text[nxt] == ",":
            i = nxt + 1
        else:
            i = nxt
    return None


def _object_has_entries(text: str, brace_start: int) -> bool:
    close = _match_delimited(text, brace_start)
    inner = text[brace_start + 1 : close]
    inner_stripped = strip_jsonc(inner).strip()
    return bool(inner_stripped)


def upsert_mcp_servers(text: str, servers: dict[str, dict]) -> str:
    """Insert or replace owned MCP server objects without rewriting unrelated text."""
    if not text.strip():
        text = "{}\n"
    mcp = _find_root_key(text, "mcp")
    if mcp is None:
        mcp_only = json.dumps(servers, indent=2)
        insert = '  "mcp": ' + mcp_only.replace("\n", "\n  ") + ",\n"
        start = _skip_ws_and_comments(text, 0)
        if text[start] != "{":
            raise ValueError("root is not an object")
        close = _match_delimited(text, start)
        inner_has = _object_has_entries(text, start)
        if not inner_has:
            return text[: start + 1] + "\n" + insert.rstrip().rstrip(",") + "\n" + text[close:]
        # insert before root close; ensure comma on previous entry
        before = text[:close].rstrip()
        if before[-1] not in "{,":
            before = before + ","
        return before + "\n" + insert.rstrip().rstrip(",") + "\n" + text[close:]
    _key_at, val_at, val_end = mcp
    if text[val_at] != "{":
        raise ValueError("mcp is not an object")
    current = text
    for name, spec in servers.items():
        spec_txt = json.dumps(spec, indent=2)
        found = _find_key_in_object(current, val_at, name)
        if found is None:
            mcp = _find_root_key(current, "mcp")
            if mcp is None:
                raise ValueError("mcp vanished")
            _, val_at, val_end = mcp
            close = _match_delimited(current, val_at)
            entry = "    " + json.dumps(name) + ": " + spec_txt.replace("\n", "\n    ")
            if not _object_has_entries(current, val_at):
                current = current[: val_at + 1] + "\n" + entry + "\n  " + current[close:]
            else:
                before = current[:close].rstrip()
                if before[-1] not in "{,":
                    before = before + ","
                current = before + "\n" + entry + "\n  " + current[close:]
            mcp = _find_root_key(current, "mcp")
            _, val_at, _ = mcp
            continue
        _k0, v0, v1 = found
        current = current[:v0] + spec_txt + current[v1 + 1 :]
        mcp = _find_root_key(current, "mcp")
        _, val_at, _ = mcp
    return current


def _find_key_in_object(text: str, brace_start: int, key: str) -> tuple[int, int, int] | None:
    close = _match_delimited(text, brace_start)
    i = brace_start + 1
    needle = json.dumps(key)
    while i < close:
        i = _skip_ws_and_comments(text, i)
        if i >= close or text[i] == "}":
            break
        if text[i] != '"':
            i += 1
            continue
        j = i + 1
        esc = False
        while j < close:
            ch = text[j]
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                break
            j += 1
        found = text[i : j + 1]
        k = _skip_ws_and_comments(text, j + 1)
        if k >= close or text[k] != ":":
            i = j + 1
            continue
        val = _skip_ws_and_comments(text, k + 1)
        if text[val] in "{[":
            end = _match_delimited(text, val)
        elif text[val] in "\"'":
            end = val + 1
            esc = False
            while end < close:
                ch = text[end]
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == text[val]:
                    break
                end += 1
        else:
            end = val
            while end < close and text[end] not in ",}":
                end += 1
            end -= 1
        if found == needle:
            return i, val, end
        nxt = _skip_ws_and_comments(text, end + 1)
        if nxt < close and text[nxt] == ",":
            i = nxt + 1
        else:
            i = nxt
    return None


def remove_mcp_servers(text: str, names: list[str] | tuple[str, ...]) -> str:
    names = list(names)
    current = text
    for name in names:
        mcp = _find_root_key(current, "mcp")
        if mcp is None:
            continue
        _, val_at, _ = mcp
        if current[val_at] != "{":
            continue
        found = _find_key_in_object(current, val_at, name)
        if found is None:
            continue
        key_at, _val, end = found
        # include leading comma if present
        left = key_at
        while left > 0 and current[left - 1] in " \t":
            left -= 1
        right = end + 1
        # trailing comma
        r = _skip_ws_and_comments(current, right)
        if r < len(current) and current[r] == ",":
            right = r + 1
        else:
            # maybe we are last entry: remove preceding comma
            p = left - 1
            while p >= 0 and current[p] in " \t\r\n":
                p -= 1
            if p >= 0 and current[p] == ",":
                left = p
        current = current[:left] + current[right:]
    return current
