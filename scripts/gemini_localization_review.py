#!/usr/bin/env python3
"""Gemini Localization Quality Gate — review PR diffs for user-facing text issues.

CLI: python scripts/gemini_localization_review.py <diff_file>
Env: GEMINI_API_KEY (required), GITHUB_STEP_SUMMARY (optional)
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from collections import OrderedDict
from typing import Any, NamedTuple

import requests


class GeminiModelQuota(NamedTuple):
    model_id: str
    rpm: int
    rpd: int
    tpm: int | None = None


GEMINI_MODEL_QUOTAS: tuple[GeminiModelQuota, ...] = (
    GeminiModelQuota("gemini-3.5-flash-lite", rpm=15, rpd=500, tpm=250_000),
    GeminiModelQuota("gemini-3.1-flash-lite", rpm=15, rpd=500, tpm=250_000),
    GeminiModelQuota("gemini-3-flash-preview", rpm=5, rpd=20, tpm=250_000),
    GeminiModelQuota("gemini-3.5-flash", rpm=5, rpd=20, tpm=250_000),
    GeminiModelQuota("gemini-3.6-flash", rpm=5, rpd=20, tpm=250_000),
)
GEMINI_MODELS = tuple(q.model_id for q in GEMINI_MODEL_QUOTAS)
HTTP_TIMEOUT_SEC = 60
MAX_ATTEMPTS = 3
MAX_REVIEW_CHARS = 100_000  # default batch size for large EN packs
# Locale/short files: pack chunks so each file uses about 1–FOCUSED_TARGET_BATCHES API calls.
FOCUSED_TARGET_BATCHES = 3
SHORT_FILE_MAX_CHUNKS = 40
SHORT_FILE_MAX_CHARS = 20_000
QUOTA_RETRY_DEFAULT_SEC = 60.0
MAX_QUOTA_RETRIES = 5
CONTEXT_LINES = 1  # light neighbor window; kept small to avoid diluting focused batches
# Paths that need smaller focused batches for CJK/PT recall.
_FOCUSED_PATH_RE = re.compile(
    r"(?:chinese|portuguese|brazil|/zh(?:[-_/]|$)|_zh\.|zh_cn|zh-cn|zh_hans|"
    r"pt_br|pt-br|/pt(?:[-_/]|$)|_pt\.)",
    re.IGNORECASE,
)
RETRY_IN_RE = re.compile(r"retry in ([0-9]+(?:\.[0-9]+)?)\s*s", re.IGNORECASE)
DAILY_QUOTA_RE = re.compile(
    r"per\s*day|daily\s*quota|rpd|free_tier_requests|generate_content_free_tier_requests",
    re.IGNORECASE,
)
_active_model_index = 0


def reset_model_failover_state() -> None:
    global _active_model_index
    _active_model_index = 0


def active_model_quota() -> GeminiModelQuota:
    return GEMINI_MODEL_QUOTAS[_active_model_index]


def active_model_id() -> str:
    return active_model_quota().model_id


def min_request_interval_sec(rpm: int | None = None) -> float:
    limit = active_model_quota().rpm if rpm is None else rpm
    return 60.0 / limit + 0.1


def gemini_endpoint(model_id: str) -> str:
    return f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent"


def try_advance_model(reason: str) -> bool:
    global _active_model_index
    if _active_model_index + 1 >= len(GEMINI_MODEL_QUOTAS):
        return False
    prev, _active_model_index = GEMINI_MODEL_QUOTAS[_active_model_index], _active_model_index + 1
    nxt = GEMINI_MODEL_QUOTAS[_active_model_index]
    print(
        f"Gemini model failover: {prev.model_id} -> {nxt.model_id} "
        f"(RPM={nxt.rpm}/RPD={nxt.rpd}; {reason})",
        file=sys.stderr,
    )
    return True


def pace_after_model_failover() -> None:
    """Wait one full interval for the new model before the next request."""
    wait = min_request_interval_sec()
    print(
        f"Post-failover pace: sleeping {wait:.1f}s before next request on {active_model_id()}",
        file=sys.stderr,
    )
    time.sleep(wait)


PLACEHOLDER_RE = re.compile(r"\{[^}]*\}|%\w|\$\{[^}]*\}")
FENCE_RE = re.compile(r"^\s*```(?:json)?\s*\n?(.*?)\n?\s*```\s*$", re.DOTALL | re.IGNORECASE)
PROP_KEY = r"[A-Za-z_][A-Za-z0-9_]*"
KEY_ONLY_RE = re.compile(rf"^{PROP_KEY}\s*:?\s*,?\s*$")
KEY_ONLY_LINE_RE = re.compile(rf"^\s*({PROP_KEY})\s*:\s*$")
KEY_ASSIGN_PREFIX_RE = re.compile(rf"^\s*({PROP_KEY})\s*[:=]\s*$")
PY_KEY_OPEN_RE = re.compile(rf"^\s*([A-Z][A-Z0-9_]*)\s*=\s*\(\s*$")
PY_TRIPLE_OPEN_RE = re.compile(
    rf"""^\s*({PROP_KEY})\s*=\s*[fFrRbBuU]*(?P<q>\"\"\"|''')(?P<rest>.*)$"""
)
# Match quoted VALUE lines; honor escapes so \" / \' do not end the string early.
STRING_VALUE_LINE_RE = re.compile(
    r"""^\s*(['"])((?:\\.|(?!\1)[^\r\n])*)\1\s*,?\s*$"""
)
ASSIGNMENT_LINE_RE = re.compile(rf"""^\s*({PROP_KEY})\s*[:=]\s*(['"])(.*)\2\s*,?\s*$""", re.DOTALL)
JSON_KV_RE = re.compile(r"""^\s*"((?:\\.|[^"\\])*)"\s*:\s*"((?:\\.|[^"\\])*)"\s*,?\s*$""")
SKIP_LINE_RE = re.compile(
    r"""(?x)^\s*(?:import\b|from\b|export\s+default\b|export\s+const\b|
    const\s+\w+\s*=\s*\{|/\*|^\s*\*|^\s*//|\}|\{|,|\#)"""
)
# Syntax-only FP signals (identifier/key typos are forced to low elsewhere — not dropped here).
SYNTAX_PROBLEM_RE = re.compile(
    r"missing comma|extra comma|\bsyntax\b|missing colon|json structure|"
    r"javascript syntax|python syntax|typescript syntax|\bbrace\b|\bquote\b",
    re.IGNORECASE,
)
SEVERITY_HIGH, SEVERITY_MEDIUM, SEVERITY_LOW = "high", "medium", "low"
VALID_SEVERITIES = {SEVERITY_HIGH, SEVERITY_MEDIUM, SEVERITY_LOW}
_SEVERITY_RANK = {SEVERITY_HIGH: 3, SEVERITY_MEDIUM: 2, SEVERITY_LOW: 1}
HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
_STRUCT_TOKENS = frozenset(("{", "}", "},", "[", "],", "];", "};", ")", "),", "("))
_ID_PROBLEM_TOKENS = (
    "identifier", "constant name", "key name", "object key", "property name",
    "variable name", "key typo",
)
_WS_PROBLEM_RE = re.compile(
    r"leading\s+space|trailing\s+space|leading\s+whitespace|trailing\s+whitespace|"
    r"extra\s+space|whitespace\s+at\s+(the\s+)?(start|beginning|end)|"
    r"starts?\s+with\s+(a\s+)?space|ends?\s+with\s+(a\s+)?space|"
    r"前导空格|尾随空格|首尾空格",
    re.IGNORECASE,
)
_COMPLETE_FINISH_REASONS = frozenset({"STOP", "stop", "FINISH_REASON_STOP"})
_ISSUE_SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "file": {"type": "STRING"},
        "line": {"type": "INTEGER"},
        "original": {"type": "STRING"},
        "problem": {"type": "STRING"},
        "suggestion": {"type": "STRING"},
        "severity": {"type": "STRING", "enum": ["high", "medium", "low"]},
    },
    "required": ["original", "problem", "suggestion", "severity"],
}
RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "has_issue": {"type": "BOOLEAN"},
        "issues": {"type": "ARRAY", "items": _ISSUE_SCHEMA},
    },
    "required": ["has_issue", "issues"],
}


# Task brief. Severity/FP also enforced in postprocess + responseSchema.
def build_prompt(review_text: str) -> str:
    return f"""You are a Localization Quality Reviewer for the UnitX monorepo.
Review ONLY user-facing string VALUES (English / Simplified Chinese / Portuguese).
Formats: JS/TS KEY: 'value'; Python KEY = "..." / KEY = (\\n  "..."\\n); JSON; CSV language cells.
Input entries use compact form [file:line] then the VALUE (file/line required for PR annotations).
Multiline VALUES encode embedded newlines as \\n (one line under the header).

Rules:
1) original/suggestion = VALUE only — never whole KEY lines or bare "KEY =" / "KEY:".
2) Identifier/key typos MAY be reported at severity "low" only.
3) IGNORE syntax (commas, braces, multiline KEY then value — that is valid).
4) Keep placeholders identical ({{...}}, %s/%d, ${{...}}, Python {{}}). Never invent/remove them.
5) Leading/trailing whitespace style → severity "low" only (never high/medium).
6) Inspect EVERY VALUE carefully (character-level spelling/grammar/wrong words,
   including Chinese character mistakes, wrong characters, and incorrect word usage).
   Do not skip entries.
Ignore imports, URLs, paths, UUIDs, hashes, debug/internal comments.

Severity (lowercase): high = VALUE spelling/grammar/wrong word; medium = wording;
low = VALUE casing/whitespace style OR identifier/key typos. Only high blocks merge.

Return JSON only (schema enforced by API). Empty → {{"has_issue": false, "issues": []}}.

PR changes to review:
{review_text}
"""


def should_skip_review_line(text: str) -> bool:
    stripped = text.strip()
    return not stripped or SKIP_LINE_RE.match(stripped) or stripped in _STRUCT_TOKENS


def extract_user_facing_hints(text: str, path: str = "") -> list[str]:
    stripped = text.strip()
    if not stripped or should_skip_review_line(stripped):
        return []
    if m := JSON_KV_RE.match(stripped):
        return [m.group(2)]
    if m := ASSIGNMENT_LINE_RE.match(stripped):
        return [m.group(3)]
    if m := STRING_VALUE_LINE_RE.match(stripped):
        return [m.group(2)]
    lower_path = path.lower()
    if lower_path.endswith(".csv") or stripped.count(",") >= 2:
        if stripped.lower().startswith("key,"):
            return []
        parts = [p.strip() for p in stripped.split(",")]
        if len(parts) >= 2 and parts[0]:
            return [p for p in parts[1:] if p]
    return []


def _escape_review_value(value: str) -> str:
    """Escape embedded newlines in a VALUE for compact Gemini payload.

    Normalize CRLF/CR to the two-character sequence \\n so a multiline VALUE stays
    one physical line under [file:line] and is not read as another entry.
    """
    return (
        value.replace("\r\n", "\\n")
        .replace("\r", "\\n")
        .replace("\n", "\\n")
    )


def _compact_review_entry(path_label: str, line_no: int, values: list[str]) -> str:
    """Build one compact review entry for Gemini.

    Format (only allowed Gemini review_text shape):
      [file:line]
      <VALUE>

    Compact Gemini payload format reduces token usage while preserving file/line
    mapping required for PR annotations. Legacy verbose labels (# file / # line /
    user_facing: / source syntax) are intentionally omitted. Multiline VALUES use
    \\n escapes so only the header line carries structure.
    """
    cleaned = [v for v in values if v is not None and str(v) != ""]
    if not cleaned:
        return ""
    # Multiple cells (e.g. CSV) join with \\n on one VALUE line — same escape rules.
    escaped = [_escape_review_value(v) for v in cleaned]
    return f"[{path_label}:{line_no}]\n" + "\\n".join(escaped)


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
    """Approximate pre-optimization review chunk size (stderr metrics only; not sent)."""
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


def _multiline_review_chunk(
    path_label: str, line_no: int, user_facing_values: list[str], *,
    key_name: str | None = None, note: str | None = None, source_line: str | None = None,
) -> str:
    """Compact multiline VALUE payload (extraction / line tracking unchanged).

    key_name / note / source_line are accepted for call-site compatibility but
    omitted from the Gemini payload. Newlines inside VALUE are escaped by
    _compact_review_entry; file+line stay in the compact header for annotations.
    """
    _ = (key_name, note, source_line)
    return _compact_review_entry(path_label, line_no, user_facing_values)


def _print_review_text_optimization(before: int, after: int) -> None:
    """Temporary stderr metric: review_text size before/after compact format."""
    if before <= 0:
        reduction = 0.0
    else:
        reduction = (before - after) * 100.0 / before
    print(
        "Review text optimization:\n"
        f"before={before} chars\n"
        f"after={after} chars\n"
        f"reduction={reduction:.1f}%",
        file=sys.stderr,
    )


def split_text_for_limit(text: str, limit: int) -> list[str]:
    if limit <= 0:
        raise ValueError("limit must be positive")
    if not text:
        return []
    if len(text) <= limit:
        return [text]
    pieces, start, n = [], 0, len(text)
    while start < n:
        remaining = n - start
        if remaining <= limit:
            pieces.append(text[start:])
            break
        window_end = start + limit
        cut = text.rfind("\n\n", start + 1, window_end + 1)
        if cut > start:
            cut += 2
        else:
            cut = text.rfind("\n", start + 1, window_end + 1)
            cut = cut + 1 if cut > start else window_end
        pieces.append(text[start:cut])
        start = cut
    return pieces


def normalize_issue_to_string_value(issue: dict[str, Any]) -> dict[str, Any]:
    """Normalize KEY/value shapes. Preserve significant leading/trailing spaces in VALUES."""
    out = dict(issue)
    original_raw = out.get("original", "")
    suggestion_raw = out.get("suggestion", "")
    # Do not .strip() before matching: VALUE leading/trailing whitespace is meaningful
    # (forced to low later). Assignment / key-prefix patterns already allow ^\\s*.
    o_m = ASSIGNMENT_LINE_RE.match(original_raw)
    s_m = ASSIGNMENT_LINE_RE.match(suggestion_raw)
    if o_m and s_m:
        if o_m.group(1) != s_m.group(1):
            out.update(original=o_m.group(1), suggestion=s_m.group(1), _kind="identifier")
            return out
        out.update(original=o_m.group(3), suggestion=s_m.group(3), _kind="value")
        return out
    if o_m and not s_m:
        out.update(original=o_m.group(3), _kind="value")
        if suggestion_raw:
            out["suggestion"] = suggestion_raw
        return out
    # Model sometimes emits bare "KEY =" / "KEY:" instead of the quoted VALUE.
    if m := KEY_ASSIGN_PREFIX_RE.match(original_raw):
        out["_recover_original"] = True
        out["_key_name"] = m.group(1)
        if suggestion_raw and not KEY_ASSIGN_PREFIX_RE.match(suggestion_raw):
            out["suggestion"] = suggestion_raw
        return out
    # Keep raw strings so intentional leading spaces are not stripped away.
    out["original"] = original_raw
    out["suggestion"] = suggestion_raw
    return out


def looks_like_code_key(text: str) -> bool:
    s = text.strip().rstrip(",").rstrip(":")
    if not s or not re.match(rf"^{PROP_KEY}$", s):
        return False
    if "_" in s or (s.isupper() and len(s) >= 3) or re.match(r"^[a-z]+[A-Z]", s):
        return True
    return False


def is_identifier_issue(issue: dict[str, Any]) -> bool:
    """True for key/constant renames — kept as low, never blocks merge."""
    if issue.get("_kind") == "identifier":
        return True
    problem = issue.get("problem", "").lower()
    if any(t in problem for t in _ID_PROBLEM_TOKENS) and not any(
        w in problem for w in ("comma", "syntax", "colon")
    ):
        return True
    original = issue.get("original", "").strip()
    suggestion = issue.get("suggestion", "").strip()
    if looks_like_code_key(original) and looks_like_code_key(suggestion):
        o_key = original.rstrip().rstrip(",").rstrip(":")
        s_key = suggestion.rstrip().rstrip(",").rstrip(":")
        return o_key != s_key
    return False


def is_whitespace_style_issue(issue: dict[str, Any]) -> bool:
    """Leading/trailing whitespace style — informational low, never blocks."""
    if _WS_PROBLEM_RE.search(issue.get("problem", "") or ""):
        return True
    original, suggestion = issue.get("original", ""), issue.get("suggestion", "")
    if original and suggestion and original != suggestion and original.strip() == suggestion.strip():
        return True
    return False


def is_syntax_false_positive(issue: dict[str, Any]) -> bool:
    original = issue.get("original", "").strip()
    problem = issue.get("problem", "")
    if SYNTAX_PROBLEM_RE.search(problem):
        return True
    if looks_like_code_key(original) or KEY_ONLY_RE.match(original):
        suggestion = issue.get("suggestion", "").strip()
        if looks_like_code_key(suggestion) or KEY_ONLY_RE.match(suggestion):
            o_key = original.rstrip().rstrip(",").rstrip(":")
            s_key = suggestion.rstrip().rstrip(",").rstrip(":")
            if o_key == s_key:
                return True
        elif not suggestion:
            return True
    if re.match(rf"^{PROP_KEY}\s*:$", original):
        suggestion = issue.get("suggestion", "").strip()
        o_key = original.rstrip(":")
        if s_m := re.match(rf"^({PROP_KEY})\s*:?\s*,?\s*$", suggestion):
            if s_m.group(1) == o_key:
                return True
        else:
            return True
    return False


def _lookup_added_value(
    added_details: dict[str, list[dict[str, Any]]],
    path: str | None,
    line: Any,
    key_name: str | None = None,
) -> tuple[str | None, int | None]:
    paths = [path] if path in (added_details or {}) else list(added_details or {})
    line_no = line if isinstance(line, int) else None
    for p in paths:
        rows = added_details.get(p) or []
        if line_no and line_no > 0:
            for row in rows:
                if row.get("line") == line_no:
                    hints = extract_user_facing_hints(row.get("text", ""), p or "")
                    if hints:
                        return hints[0], row.get("line")
        if key_name:
            for row in rows:
                text = row.get("text", "")
                if re.search(rf"\b{re.escape(key_name)}\b\s*[:=]", text):
                    hints = extract_user_facing_hints(text, p or "")
                    if hints:
                        return hints[0], row.get("line")
    return None, None


def recover_key_prefix_originals(
    issues: list[dict[str, Any]], added_details: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    """Replace bare 'KEY =' originals with the quoted VALUE from the diff."""
    recovered = []
    for issue in issues:
        out = dict(issue)
        orig = (out.get("original") or "").strip()
        need = out.pop("_recover_original", False) or bool(KEY_ASSIGN_PREFIX_RE.match(orig))
        if not need:
            recovered.append(out)
            continue
        key_name = out.pop("_key_name", None)
        if not key_name and (m := KEY_ASSIGN_PREFIX_RE.match(orig)):
            key_name = m.group(1)
        value, found_line = _lookup_added_value(
            added_details, out.get("file"), out.get("line"), key_name,
        )
        if value is not None:
            out["original"] = value
            if found_line and (not isinstance(out.get("line"), int) or out.get("line", -1) <= 0):
                out["line"] = found_line
            sugg = out.get("suggestion", "")
            # If model only gave a stripped value, keep it; if suggestion is still a key prefix, fix.
            if not sugg or KEY_ASSIGN_PREFIX_RE.match(sugg.strip()):
                out["suggestion"] = value.lstrip() if value[:1].isspace() else value
        recovered.append(out)
    return recovered


def filter_userfacing_issues(
    issues: list[dict[str, Any]], *, already_normalized: bool = False,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Drop syntax FPs; force identifier / whitespace-style findings to low."""
    kept, dropped = [], []
    for issue in issues:
        normalized = issue if already_normalized else normalize_issue_to_string_value(issue)
        if is_syntax_false_positive(normalized):
            dropped.append(issue)
            continue
        if KEY_ASSIGN_PREFIX_RE.match((normalized.get("original") or "").strip()):
            # Bare "KEY =" that could not be recovered to a VALUE — drop.
            dropped.append(issue)
            continue
        if is_identifier_issue(normalized) or is_whitespace_style_issue(normalized):
            normalized["severity"] = SEVERITY_LOW
        normalized.pop("_kind", None)
        normalized.pop("_recover_original", None)
        normalized.pop("_key_name", None)
        kept.append(normalized)
    return kept, dropped


def _new_file_entry(path: str) -> dict[str, Any]:
    return {"path": path, "added": 0, "deleted": 0, "added_lines": []}


def _peek_multiline_string_value(
    lines: list[str], start_idx: int, *, concatenate: bool = False, max_scan: int | None = None,
) -> tuple[list[int], str, int] | None:
    """Collect following +'...' lines. max_scan=None scans until hunk/meta/non-match."""
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
    """Parse KEY = \"\"\"...\"\"\" spanning one or more +diff lines.

    Returns (skip_indices, value, first_value_idx).
    - skip_indices: +diff line indices AFTER start_idx that belong to this literal
      (caller must not re-review them). start_idx is never included — the caller
      already owns the opener line.
    - One-liner KEY = \"\"\"value\"\"\" → skip=[], first_value_idx=start_idx.
    """
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


def analyze_diff(diff_text: str) -> dict[str, Any]:
    if not diff_text or not diff_text.strip():
        return {"review_text": "", "files": []}
    lines = diff_text.splitlines()
    files_order: list[str] = []
    files_map: dict[str, dict[str, Any]] = {}
    current_file, new_line_no = "", None
    review_chunks: list[str] = []
    review_by_file: OrderedDict[str, list[str]] = OrderedDict()
    seen, skip_indices = set(), set()
    # Pre-optimization size estimate (legacy verbose format) for stderr metrics only.
    legacy_chunk_chars: list[int] = []

    def ensure_file(path: str) -> dict[str, Any]:
        if path not in files_map:
            files_map[path] = _new_file_entry(path)
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
                merged_triple = _peek_triple_quoted_string(
                    lines, idx, triple.group("q"), triple.group("rest"),
                )
                if merged_triple is not None:
                    skip_idxs, string_val, first_value_idx = merged_triple
                    skip_indices.update(skip_idxs)
                    value_line_no = line_no + (first_value_idx - idx) if line_no >= 0 else -1
                    key_name = triple.group(1)
                    source_line = (
                        f"+  {key_name} = {triple.group('q')}...{triple.group('q')}"
                    )
                    note = "python triple-quoted string"
                    chunk = _multiline_review_chunk(
                        path_label, value_line_no, [string_val], key_name=key_name,
                        note=note, source_line=source_line,
                    )
                    dedupe_key = f"{path_label}:{value_line_no}:{key_name}:{string_val}"
                    if dedupe_key not in seen and chunk:
                        seen.add(dedupe_key)
                        review_chunks.append(chunk)
                        review_by_file.setdefault(path_label, []).append(chunk)
                        legacy_chunk_chars.append(
                            _legacy_review_chunk_chars(
                                path_label, value_line_no, [string_val],
                                key_name=key_name, note=note, source_line=source_line,
                            )
                        )
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
                opener = f"{key_name}:" if key_only else f"{key_name} = ("
                source_line = f"+  {opener}\n+    {string_val!r}"
                note = "multiline KEY + string value (valid formatting)"
                chunk = _multiline_review_chunk(
                    path_label, value_line_no, [string_val], key_name=key_name,
                    note=note, source_line=source_line,
                )
                dedupe_key = f"{path_label}:{value_line_no}:{key_name}:{string_val}"
                if dedupe_key not in seen and chunk:
                    seen.add(dedupe_key)
                    review_chunks.append(chunk)
                    review_by_file.setdefault(path_label, []).append(chunk)
                    legacy_chunk_chars.append(
                        _legacy_review_chunk_chars(
                            path_label, value_line_no, [string_val],
                            key_name=key_name, note=note, source_line=source_line,
                        )
                    )
                continue
            if key_only or py_open:
                continue
            if should_skip_review_line(text):
                continue
            hints = extract_user_facing_hints(text, path_label)
            if not hints:
                # Unstructured added text (no KEY/JSON extract): review the line body
                # as VALUE — same coverage as the old raw-window path, without metadata.
                stripped = text.strip()
                if not stripped:
                    continue
                hints = [stripped]
            # CONTEXT_LINES remains 1 for hard-split overlap elsewhere. Neighbor raw
            # diff lines / duplicated peer VALUES are omitted from each entry: they
            # inflated tokens without improving VALUE spelling review once each line
            # already has its own compact [file:line] entry.
            chunk = _compact_review_entry(path_label, line_no, hints)
            start = max(0, idx - CONTEXT_LINES)
            end = min(len(lines), idx + CONTEXT_LINES + 1)
            window = [
                lines[j] for j in range(start, end)
                if not lines[j].startswith(("---", "+++", "@@")) and lines[j].strip()
            ]
            legacy_context = "\n".join(window) if window else f"+{text}"
            dedupe_key = f"{path_label}:{line_no}:{chunk}"
            if dedupe_key in seen or not chunk:
                continue
            seen.add(dedupe_key)
            review_chunks.append(chunk)
            review_by_file.setdefault(path_label, []).append(chunk)
            legacy_chunk_chars.append(
                _legacy_review_chunk_chars(
                    path_label, line_no, hints, context_body=legacy_context,
                )
            )
            continue
        if line.startswith("-") and not line.startswith("---"):
            ensure_file(current_file or "(unknown)")["deleted"] += 1
            continue
        if line.startswith(" ") and new_line_no is not None:
            new_line_no += 1
    files_out = [
        {"path": files_map[p]["path"], "added": files_map[p]["added"], "deleted": files_map[p]["deleted"]}
        for p in files_order
    ]
    review_by_file_text = {p: "\n\n".join(c) for p, c in review_by_file.items() if c}
    review_text = "\n\n".join(review_chunks)
    sep = 2  # "\n\n" between chunks
    before = sum(legacy_chunk_chars) + sep * max(0, len(legacy_chunk_chars) - 1)
    after = len(review_text)
    _print_review_text_optimization(before, after)
    return {
        "review_text": review_text,
        "review_by_file": review_by_file_text,
        "files": files_out,
        "_added_line_details": {p: files_map[p]["added_lines"] for p in files_order},
    }


def parse_diff(diff_text: str) -> str:
    return analyze_diff(diff_text)["review_text"]


def print_files_report(files: list[dict[str, Any]]) -> None:
    if not files:
        print("Diff scope: (no files)", file=sys.stderr)
        return
    print("Diff scope:", file=sys.stderr)
    for item in files:
        print(f"  {item['path']}  +{item['added']} -{item['deleted']}", file=sys.stderr)


def _value_exact_in_line(needle: str, text: str) -> bool:
    stripped = text.strip().rstrip(",").strip()
    if needle == stripped:
        return True
    if m := ASSIGNMENT_LINE_RE.match(stripped):
        return m.group(3) == needle
    if m := JSON_KV_RE.match(stripped):
        return m.group(2) == needle
    if m := STRING_VALUE_LINE_RE.match(stripped):
        return m.group(2) == needle
    return False


def attach_locations(
    issues: list[dict[str, Any]], added_details: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    """Fill missing file/line only; never overwrite a positive line; require a unique hit."""
    enriched = []
    for issue in issues:
        out = dict(issue)
        raw = out.get("original") or ""
        needle = raw.strip()
        if not needle:
            enriched.append(out)
            continue
        if out.get("file") and isinstance(out.get("line"), int) and out["line"] > 0:
            enriched.append(out)
            continue
        paths = [out["file"]] if out.get("file") in added_details else list(added_details)
        exact, soft = [], []
        for path in paths:
            for row in added_details.get(path, []):
                text = row["text"]
                hit = (path, row["line"])
                # Prefer exact VALUE match including intentional leading spaces.
                if _value_exact_in_line(raw, text) or _value_exact_in_line(needle, text):
                    exact.append(hit)
                elif f'"{needle}"' in text or f"'{needle}'" in text:
                    soft.append(hit)
                elif len(needle) >= 8 and needle in text:
                    soft.append(hit)
        hits = exact or soft
        if len(hits) == 1:
            out["file"], out["line"] = hits[0]
        enriched.append(out)
    return enriched


def strip_markdown_fence(text: str) -> str:
    stripped = text.strip()
    if m := FENCE_RE.match(stripped):
        return m.group(1).strip()
    return stripped


def extract_response_text(api_payload: dict[str, Any]) -> str:
    assert_generation_complete(api_payload)
    try:
        return api_payload["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError(f"Unexpected Gemini response shape: {exc}") from exc


def assert_generation_complete(api_payload: dict[str, Any]) -> None:
    try:
        candidate = api_payload["candidates"][0]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError(f"Gemini response has no candidates: {exc}") from exc
    reason = candidate.get("finishReason") or candidate.get("finish_reason")
    if reason is None:
        return
    if reason not in _COMPLETE_FINISH_REASONS:
        raise ValueError(f"Gemini generation incomplete: finishReason={reason!r}")


def validate_result(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Result root must be an object")
    if "has_issue" not in payload or "issues" not in payload:
        raise ValueError("Result must contain has_issue and issues")
    if not isinstance(payload["has_issue"], bool):
        raise ValueError("has_issue must be boolean")
    if not isinstance(payload["issues"], list):
        raise ValueError("issues must be an array")
    issues = payload["issues"]
    if payload["has_issue"] is False and issues:
        raise ValueError("has_issue=false but issues is non-empty")
    if issues and payload["has_issue"] is not True:
        raise ValueError("issues is non-empty but has_issue is not true")
    validated_issues, skipped_reasons = [], []
    for i, issue in enumerate(issues):
        if not isinstance(issue, dict):
            skipped_reasons.append(f"issues[{i}]: not an object")
            continue
        bad_field = None
        for field in ("original", "problem", "suggestion", "severity"):
            if field not in issue:
                bad_field = f"missing {field}"
                break
            if not isinstance(issue[field], str) or not issue[field].strip():
                bad_field = f"empty {field}"
                break
        if bad_field:
            skipped_reasons.append(f"issues[{i}]: {bad_field}")
            continue
        severity = issue["severity"].strip().lower()
        if severity not in VALID_SEVERITIES:
            skipped_reasons.append(f"issues[{i}]: invalid severity {issue['severity']!r}")
            continue
        # Preserve VALUE whitespace (leading/trailing spaces may be intentional).
        # Only trim problem text; emptiness already validated via .strip() above.
        item: dict[str, Any] = {
            "original": issue["original"],
            "problem": issue["problem"].strip(),
            "suggestion": issue["suggestion"],
            "severity": severity,
        }
        if isinstance(issue.get("file"), str) and issue["file"].strip():
            item["file"] = issue["file"].strip()
        if "line" in issue:
            try:
                item["line"] = int(issue["line"])
            except (TypeError, ValueError):
                item["line"] = -1
        validated_issues.append(item)
    if skipped_reasons:
        for reason in skipped_reasons[:10]:
            print(f"Malformed model issue: {reason}", file=sys.stderr)
        raise ValueError(
            f"Dropped {len(skipped_reasons)} malformed issue(s) from model output "
            "(fail-closed; refusing partial/invalid result)"
        )
    has_issue = bool(validated_issues)
    if payload["has_issue"] is False and validated_issues:
        has_issue = True
    return {"has_issue": has_issue, "issues": validated_issues}


def parse_model_json(raw_text: str) -> dict[str, Any]:
    cleaned = strip_markdown_fence(raw_text)
    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON from model: {exc}") from exc
    return validate_result(payload)


def placeholders(text: str) -> set[str]:
    return set(PLACEHOLDER_RE.findall(text))


def filter_placeholder_mismatches(
    issues: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    kept, dropped = [], []
    for issue in issues:
        if placeholders(issue["original"]) != placeholders(issue["suggestion"]):
            dropped.append(issue)
        else:
            kept.append(issue)
    return kept, dropped


def count_by_severity(issues: list[dict[str, str]]) -> dict[str, int]:
    counts = {SEVERITY_HIGH: 0, SEVERITY_MEDIUM: 0, SEVERITY_LOW: 0}
    for issue in issues:
        counts[issue["severity"]] = counts.get(issue["severity"], 0) + 1
    return counts


def has_blocking_issues(issues: list[dict[str, str]]) -> bool:
    return any(issue["severity"] == SEVERITY_HIGH for issue in issues)


def _md_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def format_step_summary(
    *, status: str, issues: list[dict[str, Any]], duration_sec: float | None,
    usage: str = "N/A", extra_note: str = "",
    files: list[dict[str, Any]] | None = None, usage_stats: dict[str, Any] | None = None,
) -> str:
    counts = count_by_severity(issues)
    duration = f"{duration_sec:.1f}s" if duration_sec is not None else "N/A"
    lines = [
        "## Localization Quality Gate", "",
        f"- Status: {status}",
        f"- High: {counts[SEVERITY_HIGH]} | Medium: {counts[SEVERITY_MEDIUM]} | Low: {counts[SEVERITY_LOW]}",
        f"- Duration: {duration}",
        f"- Token usage: {usage}",
    ]
    if usage_stats:
        models_s, limits_s = _models_and_limits_text(usage_stats, compact=False)
        lines.extend([
            f"- Models: {models_s}",
            f"- API requests: {usage_stats['requests']} (paced ≥{usage_stats['min_interval_sec']:.1f}s; limits {limits_s})",
            f"- Tokens: prompt={usage_stats['prompt_tokens']} candidates={usage_stats['candidates_tokens']} total={usage_stats['total_tokens']}",
            f"- Review payload: sent={usage_stats['chars_sent']} chars, "
            f"batches={usage_stats['batches']}, files={usage_stats['files_reviewed']}",
        ])
    if extra_note:
        lines.append(f"- Note: {extra_note}")
    lines.extend(["", "### Changed files", ""])
    if not files:
        lines.append("_No files in scope._")
    else:
        lines.extend(["| File | Added | Deleted |", "| --- | ---: | ---: |"])
        for item in files:
            lines.append(f"| {_md_cell(item['path'])} | {item['added']} | {item['deleted']} |")
    lines.extend(["", "### Issues", ""])
    if not issues:
        lines.append("_No issues reported._")
    else:
        lines.extend(["| Severity | File | Line | Original | Problem | Suggestion |", "| --- | --- | ---: | --- | --- | --- |"])
        for issue in issues:
            lines.append(
                "| {severity} | {file} | {line} | {original} | {problem} | {suggestion} |".format(
                    severity=_md_cell(str(issue["severity"])),
                    file=_md_cell(str(issue.get("file") or "-")),
                    line=issue.get("line", "-"),
                    original=_md_cell(str(issue["original"])),
                    problem=_md_cell(str(issue["problem"])),
                    suggestion=_md_cell(str(issue["suggestion"])),
                )
            )
    lines.append("")
    return "\n".join(lines)


def append_step_summary(markdown: str) -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(markdown)
        if not markdown.endswith("\n"):
            handle.write("\n")


def is_daily_quota_error(body: str) -> bool:
    return bool(DAILY_QUOTA_RE.search(body or ""))


def parse_retry_after_seconds(response: requests.Response) -> float:
    header = response.headers.get("Retry-After") or response.headers.get("retry-after")
    if header:
        try:
            return max(float(header), QUOTA_RETRY_DEFAULT_SEC)
        except ValueError:
            pass
    if match := RETRY_IN_RE.search(response.text or ""):
        try:
            return max(float(match.group(1)), 1.0)
        except ValueError:
            pass
    return QUOTA_RETRY_DEFAULT_SEC


def _sleep_transient_backoff(attempt: int) -> None:
    time.sleep(2 ** (attempt - 1))


def call_gemini(api_key: str, prompt: str) -> tuple[dict[str, Any], float]:
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0,
            "responseMimeType": "application/json",
            "responseSchema": RESPONSE_SCHEMA,
        },
    }
    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
    start = time.monotonic()
    quota_retries = transient_attempts = 0
    while True:
        model_id = active_model_id()
        url = gemini_endpoint(model_id)
        try:
            response = requests.post(url, json=body, headers=headers, timeout=HTTP_TIMEOUT_SEC)
        except requests.Timeout as exc:
            transient_attempts += 1
            if transient_attempts >= MAX_ATTEMPTS:
                raise RuntimeError(f"Gemini API timeout after {MAX_ATTEMPTS} attempts") from exc
            _sleep_transient_backoff(transient_attempts)
            continue
        except requests.RequestException as exc:
            raise RuntimeError(f"Gemini API request failed: {exc}") from exc
        if response.status_code == 200:
            try:
                return response.json(), time.monotonic() - start
            except ValueError as exc:
                raise RuntimeError(f"Gemini returned non-JSON body: {response.text[:500]}") from exc
        if response.status_code == 429:
            text = response.text or ""
            if is_daily_quota_error(text):
                if try_advance_model(f"RPD/daily quota exhausted on {model_id}"):
                    quota_retries = transient_attempts = 0
                    pace_after_model_failover()
                    continue
                raise RuntimeError(
                    "Gemini RPD/daily quota exhausted on all models "
                    f"({', '.join(GEMINI_MODELS)}) — retry tomorrow or upgrade Usage Tier. "
                    f"Body: {text[:800]}"
                )
            wait = parse_retry_after_seconds(response)
            quota_retries += 1
            if quota_retries > MAX_QUOTA_RETRIES:
                if try_advance_model(f"RPM/TPM still exhausted after {MAX_QUOTA_RETRIES} waits on {model_id}"):
                    quota_retries = transient_attempts = 0
                    pace_after_model_failover()
                    continue
                raise RuntimeError(
                    f"Gemini RPM/TPM still exhausted after {MAX_QUOTA_RETRIES} waits on all models. "
                    f"Body: {text[:800]}"
                )
            print(
                f"HTTP 429 (RPM/TPM on {model_id}). Waiting {wait:.1f}s then auto-retry "
                f"({quota_retries}/{MAX_QUOTA_RETRIES}) — no need to reopen PR",
                file=sys.stderr,
            )
            time.sleep(wait)
            continue
        if response.status_code in (500, 503):
            transient_attempts += 1
            if transient_attempts >= MAX_ATTEMPTS:
                raise RuntimeError(
                    f"Gemini API failed with HTTP {response.status_code}: {response.text[:1000]}"
                )
            _sleep_transient_backoff(transient_attempts)
            continue
        raise RuntimeError(
            f"Gemini API failed with HTTP {response.status_code}: {response.text[:1000]}"
        )


def extract_usage_counts(api_payload: dict[str, Any]) -> dict[str, int]:
    meta = api_payload.get("usageMetadata") or api_payload.get("usage_metadata")
    if not isinstance(meta, dict):
        return {}
    mapping = {
        "promptTokenCount": "prompt", "prompt_token_count": "prompt",
        "candidatesTokenCount": "candidates", "candidates_token_count": "candidates",
        "totalTokenCount": "total", "total_token_count": "total",
    }
    out: dict[str, int] = {}
    for src, dst in mapping.items():
        if src in meta:
            try:
                out[dst] = int(meta[src])
            except (TypeError, ValueError):
                continue
    return out


def empty_usage_stats() -> dict[str, Any]:
    primary = GEMINI_MODEL_QUOTAS[0]
    return {
        "requests": 0, "prompt_tokens": 0, "candidates_tokens": 0, "total_tokens": 0,
        "batches": 0, "chars_sent": 0, "files_reviewed": 0,
        "models_used": [], "model_limits": {},
        "rpm_limit": primary.rpm, "tpm_limit": primary.tpm or 0, "rpd_limit": primary.rpd,
        "min_interval_sec": min_request_interval_sec(primary.rpm),
    }


def record_model_usage(stats: dict[str, Any], quota: GeminiModelQuota) -> None:
    mid = quota.model_id
    if mid not in stats["models_used"]:
        stats["models_used"].append(mid)
    stats["model_limits"][mid] = {
        "rpm": quota.rpm, "rpd": quota.rpd, "tpm": quota.tpm,
        "min_interval_sec": min_request_interval_sec(quota.rpm),
    }
    stats["rpm_limit"], stats["rpd_limit"] = quota.rpm, quota.rpd
    stats["tpm_limit"] = quota.tpm or 0
    stats["min_interval_sec"] = min_request_interval_sec(quota.rpm)


def _models_and_limits_text(stats: dict[str, Any], *, compact: bool = False) -> tuple[str, str]:
    models = stats.get("models_used") or []
    models_s = (",".join(models) if compact else ", ".join(models)) if models else active_model_id()
    model_limits = stats.get("model_limits") or {}
    if model_limits:
        parts = []
        for mid, lim in model_limits.items():
            if compact:
                parts.append(f"{mid}:RPM={lim['rpm']}/RPD={lim['rpd']}")
            else:
                piece = f"{mid} RPM={lim['rpm']}/RPD={lim['rpd']}"
                if lim.get("tpm"):
                    piece += f"/TPM={lim['tpm']}"
                parts.append(piece)
        limits_s = (";" if compact else "; ").join(parts)
    elif compact:
        limits_s = f"RPM={stats['rpm_limit']}/TPM={stats['tpm_limit']}/RPD={stats['rpd_limit']}"
    else:
        limits_s = f"RPM={stats['rpm_limit']} TPM={stats['tpm_limit']} RPD={stats['rpd_limit']}"
    return models_s, limits_s


def format_usage_summary(stats: dict[str, Any]) -> str:
    models_s, limits_s = _models_and_limits_text(stats, compact=True)
    return (
        f"requests={stats['requests']} (limits {limits_s}), models={models_s}, "
        f"prompt_tokens={stats['prompt_tokens']}, candidates_tokens={stats['candidates_tokens']}, "
        f"total_tokens={stats['total_tokens']}, chars_sent={stats['chars_sent']}, "
        f"batches={stats['batches']}, "
        f"files={stats['files_reviewed']}, pace>={stats['min_interval_sec']:.1f}s/req"
    )


def review_chunks(review_text: str) -> list[str]:
    return [c for c in review_text.split("\n\n") if c.strip()]


def prefers_focused_batches(path: str, review_text: str) -> bool:
    """Chinese/PT locale paths, or short files: use ~1–FOCUSED_TARGET_BATCHES requests."""
    if _FOCUSED_PATH_RE.search(path or ""):
        return True
    chunks = review_chunks(review_text)
    return (
        0 < len(chunks) <= SHORT_FILE_MAX_CHUNKS
        and len(review_text) <= SHORT_FILE_MAX_CHARS
    )


def focused_max_chunks_per_batch(chunk_count: int) -> int:
    """Pack chunks so a focused file stays within about FOCUSED_TARGET_BATCHES requests."""
    if chunk_count <= 0:
        return 1
    if chunk_count <= FOCUSED_TARGET_BATCHES:
        return chunk_count  # single request
    return (chunk_count + FOCUSED_TARGET_BATCHES - 1) // FOCUSED_TARGET_BATCHES


def split_into_batches(
    review_text: str,
    limit: int | None = None,
    *,
    max_chunks_per_batch: int | None = None,
) -> list[str]:
    """Pack whole review chunks (\\n\\n-separated). Only hard-split a chunk if it alone exceeds limit."""
    if limit is None:
        limit = MAX_REVIEW_CHARS
    if not review_text.strip():
        return []
    chunks = review_chunks(review_text)
    if not chunks:
        return []
    if max_chunks_per_batch is not None and max_chunks_per_batch <= 0:
        raise ValueError("max_chunks_per_batch must be positive when set")
    batches: list[str] = []
    current: list[str] = []
    current_len = 0
    sep = "\n\n"

    def flush() -> None:
        nonlocal current, current_len
        if current:
            batches.append(sep.join(current))
            current, current_len = [], 0

    for chunk in chunks:
        if len(chunk) > limit:
            flush()
            hard = split_text_for_limit(chunk, limit)
            # Overlap last CONTEXT_LINES of previous hard piece into the next.
            for i, piece in enumerate(hard):
                if i == 0:
                    batches.append(piece)
                    continue
                prev_tail = "\n".join(hard[i - 1].splitlines()[-CONTEXT_LINES:])
                merged = f"{prev_tail}\n{piece}" if prev_tail else piece
                if len(merged) <= limit:
                    batches.append(merged)
                else:
                    batches.append(piece)
            continue
        add_len = len(chunk) + (len(sep) if current else 0)
        chunk_cap = (
            max_chunks_per_batch is not None and len(current) >= max_chunks_per_batch
        )
        if current and (current_len + add_len > limit or chunk_cap):
            flush()
        current.append(chunk)
        current_len += len(chunk) + (len(sep) if current_len else 0)
    flush()
    return batches


def with_batch_continuation_header(path: str, batch: str, *, batch_index: int) -> str:
    """Re-anchor hard-split batches using compact [path] only.

    Compact Gemini payload format reduces token usage while preserving file/line
    mapping required for PR annotations. Never emit legacy # file / # note /
    user_facing: labels. Batches that already start with [file:...] need no header.
    """
    stripped = batch.lstrip()
    if batch_index == 0 or stripped.startswith("["):
        return batch
    return f"[{path}]\n\n{batch}"


def _log_filtered(dropped: list[dict[str, Any]], label: str, *, show_samples: bool = False) -> None:
    if not dropped:
        return
    print(f"Filtered {len(dropped)} {label}", file=sys.stderr)
    if show_samples:
        for bad in dropped[:5]:
            print(
                f"  drop: original={bad.get('original')!r} suggestion={bad.get('suggestion')!r}",
                file=sys.stderr,
            )


def dedupe_issues(issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collapse overlap/batch duplicates; keep the highest severity per finding."""
    best: dict[tuple[Any, ...], dict[str, Any]] = {}
    order: list[tuple[Any, ...]] = []
    for issue in issues:
        key = (
            issue.get("file"),
            issue.get("line"),
            issue.get("original"),
            issue.get("suggestion"),
        )
        prev = best.get(key)
        if prev is None:
            best[key] = issue
            order.append(key)
            continue
        if _SEVERITY_RANK.get(issue.get("severity"), 0) > _SEVERITY_RANK.get(prev.get("severity"), 0):
            best[key] = issue
    return [best[k] for k in order]


def postprocess_issues(
    issues: list[dict[str, Any]], added_details: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    issues = attach_locations(issues, added_details)
    normalized = [normalize_issue_to_string_value(i) for i in issues]
    recovered = recover_key_prefix_originals(normalized, added_details)
    kept, dropped = filter_userfacing_issues(recovered, already_normalized=True)
    _log_filtered(dropped, "syntax/non-localization false positive(s)")
    kept, ph_dropped = filter_placeholder_mismatches(kept)
    if ph_dropped:
        _log_filtered(
            ph_dropped,
            "issue(s) with placeholder mismatch "
            "(suggestion must not add/remove placeholders like %d / {id})",
            show_samples=True,
        )
    before = len(kept)
    kept = dedupe_issues(kept)
    if len(kept) < before:
        print(f"Deduped {before - len(kept)} duplicate issue(s)", file=sys.stderr)
    return kept


def review_by_file_sessions(
    api_key: str, review_by_file: dict[str, str],
) -> tuple[list[dict[str, Any]], float, dict[str, Any]]:
    all_issues, total_duration, stats, last_request_at = [], 0.0, empty_usage_stats(), 0.0
    for path, text in review_by_file.items():
        if not text.strip():
            continue
        focused = prefers_focused_batches(path, text)
        chunks = review_chunks(text)
        pack = focused_max_chunks_per_batch(len(chunks)) if focused else None
        batches = split_into_batches(text, max_chunks_per_batch=pack)
        stats["files_reviewed"] += 1
        stats["batches"] += len(batches)
        mode = (
            f"focused(≤{FOCUSED_TARGET_BATCHES} batches, {pack} chunk(s)/req)"
            if focused
            else "packed"
        )
        print(
            f"Review session: {path} — {len(text)} chars, {len(batches)} batch(es), {mode}",
            file=sys.stderr,
        )
        for i, raw_batch in enumerate(batches):
            batch = with_batch_continuation_header(path, raw_batch, batch_index=i)
            if len(batches) > 1:
                print(f"  batch {i + 1}/{len(batches)}: {len(batch)} chars", file=sys.stderr)
            quota = active_model_quota()
            interval = min_request_interval_sec(quota.rpm)
            if last_request_at > 0:
                wait = interval - (time.monotonic() - last_request_at)
                if wait > 0:
                    print(
                        f"  rate-limit pace: sleeping {wait:.1f}s (RPM≤{quota.rpm} on {quota.model_id})",
                        file=sys.stderr,
                    )
                    time.sleep(wait)
            api_payload, duration = call_gemini(api_key, build_prompt(batch))
            last_request_at = time.monotonic()
            total_duration += duration
            stats["requests"] += 1
            record_model_usage(stats, active_model_quota())
            stats["chars_sent"] += len(batch)
            counts = extract_usage_counts(api_payload)
            stats["prompt_tokens"] += counts.get("prompt", 0)
            stats["candidates_tokens"] += counts.get("candidates", 0)
            stats["total_tokens"] += counts.get("total", 0)
            parsed = parse_model_json(extract_response_text(api_payload))
            for issue in parsed["issues"]:
                if not issue.get("file"):
                    issue["file"] = path
            all_issues.extend(parsed["issues"])
    print(f"Usage: {format_usage_summary(stats)}", file=sys.stderr)
    return all_issues, total_duration, stats


def empty_result(files: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {"has_issue": False, "issues": [], "files": files or []}


def print_result_json(result: dict[str, Any]) -> None:
    print(json.dumps(result, ensure_ascii=False, indent=2))


def fail(message: str, *, summary: str | None = None, result: dict[str, Any] | None = None) -> int:
    print(message, file=sys.stderr)
    if summary:
        append_step_summary(summary)
    print_result_json(result if result is not None else empty_result())
    return 1


def _passed_summary(extra_note: str, files: list[dict[str, Any]] | None = None) -> str:
    return format_step_summary(
        status="PASSED", issues=[], duration_sec=None,
        extra_note=extra_note, files=files or [],
    )


def main(argv: list[str] | None = None) -> int:
    reset_model_failover_state()
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        return fail("Usage: python scripts/gemini_localization_review.py <diff_file>")
    try:
        with open(args[0], encoding="utf-8", errors="replace") as handle:
            diff_text = handle.read()
    except OSError as exc:
        return fail(f"Failed to read diff file: {exc}")
    if not diff_text.strip():
        print("No changes under LOCALIZATION_GATE_PATHSPECS — skip Gemini API", file=sys.stderr)
        append_step_summary(_passed_summary("Out of path scope / empty diff — Gemini API not called"))
        print_result_json(empty_result())
        return 0
    analyzed = analyze_diff(diff_text)
    files = analyzed["files"]
    review_by_file = analyzed.get("review_by_file") or {}
    added_details = analyzed.get("_added_line_details") or {}
    print_files_report(files)
    if not any(text.strip() for text in review_by_file.values()):
        print("No added lines to review under scoped diff — skip Gemini API", file=sys.stderr)
        append_step_summary(_passed_summary("No added lines — Gemini API not called", files))
        print_result_json(empty_result(files))
        return 0
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return fail(
            "GEMINI_API_KEY is missing",
            summary=format_step_summary(
                status="FAILED", issues=[], duration_sec=None,
                extra_note="GEMINI_API_KEY is missing", files=files,
            ),
            result=empty_result(files),
        )
    try:
        raw_issues, duration, usage_stats = review_by_file_sessions(api_key, review_by_file)
        kept = postprocess_issues(raw_issues, added_details)
        result = {"has_issue": bool(kept), "issues": kept, "files": files}
    except (ValueError, RuntimeError, OSError, requests.RequestException) as exc:
        return fail(
            f"Localization gate failed: {exc}",
            summary=format_step_summary(
                status="FAILED", issues=[], duration_sec=None,
                extra_note=f"fail-closed: {exc}", files=files,
            ),
            result=empty_result(files),
        )
    append_step_summary(format_step_summary(
        status="FAILED" if has_blocking_issues(kept) else "PASSED",
        issues=kept, duration_sec=duration,
        usage=format_usage_summary(usage_stats), usage_stats=usage_stats, files=files,
    ))
    print_result_json(result)
    if has_blocking_issues(kept):
        print("Blocking HIGH severity issues found", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
