"""Parse Git diff and extract user-facing string values."""

from __future__ import annotations

import csv
import io
import json
import re
from collections import OrderedDict
from typing import Any

from config import (
    _LOCALE_LANG_KEYS,
    _STRUCT_TOKENS,
    ASSIGNMENT_LINE_RE,
    HUNK_RE,
    JSON_KV_RE,
    KEY_ONLY_LINE_RE,
    NESTED_LOCALE_OBJECT_RE,
    NESTED_LOCALE_PAIR_RE,
    PY_KEY_OPEN_RE,
    PY_TRIPLE_OPEN_RE,
    QUOTED_KEY_STRUCT_OPEN_RE,
    SKIP_LINE_RE,
    STRING_VALUE_LINE_RE,
    STRUCT_OPEN_RE,
)


# ===== Helper functions =====
def _json_unescape(value: str) -> str:
    try:
        return json.loads(f'"{value}"')
    except json.JSONDecodeError:
        return (
            value.replace(r"\"", '"')
            .replace(r"\\", "\\")
            .replace(r"\n", "\n")
            .replace(r"\t", "\t")
        )


def _looks_like_user_facing_locale_key(key: str) -> bool:
    if any(ord(c) > 127 for c in key):
        return True
    return " " in key and not key.startswith("msg.") and "." not in key.split(" ")[0]


def should_skip_review_line(text: str) -> bool:
    stripped = text.strip()
    return not stripped or SKIP_LINE_RE.match(stripped) or stripped in _STRUCT_TOKENS


def parse_i18n_csv_row(text: str) -> tuple[str, list[str]] | None:
    try:
        rows = list(csv.reader(io.StringIO(text)))
    except csv.Error:
        return None
    if not rows:
        return None
    parts = [p for p in rows[0]]
    if len(parts) < 2:
        return None
    key = parts[0].strip()
    if not key or key.lower() == "key":
        return None
    values = [p for p in parts[1:] if p != ""]
    if not values:
        return None
    return key, values


def extract_nested_locale_values(text: str) -> tuple[str, list[str]] | None:
    m = NESTED_LOCALE_OBJECT_RE.match(text.strip())
    if not m:
        return None
    key = _json_unescape(m.group("key"))
    values: list[str] = []
    for pm in NESTED_LOCALE_PAIR_RE.finditer(m.group("body")):
        lang = _json_unescape(pm.group("lang")).lower()
        if lang in _LOCALE_LANG_KEYS:
            values.append(_json_unescape(pm.group("val")))
    if not values:
        return None
    return key, values


def extract_user_facing_hints(text: str, path: str = "") -> list[str]:
    stripped = text.strip()
    if not stripped or should_skip_review_line(stripped):
        return []
    if m := JSON_KV_RE.match(stripped):
        return [_json_unescape(m.group(2))]
    if nested := extract_nested_locale_values(stripped):
        return nested[1]
    if m := ASSIGNMENT_LINE_RE.match(stripped):
        return [m.group(3)]
    if m := STRING_VALUE_LINE_RE.match(stripped):
        return [m.group(2)]
    lower_path = path.lower()
    if lower_path.endswith(".csv") or lower_path.endswith("i18n.csv"):
        parsed = parse_i18n_csv_row(stripped)
        return list(parsed[1]) if parsed else []
    if "," in stripped and not stripped.startswith(("'", '"', "{", "[")):
        parsed = parse_i18n_csv_row(stripped)
        if parsed:
            return list(parsed[1])
    return []


def _escape_review_value(value: str) -> str:
    """Escape embedded newlines in a VALUE for compact Gemini payload."""
    return value.replace("\r\n", "\\n").replace("\r", "\\n").replace("\n", "\\n")


def _compact_review_entry(
    path_label: str,
    line_no: int,
    values: list[str],
    *,
    key_name: str | None = None,
) -> str:
    cleaned = [v for v in values if v is not None and str(v) != ""]
    if not cleaned:
        return ""
    header = (
        f"[{path_label}:{line_no}|{key_name}]"
        if key_name
        else f"[{path_label}:{line_no}]"
    )
    escaped = [_escape_review_value(v) for v in cleaned]
    return f"{header}\n" + "\\n".join(escaped)


def _peek_multiline_string_value(
    lines: list[str],
    start_idx: int,
    *,
    concatenate: bool = False,
    max_scan: int | None = None,
) -> tuple[list[int], str, int] | None:
    skip, parts, first_value_idx = [], [], None
    end = len(lines) if max_scan is None else min(len(lines), start_idx + 1 + max_scan)
    for j in range(start_idx + 1, end):
        candidate = lines[j]
        if candidate.startswith(("---", "+++", "@@")):
            break
        if candidate.startswith("-"):
            continue
        is_ctx, is_add = candidate.startswith(" "), candidate.startswith("+")
        if not is_ctx and not is_add:
            break
        if is_ctx and not concatenate and parts:
            break
        value_text = candidate[1:]
        stripped = value_text.strip()
        if parts and stripped in {")", "),"}:
            if is_add:
                skip.append(j)
            break
        if not (match := STRING_VALUE_LINE_RE.match(value_text)):
            if is_ctx and not parts:
                continue
            break
        if first_value_idx is None:
            first_value_idx = j
        if is_add:
            skip.append(j)
        parts.append(match.group(2))
        if not concatenate:
            break
    if not parts or first_value_idx is None:
        return None
    return skip, "".join(parts), first_value_idx


def _find_python_concat_opener(lines: list[str], idx: int) -> int | None:
    """Walk back from a quoted fragment to a KEY = ( opener."""
    for j in range(idx - 1, -1, -1):
        raw = lines[j]
        if raw.startswith(("---", "+++", "@@")):
            return None
        if raw.startswith("-"):
            continue
        if not raw.startswith(("+", " ")):
            return None
        text = raw[1:]
        if PY_KEY_OPEN_RE.match(text):
            return j
        if STRING_VALUE_LINE_RE.match(text) or not text.strip():
            continue
        return None
    return None


def _peek_triple_quoted_string(
    lines: list[str],
    start_idx: int,
    quote: str,
    rest: str,
) -> tuple[list[int], str, int] | None:
    pieces: list[str] = []
    skip: list[int] = []
    first_value_idx = start_idx
    if rest:
        if quote in rest:
            before, _, _after = rest.partition(quote)
            return [], before, start_idx
        pieces.append(rest)

    for j in range(start_idx + 1, len(lines)):
        candidate = lines[j]
        if candidate.startswith(("---", "+++", "@@")):
            break
        if candidate.startswith("-"):
            continue
        if not candidate.startswith("+"):
            break
        text = candidate[1:]
        skip.append(j)
        if not pieces:
            first_value_idx = j
        if quote in text:
            before, _, _after = text.partition(quote)
            pieces.append(before)
            return skip, "\n".join(pieces).rstrip("\n"), first_value_idx
        pieces.append(text)
    return None


def add_chunk_if_new(
    seen: set[str],
    review_chunks: list[str],
    review_by_file: OrderedDict[str, list[str]],
    path_label: str,
    dedupe_key: str,
    chunk: str,
) -> bool:
    if dedupe_key in seen or not chunk:
        return False
    seen.add(dedupe_key)
    review_chunks.append(chunk)
    review_by_file.setdefault(path_label, []).append(chunk)
    return True


def process_triple_quote_string(
    lines: list[str],
    idx: int,
    line_no: int,
    path_label: str,
    triple: re.Match[str],
    skip_indices: set[int],
    seen: set[str],
    review_chunks: list[str],
    review_by_file: OrderedDict[str, list[str]],
) -> bool:
    merged = _peek_triple_quoted_string(
        lines,
        idx,
        triple.group("q"),
        triple.group("rest"),
    )
    if merged is None:
        return False
    skip_idxs, string_val, first_value_idx = merged
    skip_indices.update(skip_idxs)
    value_line_no = line_no + (first_value_idx - idx) if line_no >= 0 else -1
    key_name = triple.group(1)
    chunk = _compact_review_entry(
        path_label,
        value_line_no,
        [string_val],
        key_name=key_name,
    )
    dedupe_key = f"{path_label}:{value_line_no}:{key_name}:{string_val}"
    add_chunk_if_new(
        seen,
        review_chunks,
        review_by_file,
        path_label,
        dedupe_key,
        chunk,
    )
    return True


def process_multiline_value(
    lines: list[str],
    idx: int,
    text: str,
    line_no: int,
    path_label: str,
    skip_indices: set[int],
    seen: set[str],
    review_chunks: list[str],
    review_by_file: OrderedDict[str, list[str]],
) -> str:
    key_only, py_open = KEY_ONLY_LINE_RE.match(text), PY_KEY_OPEN_RE.match(text)
    if not (key_only or py_open):
        return "fallthrough"
    merged = _peek_multiline_string_value(lines, idx, concatenate=bool(py_open))
    if not merged:
        return "skip"
    skip_idxs, string_val, first_value_idx = merged
    skip_indices.update(skip_idxs)
    value_line_no = line_no + (first_value_idx - idx) if line_no >= 0 else -1
    key_name = (key_only or py_open).group(1)
    chunk = _compact_review_entry(
        path_label,
        value_line_no,
        [string_val],
        key_name=key_name,
    )
    dedupe_key = f"{path_label}:{value_line_no}:{key_name}:{string_val}"
    add_chunk_if_new(
        seen,
        review_chunks,
        review_by_file,
        path_label,
        dedupe_key,
        chunk,
    )
    return "consumed"


def process_implicit_concat_fragment(
    lines: list[str],
    idx: int,
    text: str,
    line_no: int,
    path_label: str,
    skip_indices: set[int],
    seen: set[str],
    review_chunks: list[str],
    review_by_file: OrderedDict[str, list[str]],
) -> bool:
    """Join a +quoted fragment with unchanged KEY = ( neighbors.

    Diffs often change only one implicit-concat line; without neighbors the
    VALUE looks like an incomplete sentence to the model.
    """
    current = STRING_VALUE_LINE_RE.match(text)
    if not current:
        return False
    opener_idx = _find_python_concat_opener(lines, idx)
    if opener_idx is None:
        return False
    opener_match = PY_KEY_OPEN_RE.match(lines[opener_idx][1:])
    if not opener_match:
        return False
    merged = _peek_multiline_string_value(lines, opener_idx, concatenate=True)
    if not merged:
        return False
    skip_idxs, string_val, first_value_idx = merged
    if string_val == current.group(2):
        return False
    skip_indices.update(skip_idxs)
    value_line_no = line_no + (first_value_idx - idx) if line_no >= 0 else -1
    key_name = opener_match.group(1)
    chunk = _compact_review_entry(
        path_label, value_line_no, [string_val], key_name=key_name,
    )
    dedupe_key = f"{path_label}:{value_line_no}:{key_name}:{string_val}"
    add_chunk_if_new(
        seen, review_chunks, review_by_file, path_label, dedupe_key, chunk,
    )
    return True


def extract_user_facing_from_line(
    text: str,
    path_label: str,
) -> tuple[list[str], str | None] | None:
    hints: list[str] = []
    key_name: str | None = None
    if path_label.lower().endswith(".csv"):
        if csv_row := parse_i18n_csv_row(text.strip()):
            key_name, hints = csv_row[0], list(csv_row[1])
        else:
            return None
    if not hints:
        if nested := extract_nested_locale_values(text.strip()):
            key_name, hints = nested[0], list(nested[1])
    if not hints:
        if q_open := QUOTED_KEY_STRUCT_OPEN_RE.match(text.strip()):
            outer_key = _json_unescape(q_open.group("key"))
            if _looks_like_user_facing_locale_key(outer_key):
                hints = [outer_key]
            else:
                return None
    if not hints:
        hints = extract_user_facing_hints(text, path_label)
        if assign := ASSIGNMENT_LINE_RE.match(text):
            key_name = assign.group(1)
        elif jkv := JSON_KV_RE.match(text.strip()):
            lang = _json_unescape(jkv.group(1))
            if lang.lower() not in _LOCALE_LANG_KEYS:
                key_name = lang
    if not hints:
        stripped = text.strip()
        if not stripped:
            return None
        hints = [stripped]
    return hints, key_name


def analyze_diff(diff_text: str) -> dict[str, Any]:
    """Parse diff text and extract user-facing values per file."""
    if not diff_text or not diff_text.strip():
        return {"review_text": "", "files": []}

    lines = diff_text.splitlines()
    files_order: list[str] = []
    files_map: dict[str, dict[str, Any]] = {}
    current_file, new_line_no = "", None
    review_chunks: list[str] = []
    review_by_file: OrderedDict[str, list[str]] = OrderedDict()
    seen, skip_indices = set(), set()

    def ensure_file(path: str) -> dict[str, Any]:
        if path not in files_map:
            files_map[path] = {
                "path": path,
                "added": 0,
                "deleted": 0,
                "added_lines": [],
            }
            files_order.append(path)
        return files_map[path]

    for idx, line in enumerate(lines):
        if line.startswith("+++ b/"):
            current_file, new_line_no = line[6:], None
            ensure_file(current_file)
            continue
        if line.startswith("+++ "):
            rest = line[4:]
            if rest.startswith("b/"):
                current_file = rest[2:]
                ensure_file(current_file)
            new_line_no = None
            continue
        if hunk := HUNK_RE.match(line):
            new_line_no = int(hunk.group(3))
            continue
        if line.startswith("+") and not line.startswith("+++"):
            entry = ensure_file(current_file or "(unknown)")
            line_no = new_line_no if new_line_no is not None else -1
            text = line[1:]
            entry["added"] += 1
            entry["added_lines"].append({"line": line_no, "text": text})
            if new_line_no is not None:
                new_line_no += 1
            if idx in skip_indices:
                continue
            path_label = current_file or "(unknown)"
            if triple := PY_TRIPLE_OPEN_RE.match(text):
                if process_triple_quote_string(
                    lines,
                    idx,
                    line_no,
                    path_label,
                    triple,
                    skip_indices,
                    seen,
                    review_chunks,
                    review_by_file,
                ):
                    continue
            multiline = process_multiline_value(
                lines,
                idx,
                text,
                line_no,
                path_label,
                skip_indices,
                seen,
                review_chunks,
                review_by_file,
            )
            if multiline in ("consumed", "skip"):
                continue
            if process_implicit_concat_fragment(
                lines,
                idx,
                text,
                line_no,
                path_label,
                skip_indices,
                seen,
                review_chunks,
                review_by_file,
            ):
                continue
            if should_skip_review_line(text):
                continue
            if STRUCT_OPEN_RE.match(text):
                continue
            extracted = extract_user_facing_from_line(text, path_label)
            if extracted is None:
                continue
            hints, key_name = extracted
            chunk = _compact_review_entry(
                path_label,
                line_no,
                hints,
                key_name=key_name,
            )
            dedupe_key = f"{path_label}:{line_no}:{chunk}"
            add_chunk_if_new(
                seen,
                review_chunks,
                review_by_file,
                path_label,
                dedupe_key,
                chunk,
            )
            continue
        if line.startswith("-") and not line.startswith("---"):
            ensure_file(current_file or "(unknown)")["deleted"] += 1
            continue
        if line.startswith(" ") and new_line_no is not None:
            new_line_no += 1

    files_out = [
        {
            "path": files_map[p]["path"],
            "added": files_map[p]["added"],
            "deleted": files_map[p]["deleted"],
        }
        for p in files_order
    ]
    review_by_file_text = {p: "\n\n".join(c) for p, c in review_by_file.items() if c}
    return {
        "review_text": "\n\n".join(review_chunks),
        "review_by_file": review_by_file_text,
        "files": files_out,
        "_added_line_details": {p: files_map[p]["added_lines"] for p in files_order},
    }


def parse_diff(diff_text: str) -> str:
    return analyze_diff(diff_text)["review_text"]
