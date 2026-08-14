#!/usr/bin/env python3
"""Stock scan: extract user-facing VALUES (scope B), export full values + filtered suspects.

Does NOT call Cursor/LLM. Review artifacts under OUT_DIR and wait for human confirm.

Usage (from repo root):
  python platform/devop/localization_quality_gate/stock_user_facing_scan.py
  python platform/devop/localization_quality_gate/stock_user_facing_scan.py --out tmp/l10n_scan
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

_PKG_DIR = Path(__file__).resolve().parent
if str(_PKG_DIR) not in sys.path:
    sys.path.insert(0, str(_PKG_DIR))

from diff_parser import analyze_diff  # noqa: E402
from response_processor import allowlist_original_matches, load_allowlist  # noqa: E402

# Keep in sync with .github/workflows/localization-quality-gate.yml
# LOCALIZATION_GATE_PATHSPECS (path prefixes + fnmatch-style globs).
WHITELIST_PREFIXES: tuple[str, ...] = (
    "apps/optix/ui/locales/lang",
    "apps/optix/ui/app/translations",
    "apps/central/central_web/src/locales/lang",
    "apps/central_client/src/locales/lang",
    "apps/digix_client/digix_client_ui/src/locales/lang",
    "apps/digix_client/digix_client_src/translations",
    "apps/report_tool/web/src/i18n/locales",
    "apps/cortex/ui/app/translations",
    "apps/smart-camera/frontend/src/i18n",
    "apps/production/production_src/translations_prod",
    "platform/boot_check/translations",
    "platform/upgrade_agent/app/i18n",
    "packages/standard_postprocess/translation",
    "packages/vision_engine/unitxvisionengine/dimensional/ui/translations.py",
)

WHITELIST_GLOBS: tuple[str, ...] = (
    "**/i18n.csv",
    "apps/x/**/resources/i18n/**",
    "**/translations_optix/**",
    "**/translations_backend/**",
    "**/translations_prod/**",
    "shared/config/**/translations/**",
    "**/translations*/english.py",
    "**/translations*/chinese.py",
    "**/translations*/portuguese.py",
    "**/translations*/english.js",
    "**/translations*/chinese.js",
    "**/translations*/portuguese.js",
    "**/locales/lang/english.ts",
    "**/locales/lang/chinese.ts",
    "**/locales/lang/portuguese.ts",
)

SKIP_PATH_RE = re.compile(
    r"(^|/)"
    r"(node_modules|vendor|dist|build|\.git|__pycache__|"
    r"select2|vditor|ueditor|"
    r"assets/vs/|"  # Monaco editor bundles
    r"\.min\.|"
    r"third_party/|"
    r"\.so$)",
    re.I,
)

# Bundled/public generated assets (not first-party UI copy)
SKIP_HARDCODED_PATH_RE = re.compile(
    r"(^|/)"
    r"("
    r"resources/public/|"
    r"static/|"
    r"assets/vendor/|"
    r"\.nls\.[a-z-]+\.js$|"
    r"tsWorker\.js$|"
    r"[0-9a-f]{8,}\.js$"  # webpack hashed bundles
    r")",
    re.I,
)

HARDCODED_SUFFIXES = frozenset({".py", ".tsx", ".jsx", ".vue", ".html", ".ts", ".js"})

# Prefer UI-ish / server paths for hardcoded round; still apply UI-like filter.
HARDCODED_PATH_HINT = re.compile(
    r"(^|/)(ui|frontend|web|client|server|src|app)(/|$)",
    re.I,
)

STRING_LITERAL_RE = re.compile(
    r'(""".*?"""|\'\'\'.*?\'\'\'|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')',
    re.S,
)

PLACEHOLDER_ONLY_RE = re.compile(r"^\s*(\{[^}]*\}|%\(?\w+\)?[\w.]*|\$\{[^}]*\})+\s*$")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")
LOG_PREFIX_RE = re.compile(
    r"^(debug|trace|info|warn(ing)?|error|exception|failed to |error |creating |"
    r"setting |loading |initializ|must wait|unexpected error during)\b",
    re.I,
)

BATCH_MAX_ITEMS = 80
BATCH_MAX_CHARS = 8_000


def _fnmatch_path(path: str, pattern: str) -> bool:
    import fnmatch

    return fnmatch.fnmatch(path, pattern)


def is_whitelist_path(path: str) -> bool:
    for prefix in WHITELIST_PREFIXES:
        if path == prefix or path.startswith(prefix.rstrip("/") + "/"):
            return True
    return any(_fnmatch_path(path, g) for g in WHITELIST_GLOBS)


def detect_lang(path: str, value: str) -> str:
    lower = path.lower()
    if any(
        x in lower
        for x in (
            "chinese",
            "/zh/",
            "_zh.",
            "zh-cn",
            "zh_hans",
            "zh_cn",
            ".zh.",
        )
    ):
        return "zh"
    if any(
        x in lower
        for x in (
            "portuguese",
            "brazil",
            "/pt/",
            "_pt.",
            "pt-br",
            "pt_br",
            ".pt.",
        )
    ):
        return "pt"
    if any(
        x in lower
        for x in ("english", "/en/", "_en.", "en-us", "en_us", "/en.", ".en.")
    ):
        return "en"
    if CJK_RE.search(value):
        return "zh"
    # latin with spaces / letters → treat as en for codespell
    if re.search(r"[A-Za-z]", value):
        return "en"
    return "und"


def git_ls_files(repo: Path) -> list[str]:
    out = subprocess.check_output(
        ["git", "ls-files", "-z"],
        cwd=repo,
        text=False,
    )
    return [p.decode("utf-8", "surrogateescape") for p in out.split(b"\0") if p]


def file_as_add_diff(rel_path: str, text: str) -> str:
    lines = text.splitlines()
    if not lines:
        return ""
    buf = [f"+++ b/{rel_path}", f"@@ -0,0 +1,{len(lines)} @@"]
    buf.extend(f"+{line}" for line in lines)
    return "\n".join(buf) + "\n"


def _records_from_analyze(
    details: dict[str, Any], rel_path: str
) -> list[dict[str, Any]]:
    """Recover VALUES from analyze_diff compact review_text."""
    review = details.get("review_text") or ""
    records: list[dict[str, Any]] = []
    current_file = rel_path
    current_line = -1
    header_re = re.compile(r"^\[(.+):(-?\d+)(?:\|[^\]]*)?\]\s*$")
    for line in review.splitlines():
        if m := header_re.match(line.strip()):
            current_file, current_line = m.group(1), int(m.group(2))
            continue
        raw = line.strip()
        if not raw:
            continue
        value = raw.replace("\\n", "\n").strip()
        if not value:
            continue
        records.append(
            {
                "file": current_file,
                "line": current_line,
                "value": value,
                "lang": detect_lang(current_file, value),
                "source": "whitelist",
            }
        )
    return _dedupe_records(records)


def extract_whitelist_records(repo: Path, rel_path: str) -> list[dict[str, Any]]:
    abs_path = repo / rel_path
    try:
        text = abs_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    diff = file_as_add_diff(rel_path, text)
    if not diff:
        return []
    return _records_from_analyze(analyze_diff(diff), rel_path)


def _unescape_literal(raw: str) -> str:
    if raw.startswith(('"""', "'''")):
        body = raw[3:-3]
    else:
        body = raw[1:-1]
    try:
        if raw.startswith('"'):
            return json.loads(f'"{body}"')
    except json.JSONDecodeError:
        pass
    return (
        body.replace(r"\n", "\n")
        .replace(r"\t", "\t")
        .replace(r"\'", "'")
        .replace(r"\"", '"')
        .replace(r"\\", "\\")
    )


def looks_ui_hardcoded(value: str) -> bool:
    s = value.strip()
    if len(s) < 4:
        return False
    if PLACEHOLDER_ONLY_RE.match(s):
        return False
    if s.startswith(("http://", "https://", "data:", "./", "../")):
        return False
    if re.fullmatch(r"[A-Za-z0-9_./#|:+\-\\]+", s) and " " not in s:
        return False  # path / id / enum
    if re.fullmatch(r"[A-Z][A-Z0-9_]{2,}", s):
        return False  # CONSTANT
    has_cjk = bool(CJK_RE.search(s))
    has_space = " " in s
    has_sentence = bool(re.search(r"[.!?。！？]", s))
    if not (has_cjk or has_space or has_sentence):
        return False
    # Drop obvious non-UI blobs
    if "\n" in s and ("def " in s or "self." in s or "return " in s):
        return False
    if len(s) > 500:
        return False
    return True


def extract_hardcoded_records(repo: Path, rel_path: str) -> list[dict[str, Any]]:
    abs_path = repo / rel_path
    try:
        text = abs_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    records: list[dict[str, Any]] = []
    # Map char offset → line number
    line_starts = [0]
    for i, ch in enumerate(text):
        if ch == "\n":
            line_starts.append(i + 1)

    def offset_to_line(off: int) -> int:
        lo, hi = 0, len(line_starts) - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if line_starts[mid] <= off:
                lo = mid + 1
            else:
                hi = mid - 1
        return hi + 1

    for m in STRING_LITERAL_RE.finditer(text):
        raw = m.group(0)
        # skip module docstrings at file start roughly
        value = _unescape_literal(raw).strip()
        if not looks_ui_hardcoded(value):
            continue
        line_no = offset_to_line(m.start())
        # skip import lines
        line_text = text[line_starts[line_no - 1] : m.start()]
        if re.search(r"\b(import|from)\b", line_text.split("\n")[-1]):
            continue
        records.append(
            {
                "file": rel_path,
                "line": line_no,
                "value": value,
                "lang": detect_lang(rel_path, value),
                "source": "hardcoded",
            }
        )
    return _dedupe_records(records)


def _dedupe_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[Any, ...]] = set()
    out: list[dict[str, Any]] = []
    for r in records:
        key = (r["file"], r["line"], r["value"])
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def value_hash(value: str) -> str:
    norm = " ".join(value.split())
    return hashlib.sha1(norm.encode("utf-8")).hexdigest()[:12]


def should_auto_pass(value: str, allow_set: set[str]) -> str | None:
    s = value.strip()
    if not s or len(s) < 3:
        return "too_short"
    if PLACEHOLDER_ONLY_RE.match(s):
        return "placeholder_only"
    if any(allowlist_original_matches(s, term) for term in allow_set if term):
        return "allowlist"
    if re.fullmatch(r"[\d\s.,:%+\-_/]+", s):
        return "numeric"
    return None


def run_codespell_on_values(values: list[str]) -> set[int]:
    """Return indices into `values` that codespell flags."""
    if not values:
        return set()
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        # one value per line; escape newlines
        mapping_path = td_path / "mapping.txt"
        check_path = td_path / "check.txt"
        lines: list[str] = []
        for i, v in enumerate(values):
            flat = v.replace("\n", " ").replace("\r", " ")
            lines.append(flat)
        check_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        mapping_path.write_text(
            "\n".join(str(i) for i in range(len(values))), encoding="utf-8"
        )
        try:
            proc = subprocess.run(
                [
                    "codespell",
                    str(check_path),
                    "--quiet-level",
                    "2",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            print(
                "WARN: codespell not found; English suspects will be empty",
                file=sys.stderr,
            )
            return set()
        flagged: set[int] = set()
        # codespell output: file:line: word ==> suggestion
        line_re = re.compile(r":(\d+):")
        for out_line in (proc.stdout or "").splitlines() + (
            proc.stderr or ""
        ).splitlines():
            m = line_re.search(out_line)
            if not m:
                continue
            # codespell line numbers are 1-based into check.txt
            idx = int(m.group(1)) - 1
            if 0 <= idx < len(values):
                flagged.add(idx)
        return flagged


def is_sentence_like(value: str) -> bool:
    s = value.strip()
    if len(s) < 3 or len(s) > 500:
        return False
    return bool(CJK_RE.search(s) or " " in s or re.search(r"[.!?。！？]", s))


def write_batches(
    suspects: list[dict[str, Any]],
    batch_dir: Path,
    *,
    prefix: str = "batch",
    title: str = "Review batch",
) -> int:
    batch_dir.mkdir(parents=True, exist_ok=True)
    for old in batch_dir.glob(f"{prefix}-*.md"):
        old.unlink()
    batch_idx = 1
    buf: list[str] = []
    chars = 0
    items = 0
    count_batches = 0

    def flush() -> None:
        nonlocal batch_idx, buf, chars, items, count_batches
        if not buf:
            return
        path = batch_dir / f"{prefix}-{batch_idx:03d}.md"
        header = (
            f"# {title} {batch_idx:03d}\n\n"
            f"Items: {items}. Check **spelling + grammar** (en/zh/pt). "
            f"For Cursor only after human confirm.\n\n"
        )
        path.write_text(header + "\n".join(buf) + "\n", encoding="utf-8")
        count_batches += 1
        batch_idx += 1
        buf, chars, items = [], 0, 0

    for rec in suspects:
        value_flat = rec["value"].replace("\n", "\\n")
        block = (
            f"[{rec['file']}:{rec['line']}]\n"
            f"{value_flat}\n"
            f"reason: {rec.get('suspect_reason', '')} | "
            f"lang: {rec.get('lang', '')} | source: {rec.get('source', '')}\n"
        )
        if items >= BATCH_MAX_ITEMS or (chars + len(block) > BATCH_MAX_CHARS and items):
            flush()
        buf.append(block)
        chars += len(block)
        items += 1
    flush()
    return count_batches


def build_review_queue(
    candidates: list[dict[str, Any]],
    *,
    source: str,
    flagged_hashes: set[str],
    all_records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Unique sentence-like values for spelling+grammar review (all langs)."""
    hash_count: dict[str, int] = defaultdict(int)
    for r in all_records:
        hash_count[r["value_hash"]] += 1

    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for r in candidates:
        if r["source"] != source:
            continue
        if r["lang"] not in ("en", "zh", "pt", "und"):
            continue
        if r["source"] == "hardcoded" and LOG_PREFIX_RE.match(r["value"].strip()):
            continue
        if not is_sentence_like(r["value"]):
            continue
        h = r["value_hash"]
        if h in seen:
            continue
        seen.add(h)
        rec = dict(r)
        tags = ["grammar_spell"]
        if h in flagged_hashes:
            tags.append("codespell")
        rec["suspect_reason"] = f"{'+'.join(tags)}; occurrences={hash_count[h]}"
        rec["_priority"] = 0 if h in flagged_hashes else 1
        out.append(rec)
    out.sort(key=lambda x: (x["_priority"], x["file"], x["line"]))
    for rec in out:
        rec.pop("_priority", None)
    return out


def build_files_index(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_file: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in records:
        by_file[r["file"]].append(r)
    rows: list[dict[str, Any]] = []
    for path, items in sorted(by_file.items()):
        lines = sorted({int(i["line"]) for i in items if int(i["line"]) > 0})
        rows.append(
            {
                "file": path,
                "value_count": len(items),
                "line_count": len(lines),
                "sources": ",".join(sorted({i["source"] for i in items})),
                "sample_lines": ",".join(str(x) for x in lines[:20]),
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path.cwd(),
        help="Repository root (default: cwd)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("tmp/l10n_scan"),
        help="Output directory",
    )
    args = parser.parse_args()
    repo = args.repo.resolve()
    out_dir = (repo / args.out).resolve() if not args.out.is_absolute() else args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    batch_dir = out_dir / "batches"

    allow = load_allowlist()
    allow_set = {str(x.get("original", "")) for x in allow if x.get("original")}

    all_files = git_ls_files(repo)
    whitelist_files = [
        f for f in all_files if is_whitelist_path(f) and not SKIP_PATH_RE.search(f)
    ]
    hardcoded_files = [
        f
        for f in all_files
        if not is_whitelist_path(f)
        and not SKIP_PATH_RE.search(f)
        and not SKIP_HARDCODED_PATH_RE.search(f)
        and Path(f).suffix in HARDCODED_SUFFIXES
        and HARDCODED_PATH_HINT.search(f)
        and f.startswith(("apps/", "packages/", "platform/"))
    ]

    records: list[dict[str, Any]] = []
    print(f"Whitelist files: {len(whitelist_files)}")
    for f in whitelist_files:
        records.extend(extract_whitelist_records(repo, f))

    print(f"Hardcoded candidate files: {len(hardcoded_files)}")
    for f in hardcoded_files:
        records.extend(extract_hardcoded_records(repo, f))

    records = _dedupe_records(records)
    for r in records:
        r["value_hash"] = value_hash(r["value"])

    # Full values
    values_path = out_dir / "values.jsonl"
    with values_path.open("w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    files_index = build_files_index(records)
    index_csv = out_dir / "files_index.csv"
    with index_csv.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(
            fh,
            fieldnames=["file", "value_count", "line_count", "sources", "sample_lines"],
        )
        w.writeheader()
        w.writerows(files_index)

    # Filter → review queues (spelling + grammar, all langs)
    passed = 0
    candidates: list[dict[str, Any]] = []
    for r in records:
        reason = should_auto_pass(r["value"], allow_set)
        if reason:
            passed += 1
            continue
        candidates.append(r)

    unique_for_spell: list[dict[str, Any]] = []
    seen_spell: set[str] = set()
    for r in candidates:
        h = r["value_hash"]
        if h in seen_spell:
            continue
        if r["lang"] not in ("en", "und"):
            continue
        if r["source"] == "hardcoded" and LOG_PREFIX_RE.match(r["value"].strip()):
            continue
        if not is_sentence_like(r["value"]):
            continue
        seen_spell.add(h)
        unique_for_spell.append(r)

    spell_values = [r["value"] for r in unique_for_spell]
    flagged_idx = run_codespell_on_values(spell_values)
    flagged_hashes = {unique_for_spell[i]["value_hash"] for i in flagged_idx}

    whitelist_queue = build_review_queue(
        candidates,
        source="whitelist",
        flagged_hashes=flagged_hashes,
        all_records=records,
    )
    hardcoded_queue = build_review_queue(
        candidates,
        source="hardcoded",
        flagged_hashes=flagged_hashes,
        all_records=records,
    )
    # Combined suspects for Cursor: whitelist first (primary UX copy), then hardcoded
    suspects = whitelist_queue + hardcoded_queue

    suspects_path = out_dir / "suspects.jsonl"
    with suspects_path.open("w", encoding="utf-8") as fh:
        for r in suspects:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    (out_dir / "suspects_whitelist.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in whitelist_queue),
        encoding="utf-8",
    )
    (out_dir / "suspects_hardcoded.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in hardcoded_queue),
        encoding="utf-8",
    )

    wl_batches = write_batches(
        whitelist_queue,
        out_dir / "batches_whitelist",
        prefix="wl",
        title="Whitelist spelling+grammar",
    )
    hc_batches = write_batches(
        hardcoded_queue,
        out_dir / "batches_hardcoded",
        prefix="hc",
        title="Hardcoded spelling+grammar",
    )
    # Convenience: batches/ mirrors whitelist (primary Cursor path)
    n_batches = write_batches(
        whitelist_queue,
        batch_dir,
        prefix="batch",
        title="Whitelist spelling+grammar",
    )

    def _lang_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
        c: dict[str, int] = defaultdict(int)
        for r in rows:
            c[r.get("lang") or "und"] += 1
        return dict(sorted(c.items()))

    wl_chars = sum(len(r["value"]) for r in whitelist_queue)
    hc_chars = sum(len(r["value"]) for r in hardcoded_queue)

    summary = {
        "whitelist_files": len(whitelist_files),
        "hardcoded_candidate_files": len(hardcoded_files),
        "files_with_values": len(files_index),
        "values_total": len(records),
        "auto_passed": passed,
        "review_mode": "spelling_and_grammar_all_langs",
        "suspects_total_unique": len(suspects),
        "suspects_whitelist_unique": len(whitelist_queue),
        "suspects_hardcoded_unique": len(hardcoded_queue),
        "whitelist_by_lang": _lang_counts(whitelist_queue),
        "hardcoded_by_lang": _lang_counts(hardcoded_queue),
        "codespell_flagged_unique": len(flagged_hashes),
        "batches_whitelist": wl_batches,
        "batches_hardcoded": hc_batches,
        "batches": n_batches,
        "approx_tokens_whitelist": wl_chars // 4,
        "approx_tokens_hardcoded": hc_chars // 4,
        "out_dir": str(out_dir),
        "status": "AWAITING_HUMAN_CONFIRM_BEFORE_CURSOR_REVIEW",
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    confirm_md = f"""# L10n stock scan — confirm before Cursor review

## Status

**未开始 Cursor 审查。** 本轮审查目标：**拼写 + 语法**，语言：**en / zh / pt**。

## Summary

| metric | count |
| --- | ---: |
| values (full) | {summary['values_total']} |
| auto-passed | {summary['auto_passed']} |
| **whitelist unique for review** | **{summary['suspects_whitelist_unique']}** |
| whitelist by lang | {summary['whitelist_by_lang']} |
| whitelist batches (`batches/` / `batches_whitelist/`) | {summary['batches_whitelist']} |
| whitelist ~tokens | {summary['approx_tokens_whitelist']} |
| hardcoded unique for review | {summary['suspects_hardcoded_unique']} |
| hardcoded by lang | {summary['hardcoded_by_lang']} |
| hardcoded batches | {summary['batches_hardcoded']} |
| hardcoded ~tokens | {summary['approx_tokens_hardcoded']} |
| codespell priority tags | {summary['codespell_flagged_unique']} |

## Policy

- 全量仍在 `values.jsonl`
- 送 Cursor 的是 **去重后的句子级 VALUE**（en/zh/pt），检查 **拼写+语法**
- codespell 命中的条目排在各队列前面（`reason` 含 `codespell`）
- 白名单与硬编码分开批；默认建议先审 `batches/`（白名单）

## Token note

纯 Cursor 审完白名单约 **{summary['batches_whitelist']}** 批 / **~{summary['approx_tokens_whitelist']}** token；
硬编码再约 **{summary['batches_hardcoded']}** 批。若只想先做白名单语法+多语言，确认时写明即可。

## Confirm checklist

- [ ] 同意审查目标：拼写 + 语法，en/zh/pt
- [ ] 先审白名单 `batches/`（从 batch-001）
- [ ] （可选）白名单完成后继续 `batches_hardcoded/`
- [ ] （可选）改用 Gemini 门禁批量审、Cursor 只看 HIGH（更省对话 token）

确认后回复例如：「确认，开始审 batch-001（仅白名单，拼写+语法）」
"""
    (out_dir / "CONFIRM.md").write_text(confirm_md, encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\nWrote {out_dir}")
    print("Stop: waiting for human confirm before Cursor review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
