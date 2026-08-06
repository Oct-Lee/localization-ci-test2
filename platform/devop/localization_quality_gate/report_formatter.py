"""Format reports: Markdown summary, JSON output, usage lines."""

import json
import os
import sys
from typing import Any

from config import SEVERITY_HIGH, SEVERITY_MEDIUM, SEVERITY_LOW, GEMINI_MODEL_QUOTAS
from models import Issue, FileStat

def count_by_severity(issues: list[Issue]) -> dict[str, int]:
    counts = {SEVERITY_HIGH: 0, SEVERITY_MEDIUM: 0, SEVERITY_LOW: 0}
    for issue in issues:
        counts[issue["severity"]] = counts.get(issue["severity"], 0) + 1
    return counts

def has_blocking_issues(issues: list[Issue]) -> bool:
    return any(issue["severity"] == SEVERITY_HIGH for issue in issues)

def _md_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()

def format_step_summary(
    *, status: str, issues: list[Issue], duration_sec: float | None,
    usage: str = "N/A", extra_note: str = "",
    files: list[FileStat] | None = None, usage_stats: dict[str, Any] | None = None,
) -> str:
    counts = count_by_severity(issues)
    duration = f"{duration_sec:.1f}s" if duration_sec is not None else "N/A"
    lines = [
        "## Localization Quality Gate", "",
        f"- Status: {status}",
        f"- High: {counts[SEVERITY_HIGH]} | Medium: {counts[SEVERITY_MEDIUM]} | Low: {counts[SEVERITY_LOW]}",
        f"- Duration: {duration}",
    ]
    if usage_stats:
        lines.extend(f"- {line}" for line in format_usage_lines(usage_stats))
    else:
        lines.append(f"- Token usage: {usage}")
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

def print_result_json(result: dict[str, Any]) -> None:
    print(json.dumps(result, ensure_ascii=False, indent=2))

def empty_usage_stats() -> dict[str, Any]:
    primary = GEMINI_MODEL_QUOTAS[0]
    return {
        "requests": 0, "prompt_tokens": 0, "candidates_tokens": 0, "total_tokens": 0,
        "batches": 0, "chars_sent": 0, "files_reviewed": 0,
        "models_used": [], "model_limits": {},
        "rpm_limit": primary.rpm, "tpm_limit": primary.tpm or 0, "rpd_limit": primary.rpd,
        "min_interval_sec": 60.0 / primary.rpm,
        "wall_sec": 0.0, "effective_rpm": None,
    }

def record_model_usage(stats: dict[str, Any], quota) -> None:
    mid = quota.model_id
    if mid not in stats["models_used"]:
        stats["models_used"].append(mid)
    stats["model_limits"][mid] = {
        "rpm": quota.rpm, "rpd": quota.rpd, "tpm": quota.tpm,
        "min_interval_sec": 60.0 / quota.rpm,
    }
    stats["rpm_limit"], stats["rpd_limit"] = quota.rpm, quota.rpd
    stats["tpm_limit"] = quota.tpm or 0
    stats["min_interval_sec"] = 60.0 / quota.rpm

def compute_effective_rpm(
    request_count: int, first_start: float, last_start: float,
) -> float | None:
    if request_count < 2:
        return None
    span = last_start - first_start
    if span <= 0:
        return None
    return (request_count - 1) / (span / 60.0)

def format_usage_lines(stats: dict[str, Any]) -> list[str]:
    models = stats.get("models_used") or []
    models_s = ", ".join(models) if models else "N/A"
    eff = stats.get("effective_rpm")
    if isinstance(eff, (int, float)):
        rpm_s = f"{eff:.1f}/min effective"
    elif stats.get("requests", 0) < 2:
        rpm_s = "N/A (<2 requests)"
    else:
        rpm_s = "N/A"
    return [
        f"RPM: {rpm_s} (limit {stats['rpm_limit']})",
        f"RPD: {stats['requests']} this run (limit {stats['rpd_limit']})",
        (
            f"Tokens: total={stats['total_tokens']} "
            f"(prompt={stats['prompt_tokens']}, candidates={stats['candidates_tokens']})"
        ),
        (
            f"Requests: {stats['requests']} on {models_s} "
            f"(pace ≥{stats['min_interval_sec']:.1f}s; batches={stats['batches']}, "
            f"files={stats['files_reviewed']}, chars={stats['chars_sent']})"
        ),
    ]

def format_usage_summary(stats: dict[str, Any]) -> str:
    return " | ".join(format_usage_lines(stats))

def print_usage_summary(stats: dict[str, Any]) -> None:
    print("Usage:", file=sys.stderr)
    for line in format_usage_lines(stats):
        print(f"  {line}", file=sys.stderr)
