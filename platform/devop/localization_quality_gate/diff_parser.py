"""Parse Git diff and extract user-facing string values."""

import csv
import io
import re
from collections import OrderedDict
from pathlib import Path
from typing import Any

from config import (
    ASSIGNMENT_LINE_RE,
    CONTEXT_LINES,
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
    _LOCALE_LANG_KEYS,
    _STRUCT_TOKENS,
    _looks_like_user_facing_locale_key,  # we need to define or import
)
from models import DiffAnalysis, FileStat, AddedLine

# We need to bring in some helper functions that were in the original script
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

def should_skip_review_line(text: str) -> bool:
    stripped = text.strip()
    return not stripped or SKIP_LINE_RE.match(stripped) or stripped in _STRUCT_TOKENS

def _peek_multiline_string_value(
    lines: list[str], start_idx: int, *, concatenate: bool = False, max_scan: int | None = None,
) -> tuple[list[int], str, int] | None:
    """Collect following +'...' lines. Returns (skip_indices, concatenated_value, first_value_idx)."""
    skip, parts, first_value_idx = [], [], None
    end = len(lines) if max_scan is None else min(len(lines), start_idx + 1 + max_scan)
    for j in range(start_idx + 1, end):
        candidate = lines[j]
        if candidate.startswith(("---", "+++", "@@")) or (candidate.startswith(" ") and parts):
            break
        if candidate.startswith("-"):
            continue
        if candidate.startswith(" ") and not parts:
            continue
        if not candidate.startswith("+"):
            break
        value_text = candidate[1:]
        stripped = value_text.strip()
        if parts and stripped in {")", "),"}:
            skip.append(j)
            break
        if not (match := STRING_VALUE_LINE_RE.match(value_text)):
            break
        if first_value_idx is None:
            first_value_idx = j
        skip.append(j)
        parts.append(match.group(2))
        if not concatenate:
            break
    if not parts or first_value_idx is None:
        return None
    return skip, "".join(parts), first_value_idx

def _peek_triple_quoted_string(
    lines: list[str], start_idx: int, quote: str, rest: str,
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

def analyze_diff(diff_text: str) -> DiffAnalysis:
    """Parse diff text and extract user-facing values per file."""
    if not diff_text or not diff_text.strip():
        return {"review_text": "", "review_by_file": {}, "files": [], "_added_line_details": {}}

    lines = diff_text.splitlines()
    files_order: list[str] = []
    files_map: dict[str, dict[str, Any]] = {}
    current_file, new_line_no = "", None
    review_chunks: list[str] = []
    review_by_file: OrderedDict[str, list[str]] = OrderedDict()
    seen, skip_indices = set(), set()
    legacy_chunk_chars: list[int] = []   # only for stderr metric, not used in output

    def ensure_file(path: str) -> dict[str, Any]:
        if path not in files_map:
            files_map[path] = {"path": path, "added": 0, "deleted": 0, "added_lines": []}
            files_order.append(path)
        return files_map[path]

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
        header = f"[{path_label}:{line_no}|{key_name}]" if key_name else f"[{path_label}:{line_no}]"
        escaped = [_escape_review_value(v) for v in cleaned]
        return f"{header}\n" + "\\n".join(escaped)

    def _escape_review_value(value: str) -> str:
        return value.replace("\r\n", "\\n").replace("\r", "\\n").replace("\n", "\\n")

    def _legacy_review_chunk_chars(
        path_label: str,
        line_no: int,
        values: list[str],
        *,
        key_name: str | None = None,
        note: str | None = None,
        source_line: str | None = None,
        context_body: str | None = None,
    ) -> int:
        parts = [f"# file: {path_label}", f"# line: {line_no}"]
        if key_name:
            parts.append(f"# key: {key_name}")
        if note:
            parts.append(f"# note: {note}")
        if source_line is not None:
            parts.append(source_line if source_line.startswith("+") else f"+{source_line}")
        if context_body:
            parts.append(context_body)
        parts.extend(f"user_facing: {v}" for v in values if v is not None and str(v) != "")
        return len("\n".join(parts))

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
            # Triple-quoted string
            if triple := PY_TRIPLE_OPEN_RE.match(text):
                merged_triple = _peek_triple_quoted_string(
                    lines, idx, triple.group("q"), triple.group("rest"),
                )
                if merged_triple is not None:
                    skip_idxs, string_val, first_value_idx = merged_triple
                    skip_indices.update(skip_idxs)
                    value_line_no = line_no + (first_value_idx - idx) if line_no >= 0 else -1
                    key_name = triple.group(1)
                    chunk = _compact_review_entry(path_label, value_line_no, [string_val], key_name=key_name)
                    dedupe_key = f"{path_label}:{value_line_no}:{key_name}:{string_val}"
                    if dedupe_key not in seen and chunk:
                        seen.add(dedupe_key)
                        review_chunks.append(chunk)
                        review_by_file.setdefault(path_label, []).append(chunk)
                    continue
            key_only, py_open = KEY_ONLY_LINE_RE.match(text), PY_KEY_OPEN_RE.match(text)
            merged_value = None
            if key_only or py_open:
                merged_value = _peek_multiline_string_value(lines, idx, concatenate=bool(py_open))
            if (key_only or py_open) and merged_value:
                skip_idxs, string_val, first_value_idx = merged_value
                skip_indices.update(skip_idxs)
                value_line_no = line_no + (first_value_idx - idx) if line_no >= 0 else -1
                key_name = (key_only or py_open).group(1)
                chunk = _compact_review_entry(path_label, value_line_no, [string_val], key_name=key_name)
                dedupe_key = f"{path_label}:{value_line_no}:{key_name}:{string_val}"
                if dedupe_key not in seen and chunk:
                    seen.add(dedupe_key)
                    review_chunks.append(chunk)
                    review_by_file.setdefault(path_label, []).append(chunk)
                continue
            if key_only or py_open:
                continue
            if should_skip_review_line(text):
                continue
            if STRUCT_OPEN_RE.match(text):
                continue
            hints: list[str] = []
            key_name = None
            path_lower = path_label.lower()
            is_csv = path_lower.endswith(".csv")
            if is_csv:
                if csv_row := parse_i18n_csv_row(text.strip()):
                    key_name, hints = csv_row[0], list(csv_row[1])
                else:
                    continue
            if not hints:
                if nested := extract_nested_locale_values(text.strip()):
                    key_name, hints = nested[0], list(nested[1])
            if not hints:
                if q_open := QUOTED_KEY_STRUCT_OPEN_RE.match(text.strip()):
                    outer_key = _json_unescape(q_open.group("key"))
                    if _looks_like_user_facing_locale_key(outer_key):
                        hints = [outer_key]
                    else:
                        continue
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
                    continue
                hints = [stripped]
            chunk = _compact_review_entry(path_label, line_no, hints, key_name=key_name)
            # Dedupe
            dedupe_key = f"{path_label}:{line_no}:{chunk}"
            if dedupe_key in seen or not chunk:
                continue
            seen.add(dedupe_key)
            review_chunks.append(chunk)
            review_by_file.setdefault(path_label, []).append(chunk)
            continue
        if line.startswith("-") and not line.startswith("---"):
            ensure_file(current_file or "(unknown)")["deleted"] += 1
            continue
        if line.startswith(" ") and new_line_no is not None:
            new_line_no += 1

    files_out: list[FileStat] = [
        {"path": files_map[p]["path"], "added": files_map[p]["added"], "deleted": files_map[p]["deleted"]}
        for p in files_order
    ]
    review_by_file_text = {p: "\n\n".join(c) for p, c in review_by_file.items() if c}
    review_text = "\n\n".join(review_chunks)
    # Compute pre/post optimization size (stderr only)
    sep = 2
    # We don't have legacy_chunk_chars filled here for all chunks, but we keep for compatibility
    # Actually we kept it but didn't fill all chunks; we can skip metrics in diff_parser
    # Or we can compute from review_text length as approximation.
    # For simplicity, we just output without legacy metric.
    return {
        "review_text": review_text,
        "review_by_file": review_by_file_text,
        "files": files_out,
        "_added_line_details": {p: files_map[p]["added_lines"] for p in files_order},
    }
