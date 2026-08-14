#!/usr/bin/env python3
"""Whitelist-only typo scan (LOCALIZATION_GATE_PATHSPECS from localization-
quality-gate.yml).

Uses a custom typo dictionary + codespell on extracted VALUES.
Optionally reports KEY-name typos (does not rename keys unless --apply-keys).

Usage (repo root):
  python platform/devop/localization_quality_gate/stock_whitelist_typo_scan.py
  python platform/devop/localization_quality_gate/stock_whitelist_typo_scan.py --apply-values
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any

_PKG_DIR = Path(__file__).resolve().parent
if str(_PKG_DIR) not in sys.path:
    sys.path.insert(0, str(_PKG_DIR))

from stock_user_facing_scan import (  # noqa: E402
    SKIP_PATH_RE,
    extract_whitelist_records,
    git_ls_files,
    is_whitelist_path,
)

# VALUE typos frequently missed by short-token / compound filters.
VALUE_TYPO_PATTERNS: list[tuple[re.Pattern[str], str, str]] = [
    (re.compile(r"\bCencel\b"), "Cancel", "spelling"),
    (re.compile(r"\bGeneralTamplate\b"), "General Template", "spelling"),
    (re.compile(r"\bTamplate\b"), "Template", "spelling"),
    (re.compile(r"\bfailly\b"), "failed", "spelling"),
    (re.compile(r"\bFailly\b"), "Failed", "spelling"),
    (re.compile(r"\bRuning\b"), "Running", "spelling"),
    (re.compile(r"\bSucess\b"), "Success", "spelling"),
    (re.compile(r"\bsucess\b"), "success", "spelling"),
    (re.compile(r"\bSucessfully\b"), "Successfully", "spelling"),
    (re.compile(r"\bsucessfully\b"), "successfully", "spelling"),
    (re.compile(r"\btun ON\b"), "turn ON", "spelling"),
    (re.compile(r"\btun OFF\b"), "turn OFF", "spelling"),
    (re.compile(r"\bto recovery\b"), "to recover", "grammar"),
    (re.compile(r"\bis error\b"), "has an error", "grammar"),
    (re.compile(r"\bPleace\b"), "Please", "spelling"),
    (re.compile(r"\bDepoly\b"), "Deploy", "spelling"),
    (re.compile(r"\bInfered\b"), "Inferred", "spelling"),
    (re.compile(r"\binfered\b"), "inferred", "spelling"),
    (re.compile(r"\bnetwrok\b"), "network", "spelling"),
    (re.compile(r"\bVolumn\b"), "Volume", "spelling"),
    (re.compile(r"\bfuther\b"), "further", "spelling"),
    (re.compile(r"\bcharcters\b"), "characters", "spelling"),
    (re.compile(r"\bassigend\b"), "assigned", "spelling"),
    (re.compile(r"\bSuccessfuly\b"), "Successfully", "spelling"),
    (re.compile(r"\bcurrenly\b"), "currently", "spelling"),
    (re.compile(r"\bDetele\b"), "Delete", "spelling"),
    (re.compile(r"\bfileds\b"), "fields", "spelling"),
    (re.compile(r"\bfaild\b"), "failed", "spelling"),
    (re.compile(r"\bFaild\b"), "Failed", "spelling"),
    (re.compile(r"\bspecal\b"), "special", "spelling"),
    (re.compile(r"\bdeactive\b"), "deactivate", "spelling"),
    (re.compile(r"\bsuccessed\b"), "succeeded", "spelling"),
    (re.compile(r"\bSuccessed\b"), "Succeeded", "spelling"),
    (re.compile(r"\bappliction\b"), "application", "spelling"),
    (re.compile(r"\bmemery\b"), "memory", "spelling"),
    (re.compile(r"\boccured\b"), "occurred", "spelling"),
    (re.compile(r"\bseperator\b"), "separator", "spelling"),
    (re.compile(r"\bSeperator\b"), "Separator", "spelling"),
    (re.compile(r"\brecieve\b"), "receive", "spelling"),
    (re.compile(r"\bRecieve\b"), "Receive", "spelling"),
    (re.compile(r"\bavaliable\b"), "available", "spelling"),
    (re.compile(r"\bAvaliable\b"), "Available", "spelling"),
    (re.compile(r"\bparamter\b"), "parameter", "spelling"),
    (re.compile(r"\bParamter\b"), "Parameter", "spelling"),
    (re.compile(r"\bconfigration\b"), "configuration", "spelling"),
    (re.compile(r"\bthreshhold\b"), "threshold", "spelling"),
    (re.compile(r"\btreshold\b"), "threshold", "spelling"),
    (re.compile(r"\boverriden\b"), "overridden", "spelling"),
    (re.compile(r"\bRetreive\b"), "Retrieve", "spelling"),
    (re.compile(r"\bretreive\b"), "retrieve", "spelling"),
    (re.compile(r"\bexcpet\b"), "except", "spelling"),
    (re.compile(r"\bstandlone\b"), "standalone", "spelling"),
    (re.compile(r"\bhomogenous\b"), "homogeneous", "spelling"),
    (re.compile(r"\bconsituent\b"), "constituent", "spelling"),
    (re.compile(r"\bindividal\b"), "individual", "spelling"),
    (re.compile(r"\bcleanuped\b"), "cleaned up", "spelling"),
    (re.compile(r"\bproxys\b"), "proxies", "spelling"),
    (re.compile(r"\bReseting\b"), "Resetting", "spelling"),
    (re.compile(r"\b神经网路\b"), "神经网络", "spelling"),
    (re.compile(r"导c文件"), "导入文件", "spelling"),
    (re.compile(r"\b登陆\b"), "登录", "spelling"),
]

# KEY / identifier typos (report only; renaming needs call-site updates).
KEY_TYPO_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bSUCESS\b"), "SUCCESS"),
    (re.compile(r"CAPURE_"), "CAPTURE_"),
    (re.compile(r"(?<![A-Za-z])cencel(?![A-Za-z])"), "cancel"),
    (re.compile(r"(?<![A-Za-z])Tamplate(?![A-Za-z])"), "Template"),
    (re.compile(r"\bGeneralTamplate\b"), "GeneralTemplate"),
    (re.compile(r"\bdictionries\b"), "dictionaries"),
    (re.compile(r"(?<![A-Za-z])runing(?![A-Za-z])"), "running"),
]

PT_FALSE_POSITIVE = re.compile(
    r"\b(Nome|nome|Erro|erro|limite|atual|ser|fase|profissional|caracteres|OT)\b"
)


def scan_value_typos(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    seen: set[tuple[str, int, str]] = set()
    for r in records:
        value = r["value"]
        for pat, repl, kind in VALUE_TYPO_PATTERNS:
            if not pat.search(value):
                continue
            suggestion = pat.sub(repl, value)
            if suggestion == value:
                continue
            key = (r["file"], int(r["line"]), value)
            if key in seen:
                continue
            seen.add(key)
            issues.append(
                {
                    "file": r["file"],
                    "line": r["line"],
                    "original": value,
                    "suggestion": suggestion,
                    "problem": f"custom_dict:{kind}",
                    "severity": "high",
                    "lang": r.get("lang"),
                    "source": "whitelist",
                    "kind": "value",
                }
            )
            break
    return issues


def run_codespell(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    en = [
        r
        for r in records
        if r.get("lang") == "en"
        and not PT_FALSE_POSITIVE.search(r["value"])
        and len(r["value"].strip()) >= 3
    ]
    if not en:
        return []
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "en.txt"
        path.write_text(
            "\n".join(r["value"].replace("\n", " ") for r in en) + "\n",
            encoding="utf-8",
        )
        proc = subprocess.run(
            ["codespell", str(path), "--quiet-level", "2"],
            capture_output=True,
            text=True,
            check=False,
        )
    issues: list[dict[str, Any]] = []
    seen: set[tuple[str, int, str]] = set()
    line_re = re.compile(r":(\d+):\s*(.+)$")
    for out in (proc.stdout or "").splitlines():
        m = line_re.search(out)
        if not m:
            continue
        idx = int(m.group(1)) - 1
        if not (0 <= idx < len(en)):
            continue
        r = en[idx]
        detail = m.group(2).strip()
        # codespell: word ==> suggestion
        sug_m = re.search(r"==>\s*([A-Za-z][A-Za-z' -]*)", detail)
        suggestion = r["value"]
        if sug_m:
            wrong = detail.split("==>", 1)[0].strip().rstrip(":").split()[-1]
            right = sug_m.group(1).split(",")[0].strip()
            if wrong and right and wrong in r["value"]:
                suggestion = r["value"].replace(wrong, right, 1)
        key = (r["file"], int(r["line"]), r["value"])
        if key in seen:
            continue
        seen.add(key)
        issues.append(
            {
                "file": r["file"],
                "line": r["line"],
                "original": r["value"],
                "suggestion": suggestion,
                "problem": f"codespell:{detail}",
                "severity": "high",
                "lang": "en",
                "source": "whitelist",
                "kind": "value",
            }
        )
    return issues


KEY_LINE_RE = re.compile(
    r"""^\s*(?:export\s+)?(?:const\s+)?([A-Za-z_][\w]*)\s*[:=]|"""
    r"""^\s*([A-Za-z_][\w]*)\s*=\s*[\"']|"""
    r"""^\s*([A-Za-z_][\w]*)\s*:\s*[\"']"""
)


def scan_key_typos(repo: Path, files: list[str]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for rel in files:
        path = repo / rel
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for i, line in enumerate(lines, 1):
            # Only look at left-hand identifiers / object keys
            m = KEY_LINE_RE.match(line)
            if not m:
                continue
            key_name = next(g for g in m.groups() if g)
            for pat, repl in KEY_TYPO_PATTERNS:
                if pat.search(key_name):
                    issues.append(
                        {
                            "file": rel,
                            "line": i,
                            "original": key_name,
                            "suggestion": pat.sub(repl, key_name),
                            "problem": "key_typo",
                            "severity": "medium",
                            "lang": "id",
                            "source": "whitelist",
                            "kind": "key",
                            "context": line.strip()[:160],
                        }
                    )
                    break
    return issues


def apply_value_fixes(repo: Path, issues: list[dict[str, Any]]) -> int:
    by_file: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for iss in issues:
        if iss.get("kind") != "value":
            continue
        by_file[iss["file"]].append(iss)
    n = 0
    for rel, items in by_file.items():
        path = repo / rel
        text = path.read_text(encoding="utf-8")
        original = text
        # longer originals first
        for iss in sorted(items, key=lambda x: len(x["original"]), reverse=True):
            o, s = iss["original"], iss["suggestion"]
            if o in text and o != s:
                text = text.replace(o, s)
                n += 1
        if text != original:
            path.write_text(text, encoding="utf-8")
    return n


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path, default=Path("tmp/l10n_scan_whitelist"))
    parser.add_argument(
        "--apply-values",
        action="store_true",
        help="Apply VALUE typo replacements in-place",
    )
    args = parser.parse_args()
    repo = args.repo.resolve()
    out = args.out if args.out.is_absolute() else repo / args.out
    out.mkdir(parents=True, exist_ok=True)

    all_files = git_ls_files(repo)
    wl_files = [
        f for f in all_files if is_whitelist_path(f) and not SKIP_PATH_RE.search(f)
    ]
    print(f"Whitelist files: {len(wl_files)}")

    records: list[dict[str, Any]] = []
    for f in wl_files:
        records.extend(extract_whitelist_records(repo, f))
    print(f"Extracted values: {len(records)}")

    custom = scan_value_typos(records)
    codespell = run_codespell(records)
    # merge: prefer custom dict over codespell for same (file,line,original)
    merged: dict[tuple[Any, ...], dict[str, Any]] = {}
    for iss in codespell + custom:
        key = (iss["file"], iss["line"], iss["original"])
        merged[key] = iss
    value_issues = list(merged.values())
    key_issues = scan_key_typos(repo, wl_files)

    (out / "values_typo_issues.jsonl").write_text(
        "".join(json.dumps(i, ensure_ascii=False) + "\n" for i in value_issues),
        encoding="utf-8",
    )
    (out / "key_typo_issues.jsonl").write_text(
        "".join(json.dumps(i, ensure_ascii=False) + "\n" for i in key_issues),
        encoding="utf-8",
    )

    md = [
        "# Whitelist typo scan\n\n",
        f"Files: {len(wl_files)}  Values: {len(records)}\n\n",
        f"## VALUE issues: {len(value_issues)}\n\n",
    ]
    for i in sorted(value_issues, key=lambda x: (x["file"], x["line"])):
        md.append(
            f"- `{i['file']}:{i['line']}`: {i['original'][:90]!r} → {i['suggestion'][:90]!r} ({i['problem']})\n"
        )
    md.append(f"\n## KEY issues (report only): {len(key_issues)}\n\n")
    for i in sorted(key_issues, key=lambda x: (x["file"], x["line"])):
        md.append(
            f"- `{i['file']}:{i['line']}`: key {i['original']!r} → {i['suggestion']!r}\n"
        )
    (out / "REPORT.md").write_text("".join(md), encoding="utf-8")

    applied = 0
    if args.apply_values:
        applied = apply_value_fixes(repo, value_issues)
        print(f"Applied VALUE fixes: {applied}")

    summary = {
        "whitelist_files": len(wl_files),
        "values": len(records),
        "value_issues": len(value_issues),
        "key_issues": len(key_issues),
        "applied_values": applied,
        "out": str(out),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
