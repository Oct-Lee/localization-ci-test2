"""Process Gemini responses: validation, filtering, allowlist, dedupe, location attachment."""

from __future__ import annotations

import json
import re
import sys
from typing import Any

from diff_parser import extract_user_facing_hints
from models import Issue

from config import (
    _COMPLETE_FINISH_REASONS,
    _ID_PROBLEM_TOKENS,
    _PUNCT_ONLY_RE,
    _SEVERITY_RANK,
    _STYLE_WORDING_PROBLEM_RE,
    _WS_PROBLEM_RE,
    ALLOWLIST_PATH,
    ASSIGNMENT_LINE_RE,
    FENCE_RE,
    JSON_KV_RE,
    KEY_ASSIGN_PREFIX_RE,
    KEY_ONLY_RE,
    PLACEHOLDER_RE,
    PROP_KEY,
    SEVERITY_HIGH,
    SEVERITY_LOW,
    SEVERITY_MEDIUM,
    STRING_VALUE_LINE_RE,
    SYNTAX_PROBLEM_RE,
    VALID_SEVERITIES,
)


# ---- Helper functions ----
def strip_markdown_fence(text: str) -> str:
    stripped = text.strip()
    if m := FENCE_RE.match(stripped):
        return m.group(1).strip()
    return stripped


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


def extract_response_text(api_payload: dict[str, Any]) -> str:
    """Extract text from Gemini response payload, ensuring generation
    complete."""
    assert_generation_complete(api_payload)
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
            skipped_reasons.append(
                f"issues[{i}]: invalid severity {issue['severity']!r}"
            )
            continue
        item: Issue = {
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
            print(f"Malformed model issue (dropped): {reason}", file=sys.stderr)
        print(
            f"Dropped {len(skipped_reasons)} malformed issue(s); "
            f"keeping {len(validated_issues)} valid issue(s)",
            file=sys.stderr,
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


def normalize_issue_to_string_value(issue: Issue) -> Issue:
    out = dict(issue)
    original_raw = out.get("original", "")
    suggestion_raw = out.get("suggestion", "")
    o_m = ASSIGNMENT_LINE_RE.match(original_raw)
    s_m = ASSIGNMENT_LINE_RE.match(suggestion_raw)
    if o_m and s_m:
        if o_m.group(1) != s_m.group(1):
            out.update(
                original=o_m.group(1), suggestion=s_m.group(1), _kind="identifier"
            )
            return out
        out.update(original=o_m.group(3), suggestion=s_m.group(3), _kind="value")
        return out
    if o_m and not s_m:
        out.update(original=o_m.group(3), _kind="value")
        if suggestion_raw:
            out["suggestion"] = suggestion_raw
        return out
    if m := KEY_ASSIGN_PREFIX_RE.match(original_raw):
        out["_recover_original"] = True
        out["_key_name"] = m.group(1)
        if suggestion_raw and not KEY_ASSIGN_PREFIX_RE.match(suggestion_raw):
            out["suggestion"] = suggestion_raw
        return out
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


def is_identifier_issue(issue: Issue) -> bool:
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


def is_whitespace_style_issue(issue: Issue) -> bool:
    if _WS_PROBLEM_RE.search(issue.get("problem", "") or ""):
        return True
    original, suggestion = issue.get("original", ""), issue.get("suggestion", "")
    if (
        original
        and suggestion
        and original != suggestion
        and original.strip() == suggestion.strip()
    ):
        return True
    return False


def is_style_wording_issue(issue: Issue) -> bool:
    """Punctuation / wording preference — not a blocking misspelling."""
    if _STYLE_WORDING_PROBLEM_RE.search(issue.get("problem", "") or ""):
        return True
    original, suggestion = issue.get("original", ""), issue.get("suggestion", "")
    if not original or not suggestion or original == suggestion:
        return False
    return _PUNCT_ONLY_RE.sub(" ", original).strip().lower() == _PUNCT_ONLY_RE.sub(
        " ", suggestion
    ).strip().lower()


def is_syntax_false_positive(issue: Issue) -> bool:
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


def filter_userfacing_issues(
    issues: list[Issue],
    *,
    already_normalized: bool = False,
) -> tuple[list[Issue], list[Issue]]:
    kept, dropped = [], []
    for issue in issues:
        normalized = (
            issue if already_normalized else normalize_issue_to_string_value(issue)
        )
        if is_syntax_false_positive(normalized):
            dropped.append(issue)
            continue
        if KEY_ASSIGN_PREFIX_RE.match((normalized.get("original") or "").strip()):
            dropped.append(issue)
            continue
        if is_identifier_issue(normalized) or is_whitespace_style_issue(normalized):
            normalized["severity"] = SEVERITY_LOW
        elif (
            normalized.get("severity") == SEVERITY_HIGH
            and is_style_wording_issue(normalized)
        ):
            normalized["severity"] = SEVERITY_MEDIUM
        normalized.pop("_kind", None)
        normalized.pop("_recover_original", None)
        normalized.pop("_key_name", None)
        kept.append(normalized)
    return kept, dropped


def placeholders(text: str) -> set[str]:
    return set(PLACEHOLDER_RE.findall(text))


def filter_placeholder_mismatches(
    issues: list[Issue],
) -> tuple[list[Issue], list[Issue]]:
    kept, dropped = [], []
    for issue in issues:
        if placeholders(issue["original"]) != placeholders(issue["suggestion"]):
            dropped.append(issue)
        else:
            kept.append(issue)
    return kept, dropped


def load_allowlist(path=None) -> list[dict[str, str]]:
    allowlist_path = path if path is not None else ALLOWLIST_PATH
    if not allowlist_path.is_file():
        return []
    try:
        raw = json.loads(allowlist_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(
            f"Allowlist ignored (unreadable): {allowlist_path}: {exc}", file=sys.stderr
        )
        return []
    if not isinstance(raw, list):
        print(
            f"Allowlist ignored (root must be array): {allowlist_path}", file=sys.stderr
        )
        return []
    entries: list[dict[str, str]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        original = item.get("original")
        if not isinstance(original, str) or not original:
            continue
        entry: dict[str, str] = {"original": original}
        file_path = item.get("file")
        if isinstance(file_path, str) and file_path.strip():
            entry["file"] = file_path.strip().replace("\\", "/")
        entries.append(entry)
    return entries


def _allowlist_file_match(issue_file: str, allow_file: str) -> bool:
    issue_file = (issue_file or "").replace("\\", "/")
    allow_file = allow_file.replace("\\", "/")
    return issue_file == allow_file or issue_file.endswith("/" + allow_file)


_CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def allowlist_original_matches(issue_original: str, allow_original: str) -> bool:
    """Exact VALUE, or domain term inside VALUE (CJK substring / ASCII word)."""
    if not issue_original or not allow_original:
        return False
    if issue_original == allow_original:
        return True
    if _CJK_RE.search(allow_original):
        return allow_original in issue_original
    return (
        re.search(
            rf"(?<![A-Za-z0-9_]){re.escape(allow_original)}(?![A-Za-z0-9_])",
            issue_original,
        )
        is not None
    )


def is_allowlisted(issue: Issue, entries: list[dict[str, str]]) -> bool:
    original = issue.get("original")
    if not isinstance(original, str):
        return False
    issue_file = str(issue.get("file") or "")
    for entry in entries:
        if not allowlist_original_matches(original, entry["original"]):
            continue
        allow_file = entry.get("file")
        if not allow_file or _allowlist_file_match(issue_file, allow_file):
            return True
    return False


def filter_allowlisted(
    issues: list[Issue],
    entries: list[dict[str, str]] | None = None,
) -> tuple[list[Issue], list[Issue]]:
    allow = entries if entries is not None else load_allowlist()
    if not allow:
        return issues, []
    kept, dropped = [], []
    for issue in issues:
        if is_allowlisted(issue, allow):
            dropped.append(issue)
        else:
            kept.append(issue)
    return kept, dropped


def dedupe_issues(issues: list[Issue]) -> list[Issue]:
    best: dict[tuple[Any, ...], Issue] = {}
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
        if _SEVERITY_RANK.get(issue.get("severity"), 0) > _SEVERITY_RANK.get(
            prev.get("severity"), 0
        ):
            best[key] = issue
    return [best[k] for k in order]


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
    issues: list[Issue],
    added_details: dict[str, list[dict[str, Any]]],
) -> list[Issue]:
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
        paths = (
            [out["file"]] if out.get("file") in added_details else list(added_details)
        )
        exact, soft = [], []
        for path in paths:
            for row in added_details.get(path, []):
                text = row["text"]
                hit = (path, row["line"])
                if _value_exact_in_line(raw, text) or _value_exact_in_line(
                    needle, text
                ):
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


def _lookup_added_value(
    added_details: dict[str, list[dict[str, Any]]],
    path: str | None,
    line: Any,
    key_name: str | None = None,
) -> tuple[str | None, int | None]:
    paths = [path] if path in added_details else list(added_details)
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
    issues: list[Issue],
    added_details: dict[str, list[dict[str, Any]]],
) -> list[Issue]:
    recovered = []
    for issue in issues:
        out = dict(issue)
        orig = (out.get("original") or "").strip()
        need = out.pop("_recover_original", False) or bool(
            KEY_ASSIGN_PREFIX_RE.match(orig)
        )
        if not need:
            recovered.append(out)
            continue
        key_name = out.pop("_key_name", None)
        if not key_name and (m := KEY_ASSIGN_PREFIX_RE.match(orig)):
            key_name = m.group(1)
        value, found_line = _lookup_added_value(
            added_details,
            out.get("file"),
            out.get("line"),
            key_name,
        )
        if value is not None:
            out["original"] = value
            if found_line and (
                not isinstance(out.get("line"), int) or out.get("line", -1) <= 0
            ):
                out["line"] = found_line
            sugg = out.get("suggestion", "")
            if not sugg or KEY_ASSIGN_PREFIX_RE.match(sugg.strip()):
                out["suggestion"] = value.lstrip() if value[:1].isspace() else value
        recovered.append(out)
    return recovered


def _log_filtered(
    dropped: list[dict[str, Any]], label: str, *, show_samples: bool = False
) -> None:
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
    issues: list[Issue],
    added_details: dict[str, list[dict[str, Any]]],
    *,
    allowlist_entries: list[dict[str, str]] | None = None,
) -> list[Issue]:
    """Post-process model issues.

    If allowlist_entries is provided, use it; otherwise call
    load_allowlist(). Façade may pass entries so tests can patch
    load_allowlist on the entry module.
    """
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
    entries = allowlist_entries if allowlist_entries is not None else load_allowlist()
    kept, allow_dropped = filter_allowlisted(kept, entries=entries)
    if allow_dropped:
        _log_filtered(allow_dropped, "allowlisted issue(s)")
    before = len(kept)
    kept = dedupe_issues(kept)
    if len(kept) < before:
        print(f"Deduped {before - len(kept)} duplicate issue(s)", file=sys.stderr)
    return kept
