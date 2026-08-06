#!/usr/bin/env python3
"""Localization Quality Gate — CLI entry point."""

import os
import sys
import time
from typing import Any

import requests

from config import GEMINI_MODEL_QUOTAS
from diff_parser import analyze_diff
from gemini_client import reset_model_failover_state, active_model_quota, call_gemini
from review_batcher import (
    prefers_focused_batches,
    max_chunks_per_batch_for_file,
    split_into_batches,
    with_batch_continuation_header,
)
from response_processor import (
    postprocess_issues,
    parse_model_json,
    extract_response_text,
)
from report_formatter import (
    append_step_summary,
    format_step_summary,
    print_result_json,
    empty_usage_stats,
    record_model_usage,
    compute_effective_rpm,
    print_usage_summary,
    format_usage_summary,
    has_blocking_issues,
)

# Build prompt
def build_prompt(review_text: str) -> str:
    return f"""You are a Localization Quality Reviewer for the UnitX monorepo.
Review ONLY user-facing string VALUES (English / Simplified Chinese / Portuguese).
Formats: JS/TS KEY: 'value'; Python KEY = "..." / KEY = (\\n  "..."\\n); JSON;
i18n CSV (key,zh,en,pt cells); nested locale objects ("key": {{"en": "...", "zh": "..."}}).
Input entries use compact form [file:line] or [file:line|key] then the VALUE
(file/line required for PR annotations; |key is optional context).
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

def review_by_file_sessions(
    api_key: str, review_by_file: dict[str, str],
) -> tuple[list[dict[str, Any]], float, dict[str, Any]]:
    all_issues, total_duration, stats, last_request_at = [], 0.0, empty_usage_stats(), 0.0
    wall_t0 = time.monotonic()
    first_request_at = 0.0
    for path, text in review_by_file.items():
        if not text.strip():
            continue
        focused = prefers_focused_batches(path, text)
        pack = max_chunks_per_batch_for_file(path, text)
        batches = split_into_batches(text, max_chunks_per_batch=pack)
        stats["files_reviewed"] += 1
        stats["batches"] += len(batches)
        if focused:
            mode = f"focused(≤{2} batches, {pack} chunk(s)/req)"
        elif pack is not None:
            mode = f"packed(≤{pack} chunk(s)/req)"
        else:
            mode = "packed"
        print(
            f"Review session: {path} — {len(text)} chars, {len(batches)} batch(es), {mode}",
            file=sys.stderr,
        )
        for i, raw_batch in enumerate(batches):
            batch = with_batch_continuation_header(path, raw_batch, batch_index=i)
            if len(batches) > 1:
                print(f"  batch {i + 1}/{len(batches)}: {len(batch)} chars", file=sys.stderr)
            quota = active_model_quota()
            interval = 60.0 / quota.rpm
            if last_request_at > 0:
                wait = interval - (time.monotonic() - last_request_at)
                if wait > 0:
                    print(
                        f"  rate-limit pace: sleeping {wait:.1f}s (target RPM≤{quota.rpm} on {quota.model_id})",
                        file=sys.stderr,
                    )
                    time.sleep(wait)
            last_request_at = time.monotonic()
            if first_request_at <= 0:
                first_request_at = last_request_at
            api_payload, duration = call_gemini(api_key, build_prompt(batch))
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
    if stats["requests"] > 0:
        stats["wall_sec"] = time.monotonic() - wall_t0
        stats["effective_rpm"] = compute_effective_rpm(
            stats["requests"], first_request_at, last_request_at,
        )
    print_usage_summary(stats)
    return all_issues, total_duration, stats

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

def empty_result(files: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {"has_issue": False, "issues": [], "files": files or []}

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
        return fail(
            "Usage: python platform/devop/localization_quality_gate/"
            "localization_quality_gate.py <diff_file>"
        )
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
    if files:
        print("Diff scope:", file=sys.stderr)
        for item in files:
            print(f"  {item['path']}  +{item['added']} -{item['deleted']}", file=sys.stderr)
    else:
        print("Diff scope: (no files)", file=sys.stderr)

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
