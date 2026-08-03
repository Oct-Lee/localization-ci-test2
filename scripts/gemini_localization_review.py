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
MAX_REVIEW_CHARS = 100_000  # 0803-proven batch size; pair with ±CONTEXT_LINES overlap for recall
QUOTA_RETRY_DEFAULT_SEC = 60.0
MAX_QUOTA_RETRIES = 40
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


CONTEXT_LINES = 3
PLACEHOLDER_RE = re.compile(r"\{[^}]+\}|%\w|\$\{[^}]+\}")
FENCE_RE = re.compile(r"^\s*```(?:json)?\s*\n?(.*?)\n?\s*```\s*$", re.DOTALL | re.IGNORECASE)
PROP_KEY = r"[A-Za-z_][A-Za-z0-9_]*"
KEY_ONLY_RE = re.compile(rf"^{PROP_KEY}\s*:?\s*,?\s*$")
KEY_ONLY_LINE_RE = re.compile(rf"^\s*({PROP_KEY})\s*:\s*$")
PY_KEY_OPEN_RE = re.compile(rf"^\s*([A-Z][A-Z0-9_]*)\s*=\s*\(\s*$")
PY_TRIPLE_OPEN_RE = re.compile(
    rf"""^\s*({PROP_KEY})\s*=\s*[fFrRbBuU]*(?P<q>\"\"\"|''')(?P<rest>.*)$"""
)
STRING_VALUE_LINE_RE = re.compile(r"""^\s*(['"])(.*)\1\s*,?\s*$""")
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
HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
_STRUCT_TOKENS = frozenset(("{", "}", "},", "[", "],", "];", "};", ")", "),", "("))
_ID_PROBLEM_TOKENS = (
    "identifier", "constant name", "key name", "object key", "property name",
    "variable name", "key typo",
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
# Full task brief + examples. Severity / FP enforcement also run in postprocess + responseSchema.
def build_prompt(review_text: str) -> str:
    return f"""You are a Localization Quality Reviewer for the UnitX monorepo.

Review ONLY user-facing string VALUES in the PR changes below
(English / Simplified Chinese / Portuguese).

Monorepo formats you will see:
- JS/TS object:  auth_login: 'LOG IN'   |  title: 'ComX Config'
- JS/TS multiline (VALID):  loading_license_check:\\n  'long text'
- Python:  ERROR_X = "..."   |  ERROR_X = (\\n    "..."\\n)
- JSON:  "confirm": "Confirm"
- CSV:  key,zh-CN,en-US,pt-PT  — review language cell VALUES, not the key column
When a line is annotated with "user_facing: ...", review that text first.

Rules:
1) Primary focus: quoted string VALUES (user-facing text).
   For value issues, "original" / "suggestion" MUST be ONLY the string value,
   NOT the whole "KEY: 'value'" / 'KEY = "value"' line.
2) Constant / object-key / identifier names (e.g. FLEX_LIGNT_CONTROL_TITLE,
   cencel, dictionries): MAY be reported when misspelled, but severity MUST be
   "low" (never high/medium). These do NOT block merge.
3) MUST IGNORE code syntax / structure problems:
   missing/extra commas, colons, braces, quotes around keys, JSON/JS/TS/Python syntax.
4) Multiline key/value split is VALID. Never report "missing comma" / "incomplete
   statement" just because the value is on the next line after "KEY_NAME:".
   Review the following quoted value instead.
5) Placeholders {{...}}, %s / %d / %w, ${{...}}, and Python {{}} / str.format
   fields MUST remain identical in suggestions. NEVER invent placeholders that
   are absent from original (e.g. do not turn "个物料模拟失败:" into
   "%d个物料模拟失败"). NEVER remove existing placeholders.

Also ignore: imports, export wrappers, URLs, paths, UUIDs, hashes, debug-only
messages, internal comments, vendor/framework glue.

Good examples:
  Input: FILE_CAMERA_NOT_SELECT: 'File Camera not select',
  → original: "File Camera not select"
    suggestion: "File Camera not selected"
    severity: "high"

  Input (multiline — valid):
    COMPUTATIONAL_IMAGING_UNSAVED_SEQUENCE:
      'Please save the changes to the Sequence first',
  → review only: "Please save the changes to the Sequence first"
  → DO NOT flag the key line as missing comma / incomplete syntax

  Input: ERROR_CANNOT_FIND_CAMERA = "Cannot find camera {{}}. Pleace check..."
  → original: "Cannot find camera {{}}. Pleace check..."
    suggestion: "Cannot find camera {{}}. Please check..."
    severity: "high"

  Input: FLEX_LIGNT_CONTROL_TITLE: 'Brightness control',
  → original: "FLEX_LIGNT_CONTROL_TITLE"
    suggestion: "FLEX_LIGHT_CONTROL_TITLE"
    problem: "Identifier spelling: LIGNT → LIGHT"
    severity: "low"

  Input: cencel: 'Cencel',
  → may emit TWO issues:
      value: original "Cencel" → "Cancel" (high)
      key: original "cencel" → "cancel" (low)

  Input (Chinese typo with placeholder):
    TRAINING_QUEUE_MSG: '已经加入训练序列，前面还有%d个神经网路'
  → original: "已经加入训练序列，前面还有%d个神经网路"
    suggestion: "已经加入训练序列，前面还有%d个神经网络"
    problem: "Typo: 神经网路 should be 神经网络"
    severity: "high"
  → Note placeholder %d is preserved unchanged.

Bad examples (DO NOT emit):
  - Flagging COMPUTATIONAL_IMAGING_UNSAVED_SEQUENCE: as "missing comma" because
    the string value is on the next line
  - Marking identifier/key typos as high/medium
  - Putting "KEY: 'value'" into original for a value-only grammar fix

Casing / word-form rules (critical):
- Fix the word itself; do NOT introduce incorrect capitalization.
- Mid-sentence English words stay lowercase unless they are proper nouns or
  the start of a sentence.
- Example: "not Founded" → suggestion MUST be "not found"
  (past participle of "find"). NEVER suggest "Found" or "not Found".
- Example: "configration" → "configuration" (keep surrounding casing unchanged).
- Use English comma "," in English sentences; do not keep Chinese "，" inside
  English text when that is part of the error.

Severity rules (severity values MUST be lowercase):
- HIGH: Spelling, Grammar, Incorrect Word Usage, or Localization errors that
  seriously hurt understanding in user-facing VALUES. ALL spelling / grammar /
  incorrect word usage in VALUES MUST be "high".
- MEDIUM: Wording / Readability / consistency improvements of VALUES
- LOW: Capitalization / optional style of VALUES, AND any constant-name /
  identifier / object-key spelling issues. Capitalization and identifier
  issues MUST be "low".

Blocking rule: only "high" severity blocks merge.

Return JSON ONLY. No markdown fences. No prose outside JSON.
Schema:
{{
  "has_issue": boolean,
  "issues": [
    {{
      "file": string,
      "line": number,
      "original": string,
      "problem": string,
      "suggestion": string,
      "severity": "high" | "medium" | "low"
    }}
  ]
}}
If no issues: {{"has_issue": false, "issues": []}}
If issues is non-empty, has_issue must be true.

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


def _multiline_review_chunk(
    path_label: str, line_no: int, user_facing_values: list[str], *,
    key_name: str | None = None, note: str | None = None, source_line: str | None = None,
) -> str:
    parts = [f"# file: {path_label}", f"# line: {line_no}"]
    if key_name:
        parts.append(f"# key: {key_name}")
    if note:
        parts.append(f"# note: {note}")
    if source_line is not None:
        parts.append(source_line if source_line.startswith("+") else f"+{source_line}")
    parts.extend(f"user_facing: {v}" for v in user_facing_values)
    return "\n".join(parts)


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
    out = dict(issue)
    original, suggestion = out.get("original", "").strip(), out.get("suggestion", "").strip()
    o_m, s_m = ASSIGNMENT_LINE_RE.match(original), ASSIGNMENT_LINE_RE.match(suggestion)
    if o_m and s_m:
        if o_m.group(1) != s_m.group(1):
            out.update(original=o_m.group(1), suggestion=s_m.group(1), _kind="identifier")
            return out
        out.update(original=o_m.group(3), suggestion=s_m.group(3), _kind="value")
        return out
    if o_m and not s_m:
        out.update(original=o_m.group(3), _kind="value")
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


def filter_userfacing_issues(issues: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Drop syntax FPs; force key/identifier findings to low (informational only)."""
    kept, dropped = [], []
    for issue in issues:
        normalized = normalize_issue_to_string_value(issue)
        if is_syntax_false_positive(normalized):
            dropped.append(issue)
            continue
        if is_identifier_issue(normalized):
            normalized["severity"] = SEVERITY_LOW
        normalized.pop("_kind", None)
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
                    chunk = _multiline_review_chunk(
                        path_label, value_line_no, [string_val], key_name=key_name,
                        note="python triple-quoted string",
                        source_line=f"+  {key_name} = {triple.group('q')}...{triple.group('q')}",
                    )
                    dedupe_key = f"{path_label}:{value_line_no}:{key_name}:{string_val}"
                    if dedupe_key not in seen:
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
                opener = f"{key_name}:" if key_only else f"{key_name} = ("
                chunk = _multiline_review_chunk(
                    path_label, value_line_no, [string_val], key_name=key_name,
                    note="multiline KEY + string value (valid formatting)",
                    source_line=f"+  {opener}\n+    {string_val!r}",
                )
                dedupe_key = f"{path_label}:{value_line_no}:{key_name}:{string_val}"
                if dedupe_key not in seen:
                    seen.add(dedupe_key)
                    review_chunks.append(chunk)
                    review_by_file.setdefault(path_label, []).append(chunk)
                continue
            if key_only or py_open:
                continue
            if should_skip_review_line(text):
                continue
            hints = extract_user_facing_hints(text, path_label)
            # Keep ±CONTEXT_LINES neighbors (same as 0803): overlapping windows improve Chinese recall.
            start, end = max(0, idx - CONTEXT_LINES), min(len(lines), idx + CONTEXT_LINES + 1)
            window = [
                lines[j] for j in range(start, end)
                if not lines[j].startswith(("---", "+++", "@@"))
            ]
            if not window and not hints:
                continue
            body = "\n".join(window) if window else f"+{text}"
            if hints:
                body += "\n" + "\n".join(f"user_facing: {h}" for h in hints)
            dedupe_key = f"{path_label}:{line_no}:{body}"
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            chunk = f"# file: {path_label}\n# line: {line_no}\n{body}"
            review_chunks.append(chunk)
            review_by_file.setdefault(path_label, []).append(chunk)
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
    return {
        "review_text": "\n\n".join(review_chunks),
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
        needle = (out.get("original") or "").strip()
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
                if _value_exact_in_line(needle, text):
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
    return FENCE_RE.match(stripped).group(1).strip() if FENCE_RE.match(stripped) else stripped


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
        item: dict[str, Any] = {
            "original": issue["original"].strip(),
            "problem": issue["problem"].strip(),
            "suggestion": issue["suggestion"].strip(),
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
    start = time.monotonic()
    quota_retries = transient_attempts = 0
    while True:
        model_id = active_model_id()
        url = f"{gemini_endpoint(model_id)}?key={api_key}"
        try:
            response = requests.post(url, json=body, timeout=HTTP_TIMEOUT_SEC)
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


def split_into_batches(review_text: str, limit: int | None = None) -> list[str]:
    """Pack whole review chunks (\\n\\n-separated). Only hard-split a chunk if it alone exceeds limit."""
    if limit is None:
        limit = MAX_REVIEW_CHARS
    if not review_text.strip():
        return []
    chunks = [c for c in review_text.split("\n\n") if c.strip()]
    if not chunks:
        return []
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
        if current and current_len + add_len > limit:
            flush()
        current.append(chunk)
        current_len += len(chunk) + (len(sep) if current_len else 0)
    flush()
    return batches


def with_batch_continuation_header(path: str, batch: str, *, batch_index: int) -> str:
    """Re-anchor hard-split batches so mid-file cuts still carry # file context."""
    if batch_index == 0 or batch.lstrip().startswith("# file:"):
        return batch
    return f"# file: {path}\n# note: continuation of previous batch\n\n{batch}"


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


def postprocess_issues(
    issues: list[dict[str, Any]], added_details: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    issues = attach_locations(issues, added_details)
    kept, dropped = filter_userfacing_issues(issues)
    _log_filtered(dropped, "syntax/non-localization false positive(s)")
    kept, ph_dropped = filter_placeholder_mismatches(kept)
    if ph_dropped:
        _log_filtered(
            ph_dropped,
            "issue(s) with placeholder mismatch "
            "(suggestion must not add/remove placeholders like %d / {id})",
            show_samples=True,
        )
    return kept


def review_by_file_sessions(
    api_key: str, review_by_file: dict[str, str],
) -> tuple[list[dict[str, Any]], float, dict[str, Any]]:
    all_issues, total_duration, stats, last_request_at = [], 0.0, empty_usage_stats(), 0.0
    for path, text in review_by_file.items():
        if not text.strip():
            continue
        batches = split_into_batches(text)
        stats["files_reviewed"] += 1
        stats["batches"] += len(batches)
        print(
            f"Review session: {path} — {len(text)} chars, {len(batches)} batch(es)",
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
