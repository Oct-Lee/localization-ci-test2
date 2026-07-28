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
from typing import Any

import requests

MODEL_ID = "gemini-3.1-flash-lite"
GEMINI_ENDPOINT = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{MODEL_ID}:generateContent"
)
HTTP_TIMEOUT_SEC = 60
MAX_ATTEMPTS = 3
RETRYABLE_STATUS = {429, 500, 503}
MAX_REVIEW_CHARS = 100_000
CONTEXT_LINES = 3
PLACEHOLDER_RE = re.compile(r"\{[^}]+\}|%\w|\$\{[^}]+\}")
FENCE_RE = re.compile(
    r"^\s*```(?:json)?\s*\n?(.*?)\n?\s*```\s*$",
    re.DOTALL | re.IGNORECASE,
)

SEVERITY_HIGH = "high"
SEVERITY_MEDIUM = "medium"
SEVERITY_LOW = "low"
VALID_SEVERITIES = {SEVERITY_HIGH, SEVERITY_MEDIUM, SEVERITY_LOW}
HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def build_prompt(review_text: str) -> str:
    return f"""You are a Localization Quality Reviewer.

Review ONLY user-facing texts in the PR changes below.
Supported languages in string content: English, Simplified Chinese, Portuguese.

Ignore: variable names, function names, class names, URLs, file paths, UUIDs,
hashes, debug-only messages, and internal comments.

For each issue:
- "original" must be the complete user-facing original text
- "suggestion" must only correct the erroneous parts
- "file" and "line" must come from the "# file:" / "# line:" markers of the
  matching added line when available
- Placeholders matching {{...}}, %s / %d / %w style, and ${{...}} MUST remain identical

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
  seriously hurt understanding. ALL spelling / grammar / incorrect word usage
  MUST be "high".
- MEDIUM: Wording / Readability / consistency improvements
- LOW: Capitalization and optional style. Capitalization MUST be "low".

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


def _new_file_entry(path: str) -> dict[str, Any]:
    return {
        "path": path,
        "added": 0,
        "deleted": 0,
        "added_lines": [],  # list[{"line": int, "text": str}]
    }


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
    seen: set[str] = set()

    def ensure_file(path: str) -> dict[str, Any]:
        if path not in files_map:
            files_map[path] = _new_file_entry(path)
            files_order.append(path)
        return files_map[path]

    for idx, line in enumerate(lines):
        if line.startswith("+++ b/"):
            current_file = line[6:]
            ensure_file(current_file)
            new_line_no = None
            continue
        if line.startswith("+++ "):
            # e.g. +++ /dev/null
            rest = line[4:]
            if rest.startswith("b/"):
                current_file = rest[2:]
                ensure_file(current_file)
            new_line_no = None
            continue

        hunk = HUNK_RE.match(line)
        if hunk:
            new_line_no = int(hunk.group(3))
            continue

        if not current_file:
            # Still allow +++-less diffs; try --- a/ fallback later via +++ only
            pass

        if line.startswith("+") and not line.startswith("+++"):
            entry = ensure_file(current_file or "(unknown)")
            line_no = new_line_no if new_line_no is not None else -1
            text = line[1:]
            entry["added"] += 1
            entry["added_lines"].append({"line": line_no, "text": text})
            if new_line_no is not None:
                new_line_no += 1

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
            chunk = "\n".join(window)
            dedupe_key = f"{current_file}:{line_no}:{chunk}"
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            path_label = current_file or "(unknown)"
            header = f"# file: {path_label}\n# line: {line_no}"
            review_chunks.append(f"{header}\n{chunk}")
            continue

        if line.startswith("-") and not line.startswith("---"):
            entry = ensure_file(current_file or "(unknown)")
            entry["deleted"] += 1
            continue

        # context line (starts with space) advances new-side counter
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

    return {
        "review_text": "\n\n".join(review_chunks),
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


def check_placeholders(issues: list[dict[str, str]]) -> None:
    for issue in issues:
        original_ph = placeholders(issue["original"])
        suggestion_ph = placeholders(issue["suggestion"])
        if original_ph != suggestion_ph:
            raise ValueError(
                "Placeholder mismatch between original and suggestion: "
                f"original={sorted(original_ph)} suggestion={sorted(suggestion_ph)} "
                f"issue={issue}"
            )


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
) -> str:
    counts = count_by_severity(issues)
    duration = f"{duration_sec:.1f}s" if duration_sec is not None else "N/A"
    lines = [
        "## Localization Quality Gate",
        "",
        f"- Status: {status}",
        f"- High: {counts[SEVERITY_HIGH]} | Medium: {counts[SEVERITY_MEDIUM]} "
        f"| Low: {counts[SEVERITY_LOW]}",
        f"- Duration: {duration}",
        f"- Truncated: {'yes' if truncated else 'no'}",
        f"- Token usage: {usage}",
    ]
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


def call_gemini(api_key: str, prompt: str) -> tuple[dict[str, Any], float]:
    url = f"{GEMINI_ENDPOINT}?key={api_key}"
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    last_error: Exception | None = None
    start = time.monotonic()

    for attempt in range(MAX_ATTEMPTS):
        try:
            response = requests.post(url, json=body, timeout=HTTP_TIMEOUT_SEC)
        except requests.Timeout as exc:
            last_error = exc
            if attempt < MAX_ATTEMPTS - 1:
                time.sleep(2**attempt)
                continue
            raise RuntimeError(
                f"Gemini API timeout after {MAX_ATTEMPTS} attempts"
            ) from exc
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

        if response.status_code in RETRYABLE_STATUS and attempt < MAX_ATTEMPTS - 1:
            time.sleep(2**attempt)
            continue

        raise RuntimeError(
            f"Gemini API failed with HTTP {response.status_code}: "
            f"{response.text[:1000]}"
        )

    raise RuntimeError(f"Gemini API failed after retries: {last_error}")


def extract_usage(api_payload: dict[str, Any]) -> str:
    meta = api_payload.get("usageMetadata") or api_payload.get("usage_metadata")
    if not isinstance(meta, dict):
        return "N/A"
    parts = []
    for key in (
        "promptTokenCount",
        "candidatesTokenCount",
        "totalTokenCount",
        "prompt_token_count",
        "candidates_token_count",
        "total_token_count",
    ):
        if key in meta:
            parts.append(f"{key}={meta[key]}")
    return ", ".join(parts) if parts else "N/A"


def empty_result(files: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {"has_issue": False, "issues": [], "files": files or []}


def print_result_json(result: dict[str, Any]) -> None:
    """Stdout contract: validated JSON matching the gate schema (+ files)."""
    print(json.dumps(result, ensure_ascii=False, indent=2))


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
        print("No changes detected", file=sys.stderr)
        summary = format_step_summary(
            status="PASSED",
            issues=[],
            duration_sec=None,
            truncated=False,
            extra_note="No changes detected",
            files=[],
        )
        append_step_summary(summary)
        print_result_json(empty_result())
        return 0

    analyzed = analyze_diff(diff_text)
    files = analyzed["files"]
    review_text = analyzed["review_text"]
    added_details = analyzed.get("_added_line_details") or {}
    print_files_report(files)

    if not review_text.strip():
        print("No user-facing changes", file=sys.stderr)
        summary = format_step_summary(
            status="PASSED",
            issues=[],
            duration_sec=None,
            truncated=False,
            extra_note="No user-facing changes",
            files=files,
        )
        append_step_summary(summary)
        print_result_json(empty_result(files))
        return 0

    truncated = False
    if len(review_text) > MAX_REVIEW_CHARS:
        review_text = review_text[:MAX_REVIEW_CHARS]
        truncated = True
        print(
            f"Review text truncated to {MAX_REVIEW_CHARS} characters",
            file=sys.stderr,
        )

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        summary = format_step_summary(
            status="FAILED",
            issues=[],
            duration_sec=None,
            truncated=truncated,
            extra_note="GEMINI_API_KEY is missing",
            files=files,
        )
        return fail(
            "GEMINI_API_KEY is missing",
            summary=summary,
            result=empty_result(files),
        )

    prompt = build_prompt(review_text)
    try:
        api_payload, duration = call_gemini(api_key, prompt)
        raw_text = extract_response_text(api_payload)
        result = parse_model_json(raw_text)
        check_placeholders(result["issues"])
        result["issues"] = attach_locations(result["issues"], added_details)
        result["files"] = files
    except Exception as exc:  # noqa: BLE001 — fail-closed for infrastructure errors
        summary = format_step_summary(
            status="FAILED",
            issues=[],
            duration_sec=None,
            truncated=truncated,
            extra_note=f"fail-closed: {exc}",
            files=files,
        )
        return fail(
            f"Localization gate failed: {exc}",
            summary=summary,
            result=empty_result(files),
        )

    issues = result["issues"]
    usage = extract_usage(api_payload)
    blocked = has_blocking_issues(issues)
    status = "FAILED" if blocked else "PASSED"
    summary = format_step_summary(
        status=status,
        issues=issues,
        duration_sec=duration,
        truncated=truncated,
        usage=usage,
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
