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


def build_prompt(review_text: str) -> str:
    return f"""You are a Localization Quality Reviewer.

Review ONLY user-facing texts in the PR changes below.
Supported languages in string content: English, Simplified Chinese, Portuguese.

Ignore: variable names, function names, class names, URLs, file paths, UUIDs,
hashes, debug-only messages, and internal comments.

For each issue:
- "original" must be the complete user-facing original text
- "suggestion" must only correct the erroneous parts
- Placeholders matching {{...}}, %s / %d / %w style, and ${{...}} MUST remain identical

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


def parse_diff(diff_text: str) -> str:
    """Extract added lines with ±CONTEXT_LINES context for Gemini review."""
    if not diff_text or not diff_text.strip():
        return ""

    lines = diff_text.splitlines()
    review_chunks: list[str] = []
    seen: set[str] = set()
    current_file = ""

    for idx, line in enumerate(lines):
        if line.startswith("+++ b/"):
            current_file = line[6:]
            continue
        if line.startswith("+++ "):
            continue
        if not line.startswith("+"):
            continue
        # Added content line (not +++ metadata)
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
        if chunk in seen:
            continue
        seen.add(chunk)
        header = f"# file: {current_file}" if current_file else "# file: (unknown)"
        review_chunks.append(f"{header}\n{chunk}")

    return "\n\n".join(review_chunks)


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

    validated_issues: list[dict[str, str]] = []
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
        validated_issues.append(
            {
                "original": issue["original"].strip(),
                "problem": issue["problem"].strip(),
                "suggestion": issue["suggestion"].strip(),
                "severity": severity,
            }
        )

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
    issues: list[dict[str, str]],
    duration_sec: float | None,
    truncated: bool,
    usage: str = "N/A",
    extra_note: str = "",
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
    lines.extend(["", "### Issues", ""])
    if not issues:
        lines.append("_No issues reported._")
    else:
        lines.append("| Severity | Original | Problem | Suggestion |")
        lines.append("| --- | --- | --- | --- |")
        for issue in issues:
            lines.append(
                "| {severity} | {original} | {problem} | {suggestion} |".format(
                    severity=_md_cell(issue["severity"]),
                    original=_md_cell(issue["original"]),
                    problem=_md_cell(issue["problem"]),
                    suggestion=_md_cell(issue["suggestion"]),
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


def fail(message: str, *, summary: str | None = None) -> int:
    print(message, file=sys.stderr)
    if summary:
        append_step_summary(summary)
        print(summary)
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
        print("No changes detected")
        summary = format_step_summary(
            status="PASSED",
            issues=[],
            duration_sec=None,
            truncated=False,
            extra_note="No changes detected",
        )
        append_step_summary(summary)
        print(summary)
        return 0

    review_text = parse_diff(diff_text)
    if not review_text.strip():
        print("No user-facing changes")
        summary = format_step_summary(
            status="PASSED",
            issues=[],
            duration_sec=None,
            truncated=False,
            extra_note="No user-facing changes",
        )
        append_step_summary(summary)
        print(summary)
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
        )
        return fail("GEMINI_API_KEY is missing", summary=summary)

    prompt = build_prompt(review_text)
    try:
        api_payload, duration = call_gemini(api_key, prompt)
        raw_text = extract_response_text(api_payload)
        result = parse_model_json(raw_text)
        check_placeholders(result["issues"])
    except Exception as exc:  # noqa: BLE001 — fail-closed for infrastructure errors
        summary = format_step_summary(
            status="FAILED",
            issues=[],
            duration_sec=None,
            truncated=truncated,
            extra_note=f"fail-closed: {exc}",
        )
        return fail(f"Localization gate failed: {exc}", summary=summary)

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
    )
    append_step_summary(summary)
    print(summary)

    for issue in issues:
        print(
            f"[{issue['severity']}] original={issue['original']!r} "
            f"problem={issue['problem']!r} suggestion={issue['suggestion']!r}"
        )

    if blocked:
        print("Blocking HIGH severity issues found", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
