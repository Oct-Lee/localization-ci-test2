#!/usr/bin/env python3
"""Gemini Localization Quality Gate — review PR diffs for user-facing text issues.

CLI:
    python scripts/gemini_localization_review.py <diff_file>

Environment:
    GEMINI_API_KEY         required
    GITHUB_STEP_SUMMARY    optional; append Markdown report when set
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

# Ordered failover chain. Quotas differ by model — pacing follows the active one.
# Gemini 3 Flash API id is currently gemini-3-flash-preview.
class GeminiModelQuota(NamedTuple):
    model_id: str
    rpm: int
    rpd: int
    tpm: int = 250_000


GEMINI_MODEL_QUOTAS: tuple[GeminiModelQuota, ...] = (
    GeminiModelQuota("gemini-3.5-flash-lite", rpm=15, rpd=500),
    GeminiModelQuota("gemini-3.1-flash-lite", rpm=15, rpd=500),
    GeminiModelQuota("gemini-3-flash-preview", rpm=5, rpd=20),
    GeminiModelQuota("gemini-3.5-flash", rpm=5, rpd=20),
    GeminiModelQuota("gemini-3.6-flash", rpm=5, rpd=20),
)
GEMINI_MODELS = tuple(q.model_id for q in GEMINI_MODEL_QUOTAS)
GEMINI_API_BASE = (
    "https://generativelanguage.googleapis.com/v1beta/models"
)
MAX_REVIEW_CHARS = 100_000
HTTP_TIMEOUT_SEC = 60
MAX_ATTEMPTS = 3
# RPM/TPM: wait ~1 min (or API "retry in Xs") and retry in the same workflow.
QUOTA_RETRY_DEFAULT_SEC = 60.0
MAX_QUOTA_RETRIES = 40  # up to ~40 minutes of quota waits per request
RETRY_IN_RE = re.compile(r"retry in ([0-9]+(?:\.[0-9]+)?)\s*s", re.IGNORECASE)
DAILY_QUOTA_RE = re.compile(
    r"per\s*day|daily\s*quota|rpd|free_tier_requests|generate_content_free_tier_requests",
    re.IGNORECASE,
)

# Sticky within one process: after failover, keep using the fallback model.
_active_model_index = 0


def reset_model_failover_state() -> None:
    global _active_model_index
    _active_model_index = 0


def active_model_quota() -> GeminiModelQuota:
    return GEMINI_MODEL_QUOTAS[_active_model_index]


def active_model_id() -> str:
    return active_model_quota().model_id


def min_request_interval_sec(rpm: int | None = None) -> float:
    """Leave slight headroom vs hard RPM (60/rpm + 0.1s)."""
    limit = active_model_quota().rpm if rpm is None else rpm
    return 60.0 / limit + 0.1


def try_advance_model(reason: str) -> bool:
    """Switch to the next Gemini model; return False if none left."""
    global _active_model_index
    if _active_model_index + 1 >= len(GEMINI_MODEL_QUOTAS):
        return False
    prev = GEMINI_MODEL_QUOTAS[_active_model_index]
    _active_model_index += 1
    nxt = GEMINI_MODEL_QUOTAS[_active_model_index]
    print(
        f"Gemini model failover: {prev.model_id} -> {nxt.model_id} "
        f"(RPM={nxt.rpm}/RPD={nxt.rpd}; {reason})",
        file=sys.stderr,
    )
    return True


CONTEXT_LINES = 3
PLACEHOLDER_RE = re.compile(r"\{[^}]+\}|%\w|\$\{[^}]+\}")
FENCE_RE = re.compile(
    r"^\s*```(?:json)?\s*\n?(.*?)\n?\s*```\s*$",
    re.DOTALL | re.IGNORECASE,
)
# Monorepo key styles: SCREAMING_SNAKE, snake_case, camelCase.
PROP_KEY = r"[A-Za-z_][A-Za-z0-9_]*"
# SCREAMING_SNAKE / constant-style identifiers (for LOW severity key typos).
IDENTIFIER_RE = re.compile(r"\b[A-Z][A-Z0-9_]{2,}\b")
KEY_ONLY_RE = re.compile(rf"^{PROP_KEY}\s*:?\s*,?\s*$")
KEY_ONLY_LINE_RE = re.compile(rf"^\s*({PROP_KEY})\s*:\s*$")
PY_KEY_OPEN_RE = re.compile(rf"^\s*([A-Z][A-Z0-9_]*)\s*=\s*\(\s*$")
PY_PAREN_CLOSE_RE = re.compile(r"^\s*\)\s*,?\s*$")
STRING_VALUE_LINE_RE = re.compile(r"""^\s*(['"])(.*)\1\s*,?\s*$""")
ASSIGNMENT_LINE_RE = re.compile(
    rf"""^\s*({PROP_KEY})\s*[:=]\s*(['"])(.*)\2\s*,?\s*$""",
    re.DOTALL,
)
JSON_KV_RE = re.compile(
    r"""^\s*"((?:\\.|[^"\\])*)"\s*:\s*"((?:\\.|[^"\\])*)"\s*,?\s*$"""
)
# Skip structural / import noise lines — not user-facing content.
SKIP_LINE_RE = re.compile(
    r"""(?x)
    ^\s*(?:
        import\b|from\b|export\s+default\b|export\s+const\b|
        const\s+\w+\s*=\s*\{|
        /\*|^\s*\*|^\s*//|
        \}|\{|,|
        \#
    )
    """
)
NON_USERFACING_PROBLEM_RE = re.compile(
    r"missing comma|extra comma|syntax|object key|property name|variable name|"
    r"constant name|identifier|key name|missing colon|json structure|"
    r"javascript syntax|python syntax|typescript syntax",
    re.IGNORECASE,
)

SEVERITY_HIGH = "high"
SEVERITY_MEDIUM = "medium"
SEVERITY_LOW = "low"
VALID_SEVERITIES = {SEVERITY_HIGH, SEVERITY_MEDIUM, SEVERITY_LOW}
HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


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
    if not stripped:
        return True
    if SKIP_LINE_RE.match(stripped):
        return True
    if stripped in {
        "{",
        "}",
        "},",
        "[",
        "],",
        "];",
        "};",
        ")",
        "),",
        "(",
    }:
        return True
    return False


def extract_user_facing_hints(text: str, path: str = "") -> list[str]:
    """Extract candidate user-facing strings from a single added line."""
    stripped = text.strip()
    if not stripped or should_skip_review_line(stripped):
        return []

    json_m = JSON_KV_RE.match(stripped)
    if json_m:
        return [json_m.group(2)]

    assign_m = ASSIGNMENT_LINE_RE.match(stripped)
    if assign_m:
        return [assign_m.group(3)]

    str_m = STRING_VALUE_LINE_RE.match(stripped)
    if str_m:
        return [str_m.group(2)]

    lower_path = path.lower()
    if lower_path.endswith(".csv") or stripped.count(",") >= 2:
        if stripped.lower().startswith("key,"):
            return []
        parts = [p.strip() for p in stripped.split(",")]
        if len(parts) >= 2 and parts[0]:
            return [p for p in parts[1:] if p]

    return []



def truncate_review_text(review_text: str, limit: int = MAX_REVIEW_CHARS) -> tuple[str, bool]:
    """Take the first <=limit slice, preferring a ``\\n\\n`` cut near the end."""
    if len(review_text) <= limit:
        return review_text, False
    truncated = review_text[:limit]
    cut = truncated.rfind("\n\n")
    if cut > limit // 2:
        truncated = truncated[:cut]
    return truncated, True


def split_oversized_chunk(text: str, limit: int) -> list[str]:
    """Hard-split text into pieces each <= limit without dropping content.

    Prefers ``\\n\\n`` then ``\\n`` near the end of each window; otherwise cuts
    at ``limit``. Every character of ``text`` appears in exactly one piece
    (aside from skipped separator newlines between pieces).
    """
    if not text:
        return []
    if len(text) <= limit:
        return [text]

    pieces: list[str] = []
    start = 0
    n = len(text)
    while start < n:
        remaining = n - start
        if remaining <= limit:
            pieces.append(text[start:])
            break
        window = text[start : start + limit]
        cut_rel = window.rfind("\n\n")
        if cut_rel <= limit // 2:
            cut_rel = window.rfind("\n")
        if cut_rel <= limit // 2:
            cut_rel = limit
        end = start + cut_rel
        if end <= start:
            end = start + limit
        pieces.append(text[start:end])
        start = end
        while start < n and text[start] == "\n":
            start += 1
    return pieces


def normalize_issue_to_string_value(issue: dict[str, Any]) -> dict[str, Any]:
    """Normalize KEY: 'value' lines; mark identifier renames for LOW severity."""
    out = dict(issue)
    original = out.get("original", "").strip()
    suggestion = out.get("suggestion", "").strip()
    o_m = ASSIGNMENT_LINE_RE.match(original)
    s_m = ASSIGNMENT_LINE_RE.match(suggestion)

    if o_m and s_m:
        if o_m.group(1) != s_m.group(1):
            # Constant/key rename — keep as identifier issue (forced LOW later).
            out["original"] = o_m.group(1)
            out["suggestion"] = s_m.group(1)
            out["_kind"] = "identifier"
            return out
        out["original"] = o_m.group(3)
        out["suggestion"] = s_m.group(3)
        out["_kind"] = "value"
        return out

    if o_m and not s_m:
        out["original"] = o_m.group(3)
        out["_kind"] = "value"
        return out

    return out


def looks_like_code_key(text: str) -> bool:
    """Heuristic: i18n/object keys vs Title-Case user-facing words."""
    s = text.strip().rstrip(",").rstrip(":")
    if not s or not re.match(rf"^{PROP_KEY}$", s):
        return False
    if "_" in s:
        return True  # snake_case / SCREAMING_SNAKE
    if s.isupper() and len(s) >= 3:
        return True  # ACRONYM constants
    if re.match(r"^[a-z]+[A-Z]", s):
        return True  # camelCase
    return False


def is_identifier_issue(issue: dict[str, Any]) -> bool:
    """True when the finding targets a constant/key/identifier name."""
    if issue.get("_kind") == "identifier":
        return True

    original = issue.get("original", "").strip()
    suggestion = issue.get("suggestion", "").strip()
    problem = issue.get("problem", "").lower()

    if any(
        token in problem
        for token in (
            "identifier",
            "constant name",
            "key name",
            "object key",
            "property name",
            "variable name",
        )
    ):
        # Exclude pure syntax complaints handled elsewhere.
        if "comma" in problem or "syntax" in problem or "colon" in problem:
            return False
        return True

    if looks_like_code_key(original) and looks_like_code_key(suggestion):
        o_key = original.rstrip().rstrip(",").rstrip(":")
        s_key = suggestion.rstrip().rstrip(",").rstrip(":")
        if o_key != s_key:
            return True

    orig_ids = set(IDENTIFIER_RE.findall(original))
    sugg_ids = set(IDENTIFIER_RE.findall(suggestion))
    if orig_ids != sugg_ids:
        if re.search(rf"{PROP_KEY}\s*:", original) or re.search(
            rf"{PROP_KEY}\s*:", suggestion
        ):
            return True
        if (
            not re.search(r"['\"]", original)
            and looks_like_code_key(original)
            and looks_like_code_key(suggestion)
        ):
            return True

    return False


def is_syntax_false_positive(issue: dict[str, Any]) -> bool:
    """Drop code-structure complaints that are not localization quality."""
    original = issue.get("original", "").strip()
    problem = issue.get("problem", "")

    if NON_USERFACING_PROBLEM_RE.search(problem):
        # Identifier spelling mentioned with syntax words → still syntax FP if
        # about commas/structure; identifier-only handled separately.
        if re.search(r"comma|syntax|colon|brace|quote", problem, re.IGNORECASE):
            return True

    # Key-only original with no real rename suggestion (e.g. add comma).
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
        s_m = re.match(rf"^({PROP_KEY})\s*:?\s*,?\s*$", suggestion)
        # Trailing-colon key with no rename → multiline/format FP, not a finding.
        if not s_m or s_m.group(1) == o_key:
            return True

    return False


def filter_userfacing_issues(
    issues: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Drop syntax FPs; keep value issues; keep identifier issues as LOW."""
    kept: list[dict[str, Any]] = []
    dropped: list[dict[str, Any]] = []
    for issue in issues:
        normalized = normalize_issue_to_string_value(issue)

        if is_syntax_false_positive(normalized):
            dropped.append(issue)
            continue

        if is_identifier_issue(normalized):
            normalized["severity"] = SEVERITY_LOW
            if not normalized.get("problem"):
                normalized["problem"] = "Identifier / constant-name spelling"
            elif "identifier" not in normalized["problem"].lower():
                normalized["problem"] = (
                    f"Identifier / constant-name: {normalized['problem']}"
                )

        normalized.pop("_invalid", None)
        normalized.pop("_kind", None)
        kept.append(normalized)
    return kept, dropped

def _new_file_entry(path: str) -> dict[str, Any]:
    return {
        "path": path,
        "added": 0,
        "deleted": 0,
        "added_lines": [],  # list[{"line": int, "text": str}]
    }


def _peek_multiline_string_value(
    lines: list[str],
    start_idx: int,
    *,
    join_python_concat: bool = False,
    max_look_ahead: int = 40,
) -> tuple[list[int], str] | None:
    """Collect quoted value line(s) after a multiline KEY opener.

    For JS/TS ``KEY:`` — first quoted line only.
    For Python ``KEY = (`` — join adjacent implicit-concat string literals
    until ``)``, so the full sentence is reviewed as one value.
    Returns (diff_line_indices, joined_inner_text) or None.
    """
    indices: list[int] = []
    parts: list[str] = []
    end = min(len(lines), start_idx + 1 + max_look_ahead)
    for j in range(start_idx + 1, end):
        candidate = lines[j]
        if candidate.startswith("---") or candidate.startswith("+++"):
            break
        if candidate.startswith("@@"):
            break
        if candidate.startswith("-"):
            continue
        if candidate.startswith(" "):
            # Unchanged context between key and value — still allow.
            continue
        if not candidate.startswith("+"):
            break
        value_text = candidate[1:]
        if PY_PAREN_CLOSE_RE.match(value_text):
            break
        string_m = STRING_VALUE_LINE_RE.match(value_text)
        if string_m:
            indices.append(j)
            parts.append(string_m.group(2))
            if not join_python_concat:
                break
            continue
        # Non-string content after KEY opener.
        break
    if not parts:
        return None
    return indices, "".join(parts)


def analyze_diff(diff_text: str) -> dict[str, Any]:
    """Parse unified diff into review text + per-file add/delete line stats."""
    if not diff_text or not diff_text.strip():
        return {"review_text": "", "files": []}

    lines = diff_text.splitlines()
    files_order: list[str] = []
    files_map: dict[str, dict[str, Any]] = {}
    current_file = ""
    new_line_no: int | None = None
    review_chunks: list[str] = []
    review_by_file: "OrderedDict[str, list[str]]" = OrderedDict()
    seen: set[str] = set()
    skip_indices: set[int] = set()

    def ensure_file(path: str) -> dict[str, Any]:
        if path not in files_map:
            files_map[path] = _new_file_entry(path)
            files_order.append(path)
        return files_map[path]

    def set_current_file(path: str) -> None:
        nonlocal current_file, new_line_no
        current_file = path
        ensure_file(path)
        new_line_no = None

    for idx, line in enumerate(lines):
        if line.startswith("+++ b/"):
            set_current_file(line[6:])
            continue
        if line.startswith("+++ "):
            rest = line[4:]
            if rest.startswith("b/"):
                set_current_file(rest[2:])
            else:
                new_line_no = None
            continue

        hunk = HUNK_RE.match(line)
        if hunk:
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

            # JS/TS multiline KEY: + value, or Python KEY = ( + "a" "b" ... )
            key_only = KEY_ONLY_LINE_RE.match(text)
            py_open = PY_KEY_OPEN_RE.match(text)
            merged_value = None
            if key_only or py_open:
                merged_value = _peek_multiline_string_value(
                    lines,
                    idx,
                    join_python_concat=bool(py_open),
                )

            if (key_only or py_open) and merged_value:
                value_indices, string_val = merged_value
                for value_idx in value_indices:
                    skip_indices.add(value_idx)
                value_line_no = line_no + 1 if line_no >= 0 else -1
                key_name = (key_only or py_open).group(1)
                opener = f"{key_name}:" if key_only else f"{key_name} = ("
                note = (
                    "multiline Python KEY = ( implicit string concat "
                    "(valid formatting)"
                    if py_open
                    else "multiline KEY + string value (valid formatting)"
                )
                chunk = (
                    f"# file: {path_label}\n"
                    f"# line: {value_line_no}\n"
                    f"# key: {key_name}\n"
                    f"# note: {note}\n"
                    f"+  {opener}\n"
                    f'+    "{string_val}"\n'
                    f"user_facing: {string_val}"
                )
                dedupe_key = f"{path_label}:{value_line_no}:{key_name}:{string_val}"
                if dedupe_key not in seen:
                    seen.add(dedupe_key)
                    review_chunks.append(chunk)
                    review_by_file.setdefault(path_label, []).append(chunk)
                continue

            # Bare key / KEY = ( without visible value yet — wait for value line(s).
            if key_only or py_open:
                continue

            if should_skip_review_line(text):
                continue

            hints = extract_user_facing_hints(text, path_label)
            if hints:
                # Compact entry: only annotate values. Neighboring ±CONTEXT lines
                # inflate payload and can hide typos (e.g. 神经网路 next to 神经网络).
                key_name = None
                stripped = text.strip()
                assign_m = ASSIGNMENT_LINE_RE.match(stripped)
                if assign_m:
                    key_name = assign_m.group(1)
                else:
                    json_m = JSON_KV_RE.match(stripped)
                    if json_m:
                        key_name = json_m.group(1)
                header_parts = [
                    f"# file: {path_label}",
                    f"# line: {line_no}",
                ]
                if key_name:
                    header_parts.append(f"# key: {key_name}")
                body = "\n".join(
                    header_parts + [f"user_facing: {h}" for h in hints]
                )
                dedupe_key = f"{path_label}:{line_no}:{body}"
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)
                review_chunks.append(body)
                review_by_file.setdefault(path_label, []).append(body)
                continue

            # No extractable value — keep a small context window for rare cases.
            start = max(0, idx - CONTEXT_LINES)
            end = min(len(lines), idx + CONTEXT_LINES + 1)
            window: list[str] = []
            for j in range(start, end):
                candidate = lines[j]
                if candidate.startswith("---") or candidate.startswith("+++"):
                    continue
                if candidate.startswith("@@"):
                    continue
                window.append(candidate)
            if not window:
                continue
            body = "\n".join(window)
            dedupe_key = f"{path_label}:{line_no}:{body}"
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            header = f"# file: {path_label}\n# line: {line_no}"
            chunk = f"{header}\n{body}"
            review_chunks.append(chunk)
            review_by_file.setdefault(path_label, []).append(chunk)
            continue

        if line.startswith("-") and not line.startswith("---"):
            entry = ensure_file(current_file or "(unknown)")
            entry["deleted"] += 1
            continue

        if line.startswith(" ") and new_line_no is not None:
            new_line_no += 1

    files_out: list[dict[str, Any]] = []
    for path in files_order:
        entry = files_map[path]
        files_out.append(
            {
                "path": entry["path"],
                "added": entry["added"],
                "deleted": entry["deleted"],
            }
        )

    review_by_file_text = OrderedDict(
        (path, "\n\n".join(chunks))
        for path, chunks in review_by_file.items()
        if chunks
    )
    return {
        "review_text": "\n\n".join(review_chunks),
        "review_by_file": review_by_file_text,
        "files": files_out,
        "_added_line_details": {
            path: files_map[path]["added_lines"] for path in files_order
        },
    }


def parse_diff(diff_text: str) -> str:
    """Extract added lines with ±CONTEXT_LINES context for Gemini review."""
    return analyze_diff(diff_text)["review_text"]


def print_files_report(files: list[dict[str, Any]]) -> None:
    if not files:
        print("Diff scope: (no files)", file=sys.stderr)
        return
    print("Diff scope:", file=sys.stderr)
    for item in files:
        print(
            f"  {item['path']}  +{item['added']} -{item['deleted']}",
            file=sys.stderr,
        )


def attach_locations(
    issues: list[dict[str, Any]],
    added_details: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    """Fill missing file/line by matching original text against added lines."""
    enriched: list[dict[str, Any]] = []
    for issue in issues:
        out = dict(issue)
        if out.get("file") and out.get("line") not in (None, -1):
            enriched.append(out)
            continue
        needle = out.get("original", "")
        matched = False
        for path, rows in added_details.items():
            for row in rows:
                if needle and needle in row["text"]:
                    out.setdefault("file", path)
                    if out.get("line") in (None, -1):
                        out["line"] = row["line"]
                    matched = True
                    break
            if matched:
                break
        enriched.append(out)
    return enriched


def strip_markdown_fence(text: str) -> str:
    stripped = text.strip()
    match = FENCE_RE.match(stripped)
    if match:
        return match.group(1).strip()
    return stripped


def extract_response_text(api_payload: dict[str, Any]) -> str:
    try:
        return api_payload["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError(f"Unexpected Gemini response shape: {exc}") from exc


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

    validated_issues: list[dict[str, Any]] = []
    for i, issue in enumerate(issues):
        if not isinstance(issue, dict):
            raise ValueError(f"issues[{i}] must be an object")
        for field in ("original", "problem", "suggestion", "severity"):
            if field not in issue:
                raise ValueError(f"issues[{i}] missing field: {field}")
            if not isinstance(issue[field], str) or not issue[field].strip():
                raise ValueError(f"issues[{i}].{field} must be a non-empty string")
        severity = issue["severity"].strip().lower()
        if severity not in VALID_SEVERITIES:
            raise ValueError(
                f"issues[{i}].severity must be one of {sorted(VALID_SEVERITIES)}"
            )
        item: dict[str, Any] = {
            "original": issue["original"].strip(),
            "problem": issue["problem"].strip(),
            "suggestion": issue["suggestion"].strip(),
            "severity": severity,
        }
        if isinstance(issue.get("file"), str) and issue["file"].strip():
            item["file"] = issue["file"].strip()
        if "line" in issue and issue["line"] is not None:
            try:
                item["line"] = int(issue["line"])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"issues[{i}].line must be an integer") from exc
        validated_issues.append(item)

    return {"has_issue": bool(validated_issues), "issues": validated_issues}


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
    """Drop issues whose suggestion invents placeholders absent from original.

    Removing or reforming existing placeholders still keeps the issue so
    real spelling/grammar fixes (e.g. 神经网路 → 神经网络 with %d kept or
    accidentally dropped) are not silenced. Inventing new tokens like '%d'
    when original had none remains filtered.
    """
    kept: list[dict[str, Any]] = []
    dropped: list[dict[str, Any]] = []
    for issue in issues:
        original_ph = placeholders(issue["original"])
        suggestion_ph = placeholders(issue["suggestion"])
        invented = suggestion_ph - original_ph
        if invented:
            dropped.append(issue)
            continue
        kept.append(issue)
    return kept, dropped


def count_by_severity(issues: list[dict[str, str]]) -> dict[str, int]:
    counts = {SEVERITY_HIGH: 0, SEVERITY_MEDIUM: 0, SEVERITY_LOW: 0}
    for issue in issues:
        counts[issue["severity"]] = counts.get(issue["severity"], 0) + 1
    return counts


def has_blocking_issues(issues: list[dict[str, str]]) -> bool:
    return any(issue["severity"] == SEVERITY_HIGH for issue in issues)


def format_step_summary(
    *,
    status: str,
    issues: list[dict[str, Any]],
    duration_sec: float | None,
    truncated: bool,
    usage: str = "N/A",
    extra_note: str = "",
    files: list[dict[str, Any]] | None = None,
    usage_stats: dict[str, Any] | None = None,
) -> str:
    counts = count_by_severity(issues)
    duration = f"{duration_sec:.1f}s" if duration_sec is not None else "N/A"
    omitted = (usage_stats or {}).get("chars_omitted", 0)
    lines = [
        "## Localization Quality Gate",
        "",
        f"- Status: {status}",
        f"- High: {counts[SEVERITY_HIGH]} | Medium: {counts[SEVERITY_MEDIUM]} "
        f"| Low: {counts[SEVERITY_LOW]}",
        f"- Duration: {duration}",
        f"- Truncated: {'yes' if truncated else 'no'}"
        + (f" (omitted {omitted} chars)" if omitted else ""),
        f"- Token usage: {usage}",
    ]
    if usage_stats:
        models = usage_stats.get("models_used") or []
        models_s = ", ".join(models) if models else active_model_id()
        lines.extend(
            [
                f"- Models: {models_s}",
                f"- API requests: {usage_stats['requests']} "
                f"(paced ≥{usage_stats['min_interval_sec']:.1f}s; "
                f"limits {format_model_limits(usage_stats, sep='; ', with_tpm=True)})",
                f"- Tokens: prompt={usage_stats['prompt_tokens']} "
                f"candidates={usage_stats['candidates_tokens']} "
                f"total={usage_stats['total_tokens']}",
                f"- Review payload: sent={usage_stats['chars_sent']} chars, "
                f"omitted={usage_stats['chars_omitted']} chars, "
                f"batches={usage_stats['batches']}, "
                f"files={usage_stats['files_reviewed']}",
            ]
        )
    if extra_note:
        lines.append(f"- Note: {extra_note}")

    lines.extend(["", "### Changed files", ""])
    if not files:
        lines.append("_No files in scope._")
    else:
        lines.append("| File | Added | Deleted |")
        lines.append("| --- | ---: | ---: |")
        for item in files:
            lines.append(
                f"| {_md_cell(item['path'])} | {item['added']} | {item['deleted']} |"
            )

    lines.extend(["", "### Issues", ""])
    if not issues:
        lines.append("_No issues reported._")
    else:
        lines.append("| Severity | File | Line | Original | Problem | Suggestion |")
        lines.append("| --- | --- | ---: | --- | --- | --- |")
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


def _md_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def append_step_summary(markdown: str) -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(markdown)
        if not markdown.endswith("\n"):
            handle.write("\n")


def parse_retry_after_seconds(response: requests.Response) -> float:
    """Prefer API 'retry in Xs', then Retry-After header, else 60s."""
    header = response.headers.get("Retry-After") or response.headers.get("retry-after")
    if header:
        try:
            return max(float(header), QUOTA_RETRY_DEFAULT_SEC)
        except ValueError:
            pass
    match = RETRY_IN_RE.search(response.text or "")
    if match:
        try:
            return max(float(match.group(1)), 1.0)
        except ValueError:
            pass
    return QUOTA_RETRY_DEFAULT_SEC


def _transient_backoff(attempt: int) -> None:
    time.sleep(2 ** (attempt - 1))


def call_gemini(api_key: str, prompt: str) -> tuple[dict[str, Any], float]:
    """Call Gemini; RPM/TPM 429 wait+retry; RPD fail over to next model."""
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    start = time.monotonic()
    quota_retries = 0
    transient_attempts = 0

    while True:
        model_id = active_model_id()
        url = f"{GEMINI_API_BASE}/{model_id}:generateContent?key={api_key}"
        try:
            response = requests.post(url, json=body, timeout=HTTP_TIMEOUT_SEC)
        except requests.Timeout as exc:
            transient_attempts += 1
            if transient_attempts >= MAX_ATTEMPTS:
                raise RuntimeError(
                    f"Gemini API timeout after {MAX_ATTEMPTS} attempts"
                ) from exc
            _transient_backoff(transient_attempts)
            continue
        except requests.RequestException as exc:
            raise RuntimeError(f"Gemini API request failed: {exc}") from exc

        if response.status_code == 200:
            duration = time.monotonic() - start
            try:
                return response.json(), duration
            except ValueError as exc:
                raise RuntimeError(
                    f"Gemini returned non-JSON body: {response.text[:500]}"
                ) from exc

        if response.status_code == 429:
            text = response.text or ""
            if DAILY_QUOTA_RE.search(text):
                if try_advance_model(
                    f"RPD/daily quota exhausted on {model_id}"
                ):
                    quota_retries = 0
                    transient_attempts = 0
                    continue
                raise RuntimeError(
                    "Gemini RPD/daily quota exhausted on all models "
                    f"({', '.join(GEMINI_MODELS)}) — retry tomorrow or "
                    "upgrade Usage Tier. "
                    f"Body: {text[:800]}"
                )
            wait = parse_retry_after_seconds(response)
            quota_retries += 1
            if quota_retries > MAX_QUOTA_RETRIES:
                if try_advance_model(
                    f"RPM/TPM still exhausted after {MAX_QUOTA_RETRIES} waits "
                    f"on {model_id}"
                ):
                    quota_retries = 0
                    transient_attempts = 0
                    continue
                raise RuntimeError(
                    f"Gemini RPM/TPM still exhausted after {MAX_QUOTA_RETRIES} "
                    f"waits on all models. Body: {text[:800]}"
                )
            print(
                f"HTTP 429 (RPM/TPM on {model_id}). Waiting {wait:.1f}s then "
                f"auto-retry ({quota_retries}/{MAX_QUOTA_RETRIES}) "
                f"— no need to reopen PR",
                file=sys.stderr,
            )
            time.sleep(wait)
            continue

        if response.status_code in (500, 503):
            transient_attempts += 1
            if transient_attempts >= MAX_ATTEMPTS:
                raise RuntimeError(
                    f"Gemini API failed with HTTP {response.status_code}: "
                    f"{response.text[:1000]}"
                )
            _transient_backoff(transient_attempts)
            continue

        raise RuntimeError(
            f"Gemini API failed with HTTP {response.status_code}: "
            f"{response.text[:1000]}"
        )


def extract_usage_counts(api_payload: dict[str, Any]) -> dict[str, int]:
    meta = api_payload.get("usageMetadata") or api_payload.get("usage_metadata")
    if not isinstance(meta, dict):
        return {}
    mapping = {
        "promptTokenCount": "prompt",
        "prompt_token_count": "prompt",
        "candidatesTokenCount": "candidates",
        "candidates_token_count": "candidates",
        "totalTokenCount": "total",
        "total_token_count": "total",
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
        "requests": 0,
        "prompt_tokens": 0,
        "candidates_tokens": 0,
        "total_tokens": 0,
        "batches": 0,
        "chars_sent": 0,
        "chars_omitted": 0,
        "files_reviewed": 0,
        "models_used": [],
        "model_limits": {},
        "min_interval_sec": min_request_interval_sec(primary.rpm),
    }


def record_model_usage(stats: dict[str, Any], quota: GeminiModelQuota) -> None:
    mid = quota.model_id
    if mid not in stats["models_used"]:
        stats["models_used"].append(mid)
    interval = min_request_interval_sec(quota.rpm)
    stats["model_limits"][mid] = {
        "rpm": quota.rpm,
        "rpd": quota.rpd,
        "tpm": quota.tpm,
        "min_interval_sec": interval,
    }
    stats["min_interval_sec"] = interval


def format_model_limits(
    stats: dict[str, Any],
    *,
    sep: str = ";",
    with_tpm: bool = False,
) -> str:
    model_limits = stats.get("model_limits") or {}
    if model_limits:
        parts: list[str] = []
        for mid, lim in model_limits.items():
            piece = f"{mid}:RPM={lim['rpm']}/RPD={lim['rpd']}"
            if with_tpm and lim.get("tpm") is not None:
                piece += f"/TPM={lim['tpm']}"
            parts.append(piece)
        return sep.join(parts)
    q = active_model_quota()
    base = f"RPM={q.rpm}/RPD={q.rpd}"
    if with_tpm:
        base += f"/TPM={q.tpm}"
    return base


def format_usage_summary(stats: dict[str, Any]) -> str:
    models = stats.get("models_used") or []
    models_s = ",".join(models) if models else active_model_id()
    return (
        f"requests={stats['requests']} "
        f"(limits {format_model_limits(stats)}), "
        f"models={models_s}, "
        f"prompt_tokens={stats['prompt_tokens']}, "
        f"candidates_tokens={stats['candidates_tokens']}, "
        f"total_tokens={stats['total_tokens']}, "
        f"chars_sent={stats['chars_sent']}, "
        f"chars_omitted={stats['chars_omitted']}, "
        f"batches={stats['batches']}, "
        f"files={stats['files_reviewed']}, "
        f"pace>={stats['min_interval_sec']:.1f}s/req"
    )



def split_into_batches(
    review_text: str, limit: int = MAX_REVIEW_CHARS
) -> list[str]:
    """Split one file's review text into API-sized batches on chunk boundaries.

    Oversized single chunks are hard-split so **all** content is reviewed
    (nothing is omitted).
    """
    if not review_text.strip():
        return []
    hard_limit = min(limit, MAX_REVIEW_CHARS)
    if len(review_text) <= hard_limit:
        return [review_text]

    parts = review_text.split("\n\n")
    batches: list[str] = []
    current: list[str] = []
    current_len = 0
    for part in parts:
        part_len = len(part)
        if part_len > hard_limit:
            if current:
                batches.append("\n\n".join(current))
                current, current_len = [], 0
            batches.extend(split_oversized_chunk(part, hard_limit))
            continue
        sep = 2 if current else 0
        if current and current_len + sep + part_len > hard_limit:
            batches.append("\n\n".join(current))
            current = [part]
            current_len = part_len
        else:
            current.append(part)
            current_len += sep + part_len
    if current:
        batches.append("\n\n".join(current))
    return batches


def _log_filter(
    label: str,
    dropped: list[dict[str, Any]],
    *,
    examples: bool = False,
) -> None:
    if not dropped:
        return
    print(f"Filtered {len(dropped)} {label}", file=sys.stderr)
    if examples:
        for bad in dropped[:5]:
            print(
                f"  drop: original={bad.get('original')!r} "
                f"suggestion={bad.get('suggestion')!r}",
                file=sys.stderr,
            )


def postprocess_issues(
    issues: list[dict[str, Any]],
    added_details: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    """Attach locations, drop syntax FPs / bad placeholders, force identifier LOW."""
    kept, dropped = filter_userfacing_issues(
        attach_locations(issues, added_details)
    )
    _log_filter("syntax/non-localization false positive(s)", dropped)
    kept, ph_dropped = filter_placeholder_mismatches(kept)
    _log_filter(
        "issue(s) that invent placeholders "
        "(suggestion must not add placeholders absent from original)",
        ph_dropped,
        examples=True,
    )
    id_low = sum(
        1
        for issue in kept
        if issue["severity"] == SEVERITY_LOW
        and "identifier" in issue.get("problem", "").lower()
    )
    if id_low:
        print(
            f"Downgraded {id_low} constant-name / identifier issue(s) to low",
            file=sys.stderr,
        )
    return kept


def review_by_file_sessions(
    api_key: str,
    review_by_file: dict[str, str],
) -> tuple[list[dict[str, Any]], float, bool, dict[str, Any]]:
    """One Gemini session per file (and per batch if a file is still too large).

    Requests are paced to the active model's RPM. Issues from all successful
    batches are merged. Oversized content is hard-split into further batches
    so nothing is dropped from review.
    """
    all_issues: list[dict[str, Any]] = []
    total_duration = 0.0
    stats = empty_usage_stats()
    last_request_at = 0.0

    for path, text in review_by_file.items():
        if not text.strip():
            continue
        batches = split_into_batches(text)
        # Guarantee every piece is within the API char budget without omission.
        expanded: list[str] = []
        for batch in batches:
            if len(batch) > MAX_REVIEW_CHARS:
                expanded.extend(split_oversized_chunk(batch, MAX_REVIEW_CHARS))
            else:
                expanded.append(batch)
        batches = expanded
        stats["files_reviewed"] += 1
        stats["batches"] += len(batches)
        print(
            f"Review session: {path} — {len(text)} chars, "
            f"{len(batches)} batch(es)",
            file=sys.stderr,
        )
        for i, piece in enumerate(batches, 1):
            if len(batches) > 1:
                print(
                    f"  batch {i}/{len(batches)}: {len(piece)} chars",
                    file=sys.stderr,
                )

            # Pace to respect the active model's RPM (also spaces TPM bursts).
            quota = active_model_quota()
            interval = min_request_interval_sec(quota.rpm)
            if last_request_at > 0:
                wait = interval - (time.monotonic() - last_request_at)
                if wait > 0:
                    print(
                        f"  rate-limit pace: sleeping {wait:.1f}s "
                        f"(RPM≤{quota.rpm} on {quota.model_id})",
                        file=sys.stderr,
                    )
                    time.sleep(wait)

            prompt = build_prompt(piece)
            api_payload, duration = call_gemini(api_key, prompt)
            last_request_at = time.monotonic()
            total_duration += duration
            stats["requests"] += 1
            record_model_usage(stats, active_model_quota())
            stats["chars_sent"] += len(piece)
            counts = extract_usage_counts(api_payload)
            stats["prompt_tokens"] += counts.get("prompt", 0)
            stats["candidates_tokens"] += counts.get("candidates", 0)
            stats["total_tokens"] += counts.get("total", 0)

            raw_text = extract_response_text(api_payload)
            parsed = parse_model_json(raw_text)
            for issue in parsed["issues"]:
                if not issue.get("file"):
                    issue["file"] = path
            all_issues.extend(parsed["issues"])

    print(f"Usage: {format_usage_summary(stats)}", file=sys.stderr)
    # truncated always False: oversized text is split, never dropped.
    return all_issues, total_duration, False, stats


def empty_result(files: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {"has_issue": False, "issues": [], "files": files or []}


def print_result_json(result: dict[str, Any]) -> None:
    """Stdout contract: validated JSON matching the gate schema (+ files)."""
    print(json.dumps(result, ensure_ascii=False, indent=2))


def pass_without_api(
    *,
    files: list[dict[str, Any]],
    note: str,
    stderr_message: str,
) -> int:
    print(stderr_message, file=sys.stderr)
    append_step_summary(
        format_step_summary(
            status="PASSED",
            issues=[],
            duration_sec=None,
            truncated=False,
            extra_note=note,
            files=files,
        )
    )
    print_result_json(empty_result(files))
    return 0


def fail(
    message: str,
    *,
    summary: str | None = None,
    result: dict[str, Any] | None = None,
) -> int:
    print(message, file=sys.stderr)
    if summary:
        append_step_summary(summary)
    print_result_json(result if result is not None else empty_result())
    return 1


def main(argv: list[str] | None = None) -> int:
    reset_model_failover_state()
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        return fail("Usage: python scripts/gemini_localization_review.py <diff_file>")

    diff_path = args[0]
    try:
        with open(diff_path, encoding="utf-8", errors="replace") as handle:
            diff_text = handle.read()
    except OSError as exc:
        return fail(f"Failed to read diff file: {exc}")

    if not diff_text.strip():
        return pass_without_api(
            files=[],
            note="Out of path scope / empty diff — Gemini API not called",
            stderr_message=(
                "No changes under LOCALIZATION_GATE_PATHSPECS — skip Gemini API"
            ),
        )

    analyzed = analyze_diff(diff_text)
    files = analyzed["files"]
    review_by_file = analyzed.get("review_by_file") or {}
    added_details = analyzed.get("_added_line_details") or {}
    print_files_report(files)

    if not any(text.strip() for text in review_by_file.values()):
        return pass_without_api(
            files=files,
            note="No added lines — Gemini API not called",
            stderr_message=(
                "No added lines to review under scoped diff — skip Gemini API"
            ),
        )

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        summary = format_step_summary(
            status="FAILED",
            issues=[],
            duration_sec=None,
            truncated=False,
            extra_note="GEMINI_API_KEY is missing",
            files=files,
        )
        return fail(
            "GEMINI_API_KEY is missing",
            summary=summary,
            result=empty_result(files),
        )

    try:
        raw_issues, duration, truncated, usage_stats = review_by_file_sessions(
            api_key, review_by_file
        )
        kept = postprocess_issues(raw_issues, added_details)
        result = {
            "has_issue": bool(kept),
            "issues": kept,
            "files": files,
        }
    except Exception as exc:  # noqa: BLE001 — fail-closed for infrastructure errors
        summary = format_step_summary(
            status="FAILED",
            issues=[],
            duration_sec=None,
            truncated=False,
            extra_note=f"fail-closed: {exc}",
            files=files,
        )
        return fail(
            f"Localization gate failed: {exc}",
            summary=summary,
            result=empty_result(files),
        )

    usage = format_usage_summary(usage_stats)
    blocked = has_blocking_issues(kept)
    status = "FAILED" if blocked else "PASSED"
    summary = format_step_summary(
        status=status,
        issues=kept,
        duration_sec=duration,
        truncated=truncated,
        usage=usage,
        usage_stats=usage_stats,
        files=files,
    )
    append_step_summary(summary)
    print_result_json(result)

    if blocked:
        print("Blocking HIGH severity issues found", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
