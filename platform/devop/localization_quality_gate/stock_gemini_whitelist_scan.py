#!/usr/bin/env python3
"""Stock Gemini scan for LOCALIZATION_GATE_PATHSPECS with checkpoint resume.

Reuses localization_quality_gate prompt/batching/Gemini client.
API key via env GEMINI_API_KEY only — never commit keys.

Usage:
  export GEMINI_API_KEY='...'
  python platform/devop/localization_quality_gate/stock_gemini_whitelist_scan.py
  python platform/devop/localization_quality_gate/stock_gemini_whitelist_scan.py --resume
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import OrderedDict, defaultdict
from pathlib import Path
from typing import Any

_PKG_DIR = Path(__file__).resolve().parent
if str(_PKG_DIR) not in sys.path:
    sys.path.insert(0, str(_PKG_DIR))

from diff_parser import _compact_review_entry  # noqa: E402
from gemini_client import (  # noqa: E402
    active_model_quota,
    call_gemini,
    reset_model_failover_state,
)
from localization_quality_gate import (  # noqa: E402
    build_prompt,
    empty_result,
    extract_usage_counts,
    postprocess_issues,
)
from report_formatter import (  # noqa: E402
    count_by_severity,
    empty_usage_stats,
    format_step_summary,
    print_result_json,
    print_usage_summary,
    record_model_usage,
)
from review_batcher import (  # noqa: E402
    max_chunks_per_batch_for_file,
    prefers_focused_batches,
    split_into_batches,
    with_batch_continuation_header,
)
from stock_user_facing_scan import (  # noqa: E402
    SKIP_PATH_RE,
    extract_whitelist_records,
    git_ls_files,
    is_whitelist_path,
)

import config as gate_config  # noqa: E402
from config import (  # noqa: E402
    FOCUSED_TARGET_BATCHES,
    min_request_interval_sec,
)

# Stock scans are large; allow longer HTTP read and more transient retries.
gate_config.HTTP_TIMEOUT_SEC = 180
gate_config.MAX_ATTEMPTS = 5


def build_review_by_file(
    records: list[dict[str, Any]],
) -> tuple[OrderedDict[str, str], dict[str, list[dict[str, Any]]]]:
    by_file: OrderedDict[str, list[str]] = OrderedDict()
    added_details: dict[str, list[dict[str, Any]]] = defaultdict(list)
    seen: set[tuple[str, int, str]] = set()
    for r in records:
        path = r["file"]
        line = int(r.get("line") or -1)
        value = r["value"]
        key = (path, line, value)
        if key in seen:
            continue
        seen.add(key)
        chunk = _compact_review_entry(path, line, [value])
        if not chunk:
            continue
        by_file.setdefault(path, []).append(chunk)
        added_details[path].append({"line": line, "text": value})
    review_by_file = OrderedDict(
        (path, "\n\n".join(chunks)) for path, chunks in by_file.items() if chunks
    )
    return review_by_file, dict(added_details)


def load_checkpoint(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"completed_files": [], "issues": [], "stats": empty_usage_stats()}
    return json.loads(path.read_text(encoding="utf-8"))


def save_checkpoint(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    tmp.replace(path)


def review_with_checkpoint(
    api_key: str,
    review_by_file: dict[str, str],
    checkpoint_path: Path,
    *,
    resume: bool,
    max_chunks_per_batch: int | None = None,
) -> tuple[list[dict[str, Any]], float, dict[str, Any]]:
    ckpt = (
        load_checkpoint(checkpoint_path)
        if resume
        else {"completed_files": [], "issues": [], "stats": empty_usage_stats()}
    )
    completed = set(ckpt.get("completed_files") or [])
    all_issues: list[dict[str, Any]] = list(ckpt.get("issues") or [])
    stats: dict[str, Any] = ckpt.get("stats") or empty_usage_stats()
    total_duration = float(stats.get("api_duration_sec") or 0.0)
    last_request_at = 0.0
    wall_t0 = time.monotonic()
    first_request_at = 0.0

    pending = [
        (p, t) for p, t in review_by_file.items() if p not in completed and t.strip()
    ]
    print(
        f"Files to review: {len(pending)} " f"(skip {len(completed)} checkpointed)",
        file=sys.stderr,
    )

    for path, text in pending:
        focused = prefers_focused_batches(path, text)
        pack = (
            max_chunks_per_batch
            if max_chunks_per_batch is not None and max_chunks_per_batch > 0
            else max_chunks_per_batch_for_file(path, text)
        )
        batches = split_into_batches(text, max_chunks_per_batch=pack)
        stats["files_reviewed"] = int(stats.get("files_reviewed") or 0) + 1
        stats["batches"] = int(stats.get("batches") or 0) + len(batches)
        if focused:
            mode = f"focused(≤{FOCUSED_TARGET_BATCHES} batches, {pack} chunk(s)/req)"
        elif pack is not None:
            mode = f"packed(≤{pack} chunk(s)/req)"
        else:
            mode = "packed"
        print(
            f"Review session: {path} — {len(text)} chars, "
            f"{len(batches)} batch(es), {mode}",
            file=sys.stderr,
        )
        file_issues: list[dict[str, Any]] = []
        for i, raw_batch in enumerate(batches):
            batch = with_batch_continuation_header(path, raw_batch, batch_index=i)
            if len(batches) > 1:
                print(
                    f"  batch {i + 1}/{len(batches)}: {len(batch)} chars",
                    file=sys.stderr,
                )
            quota = active_model_quota()
            interval = min_request_interval_sec(quota.rpm)
            if last_request_at > 0:
                wait = interval - (time.monotonic() - last_request_at)
                if wait > 0:
                    print(
                        f"  rate-limit pace: sleeping {wait:.1f}s "
                        f"(target RPM≤{quota.rpm} on {quota.model_id})",
                        file=sys.stderr,
                    )
                    time.sleep(wait)
            last_request_at = time.monotonic()
            if first_request_at <= 0:
                first_request_at = last_request_at
            try:
                api_payload, duration = call_gemini(api_key, build_prompt(batch))
            except RuntimeError as exc:
                # Skip this batch but keep going; record error for resume visibility.
                print(f"  WARN batch failed, skipping: {exc}", file=sys.stderr)
                stats["batch_errors"] = int(stats.get("batch_errors") or 0) + 1
                continue
            total_duration += duration
            stats["requests"] = int(stats.get("requests") or 0) + 1
            record_model_usage(stats, active_model_quota())
            stats["chars_sent"] = int(stats.get("chars_sent") or 0) + len(batch)
            counts = extract_usage_counts(api_payload)
            stats["prompt_tokens"] = int(stats.get("prompt_tokens") or 0) + counts.get(
                "prompt", 0
            )
            stats["candidates_tokens"] = int(
                stats.get("candidates_tokens") or 0
            ) + counts.get("candidates", 0)
            stats["total_tokens"] = int(stats.get("total_tokens") or 0) + counts.get(
                "total", 0
            )
            from response_processor import (  # local import
                extract_response_text,
                parse_model_json,
            )

            parsed = parse_model_json(extract_response_text(api_payload))
            for issue in parsed["issues"]:
                if not issue.get("file"):
                    issue["file"] = path
            file_issues.extend(parsed["issues"])

        all_issues.extend(file_issues)
        completed.add(path)
        stats["api_duration_sec"] = total_duration
        save_checkpoint(
            checkpoint_path,
            {
                "completed_files": sorted(completed),
                "issues": all_issues,
                "stats": stats,
            },
        )
        print(
            f"  checkpointed {path} (+{len(file_issues)} raw issues); "
            f"done {len(completed)}/{len(review_by_file)}",
            file=sys.stderr,
        )

    if stats.get("requests"):
        stats["wall_sec"] = time.monotonic() - wall_t0
    print_usage_summary(stats)
    return all_issues, total_duration, stats


def write_outputs(
    out: Path,
    result: dict[str, Any],
    stats: dict[str, Any],
    summary_md: str,
) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (out / "usage.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    issues = result.get("issues") or []
    with (out / "issues.jsonl").open("w", encoding="utf-8") as fh:
        for iss in issues:
            fh.write(json.dumps(iss, ensure_ascii=False) + "\n")
    high = [i for i in issues if str(i.get("severity", "")).lower() == "high"]
    md = [
        "# Gemini whitelist stock scan\n\n",
        summary_md,
        "\n",
        f"## HIGH ({len(high)})\n\n",
    ]
    for i in high:
        md.append(
            f"- `{i.get('file')}:{i.get('line')}`: "
            f"{str(i.get('original', ''))[:100]!r} → "
            f"{str(i.get('suggestion', ''))[:100]!r} "
            f"({i.get('problem', '')})\n"
        )
    (out / "REPORT.md").write_text("".join(md), encoding="utf-8")
    (out / "issues_high.md").write_text(
        "".join(
            ["# HIGH issues\n\n"]
            + [
                f"- `{i.get('file')}:{i.get('line')}`: "
                f"{str(i.get('original', ''))[:120]!r} → "
                f"{str(i.get('suggestion', ''))[:120]!r}\n"
                for i in high
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path, default=Path("tmp/l10n_gemini_scan"))
    parser.add_argument("--max-files", type=int, default=0)
    parser.add_argument(
        "--paths",
        nargs="*",
        default=[],
        help="Only scan these repo-relative whitelist paths (space-separated)",
    )
    parser.add_argument(
        "--paths-file",
        type=Path,
        default=None,
        help="File with one repo-relative path per line to scan",
    )
    parser.add_argument(
        "--max-chunks-per-batch",
        type=int,
        default=0,
        help="Override batch packing (e.g. 8–15 for higher recall). 0=auto",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from out/checkpoint.json",
    )
    args = parser.parse_args()
    repo = args.repo.resolve()
    out = args.out if args.out.is_absolute() else repo / args.out
    out.mkdir(parents=True, exist_ok=True)
    checkpoint_path = out / "checkpoint.json"

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("GEMINI_API_KEY is required in the environment", file=sys.stderr)
        return 1

    reset_model_failover_state()
    all_files = git_ls_files(repo)
    wl_files = [
        f for f in all_files if is_whitelist_path(f) and not SKIP_PATH_RE.search(f)
    ]
    path_filter: set[str] = set()
    for p in args.paths or []:
        path_filter.add(p.strip().lstrip("./"))
    if args.paths_file is not None:
        pf = (
            args.paths_file if args.paths_file.is_absolute() else repo / args.paths_file
        )
        for line in pf.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if s and not s.startswith("#"):
                path_filter.add(s.lstrip("./"))
    if path_filter:
        wl_files = [f for f in wl_files if f in path_filter]
        missing = sorted(path_filter - set(wl_files))
        if missing:
            print(
                f"WARN paths not in whitelist / missing: {missing[:20]}"
                + ("..." if len(missing) > 20 else ""),
                file=sys.stderr,
            )
    wl_files.sort()
    if args.max_files and args.max_files > 0:
        wl_files = wl_files[: args.max_files]
    print(f"Whitelist files: {len(wl_files)}", file=sys.stderr)

    records: list[dict[str, Any]] = []
    for f in wl_files:
        records.extend(extract_whitelist_records(repo, f))
    print(f"Extracted values: {len(records)}", file=sys.stderr)

    review_by_file, added_details = build_review_by_file(records)
    files_meta = [
        {"path": p, "added": len(added_details.get(p, [])), "deleted": 0}
        for p in review_by_file
    ]
    print(f"Files with review text: {len(review_by_file)}", file=sys.stderr)
    if not review_by_file:
        result = empty_result(files_meta)
        write_outputs(out, result, {}, "No review text.")
        print_result_json(result)
        return 0

    chunk_override = (
        args.max_chunks_per_batch if args.max_chunks_per_batch > 0 else None
    )
    if chunk_override is not None:
        print(f"Chunk override: ≤{chunk_override} chunk(s)/req", file=sys.stderr)

    issues, duration, stats = review_with_checkpoint(
        api_key,
        review_by_file,
        checkpoint_path,
        resume=args.resume,
        max_chunks_per_batch=chunk_override,
    )
    kept = postprocess_issues(issues, added_details)
    result = {
        "has_issue": bool(kept),
        "issues": kept,
        "files": files_meta,
        "duration_sec": duration,
        "usage": stats,
    }
    by_sev = count_by_severity(kept)
    summary = format_step_summary(
        status="STOCK_GEMINI_SCAN",
        issues=kept,
        duration_sec=duration,
        extra_note=(
            f"whitelist files={len(wl_files)} values={len(records)} "
            f"high={by_sev.get('high', 0)} medium={by_sev.get('medium', 0)} "
            f"low={by_sev.get('low', 0)} batch_errors={stats.get('batch_errors', 0)}"
        ),
        files=files_meta,
    )
    write_outputs(out, result, stats, summary)
    print_result_json(result)
    print(f"Wrote {out}", file=sys.stderr)
    print(
        f"Summary: issues={len(kept)} high={by_sev.get('high', 0)} "
        f"medium={by_sev.get('medium', 0)} low={by_sev.get('low', 0)} "
        f"requests={stats.get('requests')} tokens={stats.get('total_tokens')}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
