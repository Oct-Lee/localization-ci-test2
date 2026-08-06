"""Unit tests for platform/devop/localization_quality_gate/localization_quality_gate.py."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

_PACKAGE_DIR = Path(__file__).resolve().parent
_SCRIPT = _PACKAGE_DIR / "localization_quality_gate.py"
_SPEC = importlib.util.spec_from_file_location(
    "localization_quality_gate", _SCRIPT
)
assert _SPEC and _SPEC.loader
gate = importlib.util.module_from_spec(_SPEC)
sys.modules["localization_quality_gate"] = gate
_SPEC.loader.exec_module(gate)


@pytest.fixture(autouse=True)
def _reset_model_failover():
    gate.reset_model_failover_state()
    yield
    gate.reset_model_failover_state()


def _write(tmp_path: Path, name: str, content: str) -> Path:
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


# ----- Diff Parser -----


def test_parse_diff_empty():
    assert gate.parse_diff("") == ""
    assert gate.parse_diff("   \n") == ""


def test_parse_diff_deletions_only():
    diff = """\
diff --git a/apps/optix/ui/locales/lang/en.json b/apps/optix/ui/locales/lang/en.json
--- a/apps/optix/ui/locales/lang/en.json
+++ b/apps/optix/ui/locales/lang/en.json
@@ -1 +0,0 @@
-  "old": "removed"
"""
    assert gate.parse_diff(diff) == ""


def test_parse_diff_added_line_with_context():
    diff = """\
diff --git a/apps/optix/ui/locales/lang/en.json b/apps/optix/ui/locales/lang/en.json
--- a/apps/optix/ui/locales/lang/en.json
+++ b/apps/optix/ui/locales/lang/en.json
@@ -10,0 +11 @@
+  "camera_missing": "camera[{camera_id}] not Founded"
"""
    review = gate.parse_diff(diff)
    assert "camera[{camera_id}] not Founded" in review
    assert "[apps/optix/ui/locales/lang/en.json:11" in review
    assert "user_facing:" not in review
    assert "# file:" not in review


def test_analyze_diff_reports_add_delete_and_line_numbers():
    diff = """\
diff --git a/apps/optix/ui/locales/lang/en.json b/apps/optix/ui/locales/lang/en.json
--- a/apps/optix/ui/locales/lang/en.json
+++ b/apps/optix/ui/locales/lang/en.json
@@ -10,1 +10,2 @@
-  "old": "gone"
+  "old": "kept"
+  "camera_missing": "camera[{camera_id}] not Founded"
"""
    analyzed = gate.analyze_diff(diff)
    assert analyzed["files"] == [
        {
            "path": "apps/optix/ui/locales/lang/en.json",
            "added": 2,
            "deleted": 1,
        }
    ]
    assert "[apps/optix/ui/locales/lang/en.json:10" in analyzed["review_text"]
    assert "[apps/optix/ui/locales/lang/en.json:11" in analyzed["review_text"]


def test_analyze_diff_coalesces_multiline_key_value():
    diff = """\
diff --git a/translations/english.js b/translations/english.js
--- a/translations/english.js
+++ b/translations/english.js
@@ -10,0 +11,2 @@
+  COMPUTATIONAL_IMAGING_UNSAVED_SEQUENCE:
+    'Please save the changes to the Sequence first',
"""
    analyzed = gate.analyze_diff(diff)
    review = analyzed["review_text"]
    assert "[translations/english.js:12|" in review
    assert "Please save the changes to the Sequence first" in review
    assert "user_facing:" not in review
    assert "# key:" not in review
    # Bare key-only chunk should not appear (avoids "missing comma" FPs).
    assert "COMPUTATIONAL_IMAGING_UNSAVED_SEQUENCE:" not in review


def test_attach_locations_from_added_lines():
    issues = [
        {
            "original": "not Founded",
            "problem": "grammar",
            "suggestion": "not found",
            "severity": "high",
        }
    ]
    details = {
        "a.json": [{"line": 42, "text": '  "x": "not Founded"'}],
    }
    out = gate.attach_locations(issues, details)
    assert out[0]["file"] == "a.json"
    assert out[0]["line"] == 42


def test_attach_locations_does_not_overwrite_known_line():
    issues = [{
        "file": "a.json", "line": 99, "original": "not Founded",
        "problem": "grammar", "suggestion": "not found", "severity": "high",
    }]
    details = {"a.json": [{"line": 42, "text": '  "x": "not Founded"'}]}
    out = gate.attach_locations(issues, details)
    assert out[0]["line"] == 99


def test_attach_locations_skips_ambiguous_substring():
    issues = [{
        "original": "ok", "problem": "style", "suggestion": "OK", "severity": "low",
    }]
    details = {
        "a.json": [{"line": 1, "text": '  "a": "ok"'}],
        "b.json": [{"line": 2, "text": '  "b": "ok"'}],
    }
    out = gate.attach_locations(issues, details)
    assert "file" not in out[0]
    assert "line" not in out[0]


def test_parse_diff_multiple_files():
    diff = """\
diff --git a/a.json b/a.json
--- a/a.json
+++ b/a.json
@@ -1,0 +1 @@
+  "a": "hello"
diff --git a/b.json b/b.json
--- a/b.json
+++ b/b.json
@@ -1,0 +1 @@
+  "b": "world"
"""
    review = gate.parse_diff(diff)
    assert "[a.json:1" in review
    assert "[b.json:1" in review
    assert "hello" in review
    assert "world" in review


def test_parse_diff_ignores_metadata_lines_in_window():
    diff = """\
--- a/file.json
+++ b/file.json
@@ -0,0 +1 @@
+added line
"""
    review = gate.parse_diff(diff)
    assert "---" not in review
    assert "+++" not in review
    assert "@@" not in review
    assert "added line" in review


# ----- Result Parser / Validator -----


def test_strip_markdown_fence():
    raw = '```json\n{"has_issue": false, "issues": []}\n```'
    assert gate.strip_markdown_fence(raw) == '{"has_issue": false, "issues": []}'


def test_parse_model_json_valid():
    payload = {
        "has_issue": True,
        "issues": [
            {
                "original": "not Founded",
                "problem": "grammar",
                "suggestion": "not found",
                "severity": "HIGH",
            }
        ],
    }
    result = gate.parse_model_json(json.dumps(payload))
    assert result["has_issue"] is True
    assert result["issues"][0]["severity"] == "high"


def test_parse_model_json_with_fence():
    raw = '```json\n{"has_issue": false, "issues": []}\n```'
    result = gate.parse_model_json(raw)
    assert result == {"has_issue": False, "issues": []}


def test_validate_missing_fields():
    with pytest.raises(ValueError, match="has_issue"):
        gate.validate_result({"issues": []})


def test_validate_illegal_severity_dropped():
    result = gate.validate_result(
        {
            "has_issue": True,
            "issues": [
                {
                    "original": "x",
                    "problem": "y",
                    "suggestion": "z",
                    "severity": "critical",
                }
            ],
        }
    )
    assert result == {"has_issue": False, "issues": []}


def test_validate_mixed_malformed_keeps_valid_issues():
    result = gate.validate_result(
        {
            "has_issue": True,
            "issues": [
                {
                    "original": "ok text",
                    "problem": "grammar",
                    "suggestion": "OK text",
                    "severity": "high",
                },
                {
                    "original": "x",
                    "problem": "y",
                    "suggestion": "",
                    "severity": "high",
                },
                {
                    "original": "x",
                    "problem": "y",
                    "suggestion": "z",
                    "severity": "critical",
                },
            ],
        }
    )
    assert result["has_issue"] is True
    assert len(result["issues"]) == 1
    assert result["issues"][0]["original"] == "ok text"
    assert result["issues"][0]["severity"] == "high"


def test_validate_empty_suggestion_dropped_not_fail_closed():
    result = gate.validate_result(
        {
            "has_issue": True,
            "issues": [
                {
                    "original": "神经网路",
                    "problem": "wrong character",
                    "suggestion": "   ",
                    "severity": "high",
                }
            ],
        }
    )
    assert result == {"has_issue": False, "issues": []}


def test_validate_has_issue_consistency_false_with_issues():
    with pytest.raises(ValueError, match="has_issue=false"):
        gate.validate_result(
            {
                "has_issue": False,
                "issues": [
                    {
                        "original": "x",
                        "problem": "y",
                        "suggestion": "z",
                        "severity": "low",
                    }
                ],
            }
        )


def test_validate_empty_issues_ok():
    assert gate.validate_result({"has_issue": False, "issues": []}) == {
        "has_issue": False,
        "issues": [],
    }


def test_validate_has_issue_true_with_empty_issues_normalized():
    result = gate.validate_result({"has_issue": True, "issues": []})
    assert result["has_issue"] is False
    assert result["issues"] == []


# ----- Placeholder -----


def test_placeholders_consistent_pass():
    kept, dropped = gate.filter_placeholder_mismatches(
        [
            {
                "original": "camera[{camera_id}] not found",
                "problem": "ok",
                "suggestion": "camera[{camera_id}] not found",
                "severity": "low",
            }
        ]
    )
    assert len(kept) == 1
    assert dropped == []


def test_placeholders_mismatch_is_dropped_not_fatal():
    kept, dropped = gate.filter_placeholder_mismatches(
        [
            {
                "original": "个物料模拟失败:",
                "problem": "missing placeholder",
                "suggestion": "%d个物料模拟失败",
                "severity": "high",
            },
            {
                "original": "Failued to delete",
                "problem": "spelling",
                "suggestion": "Failed to delete",
                "severity": "high",
            },
        ]
    )
    assert len(dropped) == 1
    assert dropped[0]["original"] == "个物料模拟失败:"
    assert [i["original"] for i in kept] == ["Failued to delete"]


def test_placeholders_percent_and_dollar():
    assert gate.placeholders("hello %s ${name}") == {"%s", "${name}"}


def test_string_value_line_re_handles_escaped_quotes():
    m = gate.STRING_VALUE_LINE_RE.match(r'''  "He said \"hi\"",''')
    assert m is not None
    assert m.group(2) == r'He said \"hi\"'
    m2 = gate.STRING_VALUE_LINE_RE.match(r"  'it\'s ok',")
    assert m2 is not None
    assert m2.group(2) == r"it\'s ok"
    # Unescaped inner quote of the same kind must not over-match to trailing junk.
    assert gate.STRING_VALUE_LINE_RE.match('''  "a" + "b"''') is None


def test_escape_review_value_normalizes_crlf():
    assert gate._escape_review_value("a\r\nb\rc\nd") == r"a\nb\nc\nd"


def test_max_quota_retries_reduced():
    assert gate.MAX_QUOTA_RETRIES == 5


def test_normalize_issue_does_not_strip_value_whitespace():
    out = gate.normalize_issue_to_string_value(
        {
            "original": " {}【判定条件】",
            "suggestion": "{}【判定条件】",
            "problem": "leading space",
            "severity": "low",
        }
    )
    assert out["original"].startswith(" ")
    assert out["suggestion"] == "{}【判定条件】"
    # Bare KEY = still recovered without stripping VALUE-only originals.
    bare = gate.normalize_issue_to_string_value(
        {"original": "  MSG =", "suggestion": "hello", "problem": "x", "severity": "high"}
    )
    assert bare.get("_recover_original") is True
    assert bare.get("_key_name") == "MSG"
    assert bare["suggestion"] == "hello"


def test_placeholders_bare_braces():
    assert "{}" in gate.placeholders(" {}【判定条件】导致图像LIMIT。")
    kept, dropped = gate.filter_placeholder_mismatches(
        [
            {
                "original": " {}【判定条件】导致图像LIMIT。",
                "problem": "leading space",
                "suggestion": "{}【判定条件】导致图像LIMIT。",
                "severity": "low",
            },
            {
                "original": "后处理中【{}】问题",
                "problem": "removed placeholder",
                "suggestion": "后处理中问题",
                "severity": "high",
            },
        ]
    )
    assert len(kept) == 1
    assert kept[0]["original"].startswith(" ")
    assert len(dropped) == 1


def test_validate_result_preserves_value_whitespace():
    result = gate.validate_result(
        {
            "has_issue": True,
            "issues": [
                {
                    "original": " {}【判定条件】导致图像LIMIT。",
                    "problem": "Leading space",
                    "suggestion": "{}【判定条件】导致图像LIMIT。",
                    "severity": "low",
                }
            ],
        }
    )
    assert result["issues"][0]["original"].startswith(" ")
    assert result["issues"][0]["suggestion"] == "{}【判定条件】导致图像LIMIT。"


def test_dedupe_issues_from_overlap():
    details = {
        "a.py": [{"line": 1, "text": 'MSG = "not Founded"'}],
    }
    dup = {
        "file": "a.py",
        "line": 1,
        "original": "not Founded",
        "problem": "grammar",
        "suggestion": "not found",
        "severity": "high",
    }
    kept = gate.postprocess_issues([dup, dict(dup)], details)
    assert len(kept) == 1
    assert kept[0]["suggestion"] == "not found"


def test_dedupe_keeps_highest_severity():
    low = {
        "file": "a.py",
        "line": 1,
        "original": "Cencel",
        "problem": "style",
        "suggestion": "Cancel",
        "severity": "low",
    }
    high = {**low, "problem": "spelling", "severity": "high"}
    out = gate.dedupe_issues([low, high])
    assert len(out) == 1
    assert out[0]["severity"] == "high"
    # Order: first-seen key, severity upgraded in place.
    out2 = gate.dedupe_issues([high, low])
    assert len(out2) == 1
    assert out2[0]["severity"] == "high"


# ----- Severity Policy -----


def test_has_blocking_issues_only_high():
    assert gate.has_blocking_issues(
        [{"severity": "medium"}, {"severity": "low"}]
    ) is False
    assert gate.has_blocking_issues([{"severity": "high"}]) is True


def test_count_by_severity():
    counts = gate.count_by_severity(
        [
            {"severity": "high"},
            {"severity": "high"},
            {"severity": "medium"},
            {"severity": "low"},
        ]
    )
    assert counts == {"high": 2, "medium": 1, "low": 1}


# ----- Step Summary -----


def test_format_step_summary_contains_required_fields():
    md = gate.format_step_summary(
        status="FAILED",
        issues=[
            {
                "original": "Founded",
                "problem": "grammar",
                "suggestion": "Found",
                "severity": "high",
            }
        ],
        duration_sec=1.25,
    )
    assert "## Localization Quality Gate" in md
    assert "Status: FAILED" in md
    assert "High: 1" in md
    assert "Truncated:" not in md
    assert "chars_omitted" not in md
    assert "Founded" in md


def test_compute_effective_rpm_uses_start_spacing_not_wall():
    # Two starts 4.0s apart → exactly 15 RPM (limit), not ~20+ from wall throughput.
    assert gate.compute_effective_rpm(2, 100.0, 104.0) == pytest.approx(15.0)
    assert gate.compute_effective_rpm(5, 0.0, 16.0) == pytest.approx(15.0)
    assert gate.compute_effective_rpm(1, 0.0, 0.0) is None
    assert gate.compute_effective_rpm(2, 5.0, 5.0) is None


def test_format_usage_lines_highlights_rpm_rpd_tokens():
    stats = gate.empty_usage_stats()
    stats.update(
        {
            "requests": 47,
            "prompt_tokens": 79977,
            "candidates_tokens": 17232,
            "total_tokens": 97209,
            "chars_sent": 196857,
            "batches": 47,
            "files_reviewed": 4,
            "models_used": ["gemini-3.1-flash-lite"],
            "model_limits": {
                "gemini-3.1-flash-lite": {"rpm": 15, "rpd": 500, "tpm": 250000},
            },
            "rpm_limit": 15,
            "rpd_limit": 500,
            "min_interval_sec": 4.0,
            "wall_sec": 200.0,
            "effective_rpm": 14.1,
        }
    )
    lines = gate.format_usage_lines(stats)
    joined = "\n".join(lines)
    assert "RPM: 14.1/min effective (limit 15)" in joined
    assert "RPD: 47 this run (limit 500)" in joined
    assert "Tokens: total=97209 (prompt=79977, candidates=17232)" in joined
    assert "Requests: 47 on gemini-3.1-flash-lite" in joined
    md = gate.format_step_summary(
        status="PASSED", issues=[], duration_sec=200.0, usage_stats=stats,
    )
    assert "Token usage:" not in md
    assert "RPM: 14.1/min effective (limit 15)" in md
    assert "RPD: 47 this run (limit 500)" in md
    assert "Tokens: total=97209" in md
    # No duplicated Models / API requests / Review payload block
    assert md.count("RPM:") == 1
    assert "Models:" not in md
    assert "Review payload:" not in md


# ----- main() integration with mocks -----


def test_main_empty_diff_exit_0(tmp_path: Path):
    diff = _write(tmp_path, "empty.diff", "")
    assert gate.main([str(diff)]) == 0


def test_main_deletions_only_exit_0(tmp_path: Path):
    content = """\
--- a/x.json
+++ b/x.json
@@ -1 +0,0 @@
-removed
"""
    diff = _write(tmp_path, "del.diff", content)
    assert gate.main([str(diff)]) == 0


def test_main_missing_api_key_exit_1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    content = """\
+++ b/apps/optix/ui/locales/lang/en.json
@@ -0,0 +1 @@
+  "msg": "hello world"
"""
    diff = _write(tmp_path, "add.diff", content)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    assert gate.main([str(diff)]) == 1


def test_main_high_issue_exit_1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    content = """\
+++ b/apps/optix/ui/locales/lang/en.json
@@ -0,0 +1 @@
+  "msg": "camera[{camera_id}] not Founded"
"""
    diff = _write(tmp_path, "bad.diff", content)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    model_json = {
        "has_issue": True,
        "issues": [
            {
                "original": "camera[{camera_id}] not Founded",
                "problem": "Grammar error: Founded",
                "suggestion": "camera[{camera_id}] not found",
                "severity": "high",
            }
        ],
    }
    api_payload = {
        "candidates": [{"content": {"parts": [{"text": json.dumps(model_json)}]}}],
        "usageMetadata": {"totalTokenCount": 42},
    }

    with patch.object(gate, "call_gemini", return_value=(api_payload, 0.5)):
        assert gate.main([str(diff)]) == 1


def test_main_medium_only_exit_0(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    content = """\
+++ b/apps/optix/ui/locales/lang/en.json
@@ -0,0 +1 @@
+  "msg": "Please check the configuration"
"""
    diff = _write(tmp_path, "med.diff", content)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    model_json = {
        "has_issue": True,
        "issues": [
            {
                "original": "Please check the configuration",
                "problem": "Wording could be clearer",
                "suggestion": "Please verify the configuration",
                "severity": "medium",
            }
        ],
    }
    api_payload = {
        "candidates": [{"content": {"parts": [{"text": json.dumps(model_json)}]}}],
    }

    with patch.object(gate, "call_gemini", return_value=(api_payload, 0.2)):
        assert gate.main([str(diff)]) == 0


def test_main_fence_wrapped_response_ok(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    content = """\
+++ b/a.json
@@ -0,0 +1 @@
+  "ok": "fine"
"""
    diff = _write(tmp_path, "ok.diff", content)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    fenced = '```json\n{"has_issue": false, "issues": []}\n```'
    api_payload = {
        "candidates": [{"content": {"parts": [{"text": fenced}]}}],
    }
    with patch.object(gate, "call_gemini", return_value=(api_payload, 0.1)):
        assert gate.main([str(diff)]) == 0


def test_filter_allowlisted_by_original_and_optional_file():
    entries = [
        {"original": "KeepThis"},
        {"file": "translations/chinese.js", "original": "神经网路"},
    ]
    issues = [
        {
            "file": "apps/optix/ui/locales/lang/english.ts",
            "original": "KeepThis",
            "problem": "casing",
            "suggestion": "Keep this",
            "severity": "high",
        },
        {
            "file": "apps/foo/translations/chinese.js",
            "original": "神经网路",
            "problem": "typo",
            "suggestion": "神经网络",
            "severity": "high",
        },
        {
            "file": "translations/english.py",
            "original": "神经网路",
            "problem": "typo",
            "suggestion": "神经网络",
            "severity": "high",
        },
        {
            "file": "x.py",
            "original": "Other",
            "problem": "x",
            "suggestion": "y",
            "severity": "high",
        },
    ]
    kept, dropped = gate.filter_allowlisted(issues, entries)
    assert len(dropped) == 2
    assert {d["original"] for d in dropped} == {"KeepThis", "神经网路"}
    assert len(kept) == 2
    assert kept[0]["file"] == "translations/english.py"
    assert kept[1]["original"] == "Other"


def test_load_allowlist_and_postprocess(tmp_path: Path):
    allow = tmp_path / "allowlist.json"
    allow.write_text(
        json.dumps([{"file": "translations/chinese.js", "original": "神经网路"}]),
        encoding="utf-8",
    )
    assert gate.load_allowlist(allow) == [
        {"original": "神经网路", "file": "translations/chinese.js"},
    ]
    details = {
        "translations/chinese.js": [{"line": 11, "text": 'FOO = "神经网路"'}],
    }
    issues = [
        {
            "file": "translations/chinese.js",
            "line": 11,
            "original": "神经网路",
            "problem": "wrong char",
            "suggestion": "神经网络",
            "severity": "high",
        }
    ]
    with patch.object(gate, "load_allowlist", return_value=gate.load_allowlist(allow)):
        kept = gate.postprocess_issues(issues, details)
    assert kept == []


def test_main_placeholder_tamper_dropped_not_blocking(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    """Inventing/removing placeholders drops the issue; gate does not fail-closed."""
    content = """\
+++ b/a.json
@@ -0,0 +1 @@
+  "msg": "id={camera_id}"
"""
    diff = _write(tmp_path, "ph.diff", content)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    model_json = {
        "has_issue": True,
        "issues": [
            {
                "original": "id={camera_id}",
                "problem": "style",
                "suggestion": "id=camera",
                "severity": "high",
            }
        ],
    }
    api_payload = {
        "candidates": [{"content": {"parts": [{"text": json.dumps(model_json)}]}}],
    }
    with patch.object(gate, "call_gemini", return_value=(api_payload, 0.1)):
        assert gate.main([str(diff)]) == 0
    captured = capsys.readouterr()
    out = json.loads(captured.out)
    assert out["issues"] == []
    assert "placeholder mismatch" in captured.err.lower()


def test_main_writes_step_summary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    summary_path = tmp_path / "summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary_path))
    diff = _write(tmp_path, "empty.diff", "")
    assert gate.main([str(diff)]) == 0
    text = summary_path.read_text(encoding="utf-8")
    assert "Localization Quality Gate" in text
    assert "PASSED" in text
    out = json.loads(capsys.readouterr().out)
    assert out == {"has_issue": False, "issues": [], "files": []}


def test_main_stdout_is_schema_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
):
    content = """\
+++ b/apps/optix/ui/locales/lang/en.json
@@ -0,0 +1 @@
+  "msg": "camera[{camera_id}] not Founded"
"""
    diff = _write(tmp_path, "bad.diff", content)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    model_json = {
        "has_issue": True,
        "issues": [
            {
                "original": "camera[{camera_id}] not Founded",
                "problem": "Grammar error: Founded",
                "suggestion": "camera[{camera_id}] not found",
                "severity": "high",
            }
        ],
    }
    api_payload = {
        "candidates": [{"content": {"parts": [{"text": json.dumps(model_json)}]}}],
    }
    with patch.object(gate, "call_gemini", return_value=(api_payload, 0.5)):
        assert gate.main([str(diff)]) == 1
    captured = capsys.readouterr()
    out = json.loads(captured.out)
    assert out["has_issue"] is True
    assert out["issues"][0]["severity"] == "high"
    assert out["issues"][0]["original"] == "camera[{camera_id}] not Founded"
    assert out["issues"][0]["file"] == "apps/optix/ui/locales/lang/en.json"
    assert out["issues"][0]["line"] == 1
    assert out["files"][0]["path"] == "apps/optix/ui/locales/lang/en.json"
    assert out["files"][0]["added"] == 1
    assert "Diff scope:" in captured.err
    assert "### Issues" not in captured.out
    assert "### Issues" not in captured.err



def test_call_gemini_retries_on_429(monkeypatch: pytest.MonkeyPatch):
    sleeps: list[float] = []
    monkeypatch.setattr(gate.time, "sleep", lambda s: sleeps.append(s))
    ok = MagicMock()
    ok.status_code = 200
    ok.json.return_value = {"candidates": [{"content": {"parts": [{"text": "{}"}]}}]}
    busy = MagicMock()
    busy.status_code = 429
    busy.text = (
        "Quota exceeded for metric: generate_content_free_tier_input_token_count, "
        "limit: 250000. Please retry in 41.5s."
    )
    busy.headers = {}

    with patch.object(
        gate.requests, "post", side_effect=[busy, ok]
    ) as post:
        payload, _duration = gate.call_gemini("key", "prompt")
        assert payload["candidates"]
        assert post.call_count == 2
        assert gate.GEMINI_MODELS[0] in post.call_args_list[0].args[0]
        assert "?key=" not in post.call_args_list[0].args[0]
        assert post.call_args_list[0].kwargs["headers"]["x-goog-api-key"] == "key"
    assert sleeps and sleeps[0] == 41.5


def test_call_gemini_daily_quota_failsover_to_next(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(gate.time, "sleep", lambda _: None)
    busy = MagicMock()
    busy.status_code = 429
    busy.text = "Quota exceeded for metric: generate_content_free_tier_requests per day"
    busy.headers = {}
    ok = MagicMock()
    ok.status_code = 200
    ok.json.return_value = {"candidates": [{"content": {"parts": [{"text": "{}"}]}}]}
    with patch.object(
        gate.requests, "post", side_effect=[busy, ok]
    ) as post:
        payload, _duration = gate.call_gemini("key", "prompt")
        assert payload["candidates"]
        assert post.call_count == 2
        assert gate.GEMINI_MODELS[0] in post.call_args_list[0].args[0]
        assert gate.GEMINI_MODELS[1] in post.call_args_list[1].args[0]
        assert post.call_args_list[1].kwargs["headers"]["x-goog-api-key"] == "key"
    assert gate.active_model_id() == gate.GEMINI_MODELS[1]


def test_call_gemini_daily_quota_all_models_fails(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(gate.time, "sleep", lambda _: None)
    busy = MagicMock()
    busy.status_code = 429
    busy.text = "Quota exceeded for metric: generate_content_free_tier_requests per day"
    busy.headers = {}
    with patch.object(gate.requests, "post", return_value=busy) as post:
        with pytest.raises(RuntimeError, match="all models"):
            gate.call_gemini("key", "prompt")
        assert post.call_count == len(gate.GEMINI_MODELS)


def test_gemini_model_quota_chain():
    assert len(gate.GEMINI_MODELS) >= 2
    assert gate.GEMINI_MODELS[0] == "gemini-3.1-flash-lite"
    assert gate.GEMINI_MODELS[1] == "gemini-3.5-flash-lite"
    assert "gemini-3-flash-preview" in gate.GEMINI_MODELS
    assert "gemini-3.6-flash" in gate.GEMINI_MODELS
    by_id = {q.model_id: q for q in gate.GEMINI_MODEL_QUOTAS}
    assert by_id["gemini-3.5-flash-lite"].rpm == 15
    assert by_id["gemini-3.5-flash-lite"].rpd == 500
    assert by_id["gemini-3-flash-preview"].rpm == 5
    assert by_id["gemini-3-flash-preview"].rpd == 20
    assert by_id["gemini-3.6-flash"].rpm == 5
    assert by_id["gemini-3.6-flash"].tpm == 250_000
    assert all(q.tpm == 250_000 for q in gate.GEMINI_MODEL_QUOTAS)
    assert abs(gate.min_request_interval_sec(5) - 12.0) < 1e-6
    assert abs(gate.min_request_interval_sec(15) - 4.0) < 1e-6


def test_call_gemini_503_failsover_to_next(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(gate.time, "sleep", lambda _: None)
    busy = MagicMock()
    busy.status_code = 503
    busy.text = (
        '{"error":{"code":503,"message":"This model is currently experiencing high demand.",'
        '"status":"UNAVAILABLE"}}'
    )
    ok = MagicMock()
    ok.status_code = 200
    ok.json.return_value = {"candidates": [{"content": {"parts": [{"text": "{}"}]}}]}
    # Exhaust primary (MAX_ATTEMPTS × 503), then succeed on next model.
    side_effect = [busy] * gate.MAX_ATTEMPTS + [ok]
    with patch.object(gate.requests, "post", side_effect=side_effect) as post:
        payload, _duration = gate.call_gemini("key", "prompt")
        assert payload["candidates"]
        assert post.call_count == gate.MAX_ATTEMPTS + 1
        assert gate.GEMINI_MODELS[0] in post.call_args_list[0].args[0]
        assert gate.GEMINI_MODELS[1] in post.call_args_list[-1].args[0]
    assert gate.active_model_id() == gate.GEMINI_MODELS[1]


def test_call_gemini_fail_closed_on_persistent_503(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(gate.time, "sleep", lambda _: None)
    busy = MagicMock()
    busy.status_code = 503
    busy.text = "unavailable"
    with patch.object(gate.requests, "post", return_value=busy) as post:
        with pytest.raises(RuntimeError, match="all models"):
            gate.call_gemini("key", "prompt")
        assert post.call_count == len(gate.GEMINI_MODELS) * gate.MAX_ATTEMPTS


def test_call_gemini_non_retryable_400():
    bad = MagicMock()
    bad.status_code = 400
    bad.text = "bad request"
    with patch.object(gate.requests, "post", return_value=bad):
        with pytest.raises(RuntimeError, match="400"):
            gate.call_gemini("key", "prompt")


def test_call_gemini_timeout_retries(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(gate.time, "sleep", lambda _: None)
    with patch.object(
        gate.requests, "post", side_effect=requests.Timeout("boom")
    ):
        with pytest.raises(RuntimeError, match="timeout"):
            gate.call_gemini("key", "prompt")


def test_analyze_diff_groups_review_by_file():
    diff = """\
diff --git a/translations/chinese.py b/translations/chinese.py
+++ b/translations/chinese.py
@@ -0,0 +1 @@
+X = "神经网路"
diff --git a/translations/english.py b/translations/english.py
+++ b/translations/english.py
@@ -0,0 +1 @@
+Y = "not Founded"
"""
    analyzed = gate.analyze_diff(diff)
    by_file = analyzed["review_by_file"]
    assert set(by_file) == {
        "translations/chinese.py",
        "translations/english.py",
    }
    assert "神经网路" in by_file["translations/chinese.py"]
    assert "not Founded" in by_file["translations/english.py"]


def test_split_into_batches_respects_limit():
    chunk = "# file: a.py\n# line: 1\nuser_facing: hello"
    text = "\n\n".join([chunk] * 10)
    limit = len(chunk) * 3 + 5
    batches = gate.split_into_batches(text, limit=limit)
    assert len(batches) >= 3
    assert all(len(b) <= limit for b in batches)
    for piece in text.split("\n\n"):
        assert any(piece in b for b in batches)


def test_split_into_batches_hard_splits_oversized_single_chunk():
    huge = "x" * 500
    batches = gate.split_into_batches(huge, limit=100)
    assert all(len(b) <= 100 for b in batches)
    assert len(batches) == 5
    # No silent drop of the payload characters (overlap may duplicate edges).
    assert all(set(b) <= {"x"} for b in batches)
    assert sum(b.count("x") for b in batches) >= 500


def test_split_into_batches_prefers_newline_breaks():
    lines = [f"line-{i:02d}-" + ("a" * 20) for i in range(10)]
    text = "\n".join(lines)
    limit = 80
    batches = gate.split_into_batches(text, limit=limit)
    assert all(len(b) <= limit for b in batches)
    for line in lines:
        assert any(line in b for b in batches)
    assert any(b.endswith("\n") or "\n" in b for b in batches[:-1])


def test_review_by_file_sessions_calls_once_per_file(
    monkeypatch: pytest.MonkeyPatch,
):
    review_by_file = {
        "translations/chinese.py": "# file: translations/chinese.py\nuser_facing: 神经网路",
        "translations/english.py": "# file: translations/english.py\nuser_facing: not Founded",
    }
    calls: list[str] = []

    def fake_gemini(_key: str, prompt: str):
        calls.append(prompt)
        # Match the review payload, not examples inside the static prompt template.
        if "user_facing: 神经网路" in prompt:
            body = {
                "has_issue": True,
                "issues": [
                    {
                        "original": "神经网路",
                        "problem": "spelling",
                        "suggestion": "神经网络",
                        "severity": "high",
                    }
                ],
            }
        else:
            body = {
                "has_issue": True,
                "issues": [
                    {
                        "original": "not Founded",
                        "problem": "grammar",
                        "suggestion": "not found",
                        "severity": "high",
                    }
                ],
            }
        return (
            {"candidates": [{"content": {"parts": [{"text": json.dumps(body)}]}}]},
            0.1,
        )

    monkeypatch.setattr(gate, "call_gemini", fake_gemini)
    monkeypatch.setattr(gate.time, "sleep", lambda _s: None)
    issues, _dur, stats = gate.review_by_file_sessions("k", review_by_file)
    assert len(calls) == 2
    assert stats["requests"] == 2
    assert stats["files_reviewed"] == 2
    assert {i["original"] for i in issues} == {"神经网路", "not Founded"}
    assert {i["file"] for i in issues} == {
        "translations/chinese.py",
        "translations/english.py",
    }


def test_whitespace_style_forced_low_and_original_recovered():
    details = {
        "translations/chinese.py": [
            {
                "line": 871,
                "text": 'LIMIT_NORMAL_DEFECT_REASON = " {}【判定条件】导致图像LIMIT。"',
            },
            {
                "line": 873,
                "text": 'LIMIT_POST_PROCESS_DEFECT_REASON = " 后处理中【{}】问题导致图像LIMIT。"',
            },
        ]
    }
    raw = [
        {
            "file": "translations/chinese.py",
            "line": 871,
            "original": "LIMIT_NORMAL_DEFECT_REASON =",
            "problem": "Leading space in translated string value",
            "suggestion": "{}【判定条件】导致图像LIMIT。",
            "severity": "high",
        },
        {
            "file": "translations/chinese.py",
            "line": 873,
            "original": "LIMIT_POST_PROCESS_DEFECT_REASON =",
            "problem": "Leading space in translated string value",
            "suggestion": "后处理中【{}】问题导致图像LIMIT。",
            "severity": "high",
        },
    ]
    kept = gate.postprocess_issues(raw, details)
    assert len(kept) == 2
    by_line = {i["line"]: i for i in kept}
    assert by_line[871]["severity"] == "low"
    assert by_line[871]["original"] == " {}【判定条件】导致图像LIMIT。"
    assert by_line[871]["suggestion"] == "{}【判定条件】导致图像LIMIT。"
    assert by_line[873]["severity"] == "low"
    assert by_line[873]["original"] == " 后处理中【{}】问题导致图像LIMIT。"
    assert "LIMIT_" not in by_line[871]["original"]
    assert "LIMIT_" not in by_line[873]["original"]


def test_build_prompt_covers_required_rules():
    prompt = gate.build_prompt("+ hello")
    assert "Localization Quality Reviewer" in prompt
    assert "English" in prompt
    assert "Simplified Chinese" in prompt
    assert "Portuguese" in prompt
    assert "[file:line]" in prompt
    assert "VALUE only" in prompt
    assert "placeholders" in prompt.lower()
    assert "whitespace" in prompt.lower()
    assert "severity" in prompt
    assert "Chinese character mistakes" in prompt
    assert "wrong characters" in prompt
    assert "incorrect word usage" in prompt
    assert "CJK" not in prompt
    assert "Chinese wrong characters" not in prompt
    assert "+ hello" in prompt
    assert "PR changes to review:" in prompt
    # No concrete seed examples (avoid anchoring / token waste).
    assert "Examples:" not in prompt
    assert "神经网路" not in prompt
    assert "FILE_CAMERA_NOT_SELECT" not in prompt
    assert "FLEX_LIGNT" not in prompt
    assert len(prompt) < 2000


def test_analyze_diff_python_triple_quoted_string():
    py_diff = '''\
+++ b/translations/english.py
@@ -1,0 +1,4 @@
+HELP_TEXT = """
+Select the camra before continuing.
+Then press Start.
+"""
'''
    review = gate.analyze_diff(py_diff)["review_text"]
    assert "[translations/english.py:" in review
    # Multiline VALUE uses \\n escape (one physical line under the header).
    assert "Select the camra before continuing.\\nThen press Start." in review
    assert "Select the camra before continuing.\nThen press Start." not in review
    assert "user_facing:" not in review
    assert "# file:" not in review

    one_line = '''\
+++ b/translations/english.py
@@ -1,0 +1 @@
+HINT = """Select the camra"""
'''
    one = gate.analyze_diff(one_line)["review_text"]
    assert "Select the camra" in one
    assert "[translations/english.py:" in one
    assert "user_facing:" not in one


def test_peek_triple_quoted_skip_contract():
    lines = [
        '+++ b/t.py',
        '@@ -1,0 +1,3 @@',
        '+MSG = """',
        '+hello',
        '+"""',
    ]
    skip, value, first = gate._peek_triple_quoted_string(lines, 2, '"""', "")
    assert skip == [3, 4]
    assert 2 not in skip  # opener owned by caller
    assert first == 3
    assert value == "hello"

    skip2, value2, first2 = gate._peek_triple_quoted_string(
        ['+HINT = """Select the camra"""'], 0, '"""', 'Select the camra"""',
    )
    # one-liner: no further lines to skip
    assert skip2 == []
    assert first2 == 0
    assert value2 == "Select the camra"


def test_split_into_batches_keeps_chunk_boundaries():
    c1 = "# file: a.py\n# line: 1\nuser_facing: hello one"
    c2 = "# file: a.py\n# line: 2\nuser_facing: hello two"
    text = f"{c1}\n\n{c2}"
    batches = gate.split_into_batches(text, limit=len(c1) + 10)
    assert len(batches) == 2
    assert batches[0] == c1
    assert batches[1] == c2


def test_pace_after_failover_uses_new_model_interval(monkeypatch: pytest.MonkeyPatch):
    sleeps: list[float] = []
    monkeypatch.setattr(gate.time, "sleep", lambda s: sleeps.append(s))
    gate.reset_model_failover_state()
    assert gate.try_advance_model("test")
    gate.pace_after_model_failover()
    assert sleeps
    assert sleeps[-1] == pytest.approx(gate.min_request_interval_sec(), rel=1e-3)


def test_assert_generation_complete_rejects_max_tokens():
    with pytest.raises(ValueError, match="finishReason"):
        gate.assert_generation_complete({
            "candidates": [{"finishReason": "MAX_TOKENS", "content": {"parts": [{"text": "{}"}]}}],
        })


def test_with_batch_continuation_header():
    cont = gate.with_batch_continuation_header("a.py", "mid chunk without header", batch_index=1)
    assert cont == "[a.py]\n\nmid chunk without header"
    assert "# file:" not in cont
    assert "# note:" not in cont
    # Already compact — do not add legacy or duplicate headers.
    already = "[a.py:10]\nhello"
    assert gate.with_batch_continuation_header("a.py", already, batch_index=1) == already
    assert gate.with_batch_continuation_header("a.py", already, batch_index=0) == already


def test_prefers_focused_batches_for_chinese_and_short_files():
    assert gate.prefers_focused_batches(
        "translations/chinese.py",
        "# file: translations/chinese.py\nuser_facing: x",
    )
    assert gate.prefers_focused_batches(
        "locales/pt_br/messages.py",
        "# file: locales/pt_br/messages.py\nuser_facing: x",
    )
    # Large English pack: stay packed unless path is focused.
    big = "\n\n".join(
        f"# file: translations/english.py\n# line: {i}\nuser_facing: value-{i}"
        for i in range(50)
    )
    assert not gate.prefers_focused_batches("translations/english.py", big)
    # Short non-locale file still gets focused review.
    short = "# file: app/ui_strings.py\nuser_facing: Hello woord"
    assert gate.prefers_focused_batches("app/ui_strings.py", short)


def test_focused_max_chunks_per_batch_targets_1_to_3_requests():
    assert gate.focused_max_chunks_per_batch(1) == 1
    assert gate.focused_max_chunks_per_batch(2) == 2  # → 1 request
    assert gate.focused_max_chunks_per_batch(3) == 2  # → 2 requests
    assert gate.focused_max_chunks_per_batch(18) == 9  # → 2 requests
    assert gate.focused_max_chunks_per_batch(5) == 3   # → 2 requests
    assert gate.FOCUSED_TARGET_BATCHES == 2


def test_split_into_batches_focused_packs_to_target_requests():
    chunks = [
        f"# file: translations/chinese.py\n# line: {i}\nuser_facing: v{i}"
        for i in range(18)
    ]
    text = "\n\n".join(chunks)
    pack = gate.focused_max_chunks_per_batch(18)
    batches = gate.split_into_batches(text, max_chunks_per_batch=pack)
    assert pack == 9
    assert len(batches) == 2
    assert all(len(gate.review_chunks(b)) <= 9 for b in batches)


def test_review_by_file_sessions_focused_packs_small_file(
    monkeypatch: pytest.MonkeyPatch,
):
    c1 = "# file: translations/chinese.py\n# line: 1\nuser_facing: 神经网路"
    c2 = "# file: translations/chinese.py\n# line: 6\nuser_facing: 导c文件"
    review_by_file = {"translations/chinese.py": f"{c1}\n\n{c2}"}
    calls: list[str] = []

    def fake_gemini(_key: str, prompt: str):
        calls.append(prompt)
        body = {
            "has_issue": True,
            "issues": [{
                "original": "已经加入训练序列，前面还有%d个神经网路",
                "problem": "spelling",
                "suggestion": "已经加入训练序列，前面还有%d个神经网络",
                "severity": "high",
            }],
        }
        return (
            {"candidates": [{"content": {"parts": [{"text": json.dumps(body)}]}}]},
            0.05,
        )

    monkeypatch.setattr(gate, "call_gemini", fake_gemini)
    monkeypatch.setattr(gate.time, "sleep", lambda _s: None)
    issues, _dur, stats = gate.review_by_file_sessions("k", review_by_file)
    # 2 chunks ≤ FOCUSED_TARGET_BATCHES → single request
    assert len(calls) == 1
    assert stats["batches"] == 1
    assert stats["requests"] == 1
    assert "神经网路" in calls[0] and "导c文件" in calls[0]
    assert any("神经网路" in i["original"] for i in issues)


def test_analyze_diff_neighbor_context_keeps_overlapping_views():
    """Compact VALUE entries still carry file/line; typo VALUE is present once."""
    diff = """\
+++ b/translations/chinese.py
@@ -8,0 +8,4 @@
+TRAINING_IN_LOCAL_MODE = "本机"
+TRAINING_IN_REMOTE_MODE = "多GPU机"
+TRAINING_IN_PROGRESS = "正在训练"
+TRAIN_SCHEDULED = "已经加入训练序列，前面还有%d个神经网路"
"""
    review = gate.analyze_diff(diff)["review_text"]
    assert "已经加入训练序列，前面还有%d个神经网路" in review
    assert "[translations/chinese.py:11|TRAIN_SCHEDULED]" in review
    assert "user_facing:" not in review
    # No neighbor duplication: typo appears in its own entry only.
    assert review.count("神经网路") == 1
    assert gate.CONTEXT_LINES == 1
    assert gate.FOCUSED_TARGET_BATCHES == 2
    assert gate.MAX_REVIEW_CHARS == 100_000


def test_postprocess_does_not_inject_hardcoded_typos():
    details = {
        "translations/chinese.py": [
            {
                "line": 11,
                "text": 'TRAIN_SCHEDULED = "已经加入训练序列，前面还有%d个神经网路"',
            }
        ]
    }
    assert gate.postprocess_issues([], details) == []


def test_analyze_diff_python_multiline_and_json_csv_hints():
    py_diff = """\
+++ b/apps/optix/optix_src/server/translations_optix/english.py
@@ -1,0 +1,3 @@
+ERROR_NO_CAMERA_DETECTED = (
+    "No camera with id {} detected."
+)
"""
    review = gate.analyze_diff(py_diff)["review_text"]
    assert "No camera with id {} detected." in review
    assert "[apps/optix/optix_src/server/translations_optix/english.py:" in review
    assert "user_facing:" not in review

    json_diff = """\
+++ b/apps/report_tool/web/src/i18n/locales/en.json
@@ -1,0 +1 @@
+    "confirm": "Confim",
"""
    assert "Confim" in gate.analyze_diff(json_diff)["review_text"]

    csv_diff = """\
+++ b/apps/x/central-web/src/assets/i18n.csv
@@ -1,0 +1 @@
+login.button,登录,Logn,Login
"""
    csv_review = gate.analyze_diff(csv_diff)["review_text"]
    assert "Logn" in csv_review
    assert "|login.button]" in csv_review


def test_parse_i18n_csv_row_preserves_quoted_commas():
    row = gate.parse_i18n_csv_row(
        'login.idle,超时,"Your session expired, please log in","Sessão expirou, faça login"'
    )
    assert row is not None
    key, values = row
    assert key == "login.idle"
    assert values == [
        "超时",
        "Your session expired, please log in",
        "Sessão expirou, faça login",
    ]
    assert gate.parse_i18n_csv_row("key,zh-CN,en-US,pt-PT") is None


def test_analyze_diff_csv_quoted_commas_and_key():
    csv_diff = """\
+++ b/apps/x/central-web/src/assets/i18n.csv
@@ -10,0 +11 @@
+login.idle,超时,"Your session expired, please log in","Sessão expirou, faça login"
"""
    review = gate.analyze_diff(csv_diff)["review_text"]
    assert "Your session expired, please log in" in review
    assert "|login.idle]" in review
    # Must not split on commas inside quotes.
    assert 'please log in"' not in review
    assert '"Your session expired' not in review


def test_analyze_diff_standard_postprocess_translation_json():
    diff = """\
+++ b/packages/standard_postprocess/translation
@@ -1,0 +2,4 @@
+    "保存图篇": {
+        "Chinese": "保存图篇",
+        "English": "Save Imge"
+    },
"""
    review = gate.analyze_diff(diff)["review_text"]
    assert "保存图篇" in review
    assert "Save Imge" in review
    # Nested opener line must not be sent as raw syntax VALUE.
    assert '": {' not in review


def test_analyze_diff_vision_engine_nested_locale_object():
    diff = """\
+++ b/packages/vision_engine/unitxvisionengine/dimensional/ui/translations.py
@@ -100,0 +101 @@
+    "tab.setup": {"en": "Setp", "zh": "设置"},
"""
    review = gate.analyze_diff(diff)["review_text"]
    assert "Setp" in review
    assert "设置" in review
    assert "|tab.setup]" in review


def test_analyze_diff_python_implicit_string_concat():
    py_diff = """\
+++ b/translations/english.py
@@ -853,0 +853,6 @@
+GLOBAL_CONFIG_DESCRIPTION_TROUBLE_SHOOTING_TASK_GRAPH_CUSTOM_STEPS_TIMEOUT_MS = (
+    "Set the processing time of customized task graph nodes (such as custom image processing, "
+    "2.5D customization requirements, applying customized thresholds) has timed out. "
+    "This is used for system issue localization. The default is 100ms; when the time exceeds 100ms, "
+    "troubleshooting will determine a processing timeout and record it in the system."
+)
"""
    review = gate.analyze_diff(py_diff)["review_text"]
    expected = (
        "Set the processing time of customized task graph nodes "
        "(such as custom image processing, "
        "2.5D customization requirements, applying customized thresholds) "
        "has timed out. "
        "This is used for system issue localization. The default is 100ms; "
        "when the time exceeds 100ms, "
        "troubleshooting will determine a processing timeout and record it "
        "in the system."
    )
    assert expected in review
    assert "[translations/english.py:" in review
    assert "user_facing:" not in review
    assert "2.5D customization requirements" in review
    # Fragments must not appear as separate orphan reviews.
    assert "\n2.5D\n" not in review
    # Key appears only in compact header, not as a bare KEY = opener line.
    assert "|GLOBAL_CONFIG_DESCRIPTION_TROUBLE_SHOOTING_TASK_GRAPH_" in review
    assert "GLOBAL_CONFIG_DESCRIPTION_TROUBLE_SHOOTING_TASK_GRAPH_CUSTOM_STEPS_TIMEOUT_MS =" not in review


def test_filter_value_vs_key_severity():
    kept, dropped = gate.filter_userfacing_issues(
        [
            {
                "original": "auth_usrname",
                "problem": "key typo",
                "suggestion": "auth_username",
                "severity": "high",
            },
            {
                "original": "CONSOLE_lOG_SEARCH_SIGNAL",
                "problem": "Key CONSOLE_lOG_SEARCH_SIGNAL has lowercase 'l' in 'lOG' (identifier typo).",
                "suggestion": "CONSOLE_LOG_SEARCH_SIGNAL",
                "severity": "high",
            },
            {
                "original": "Cencel",
                "problem": "spelling in UI text",
                "suggestion": "Cancel",
                "severity": "high",
            },
            {
                "original": "FOO:",
                "problem": "Missing comma after key",
                "suggestion": "FOO:,",
                "severity": "high",
            },
        ]
    )
    assert {i["original"] for i in dropped} == {"FOO:"}
    by_o = {i["original"]: i for i in kept}
    assert by_o["auth_usrname"]["severity"] == "low"
    assert by_o["CONSOLE_lOG_SEARCH_SIGNAL"]["severity"] == "low"
    assert by_o["Cencel"]["severity"] == "high"


def test_filter_drops_key_and_syntax_false_positives():
    issues = [
        {
            "original": "COMPUTATIONAL_IMAGING_UNSAVED_SEQUENCE:",
            "problem": "Missing comma after key",
            "suggestion": "COMPUTATIONAL_IMAGING_UNSAVED_SEQUENCE:,",
            "severity": "high",
        },
        {
            "original": "FLEX_LIGNT_CONTROL_TITLE: 'Brightness control',",
            "problem": "Spelling error: 'LIGNT' should be 'LIGHT'",
            "suggestion": "FLEX_LIGHT_CONTROL_TITLE: 'Brightness control',",
            "severity": "high",
        },
        {
            "original": "FILE_CAMERA_NOT_SELECT: 'File Camera not select',",
            "problem": "Incorrect grammar (should be 'not selected')",
            "suggestion": "FILE_CAMERA_NOT_SELECT: 'File Camera not selected',",
            "severity": "high",
        },
        {
            "original": "File Camera not select",
            "problem": "Grammar: should be 'not selected'",
            "suggestion": "File Camera not selected",
            "severity": "high",
        },
        {
            "original": "serial port",
            "problem": "Inconsistent casing",
            "suggestion": "Serial Port",
            "severity": "low",
        },
    ]
    kept, dropped = gate.filter_userfacing_issues(issues)
    assert len(dropped) == 1
    assert dropped[0]["original"].startswith("COMPUTATIONAL_IMAGING_UNSAVED_SEQUENCE")

    by_original = {i["original"]: i for i in kept}
    assert by_original["FLEX_LIGNT_CONTROL_TITLE"]["severity"] == "low"
    assert by_original["FLEX_LIGNT_CONTROL_TITLE"]["suggestion"] == "FLEX_LIGHT_CONTROL_TITLE"
    assert by_original["File Camera not select"]["severity"] == "high"
    assert by_original["File Camera not select"]["suggestion"] == "File Camera not selected"
    assert by_original["serial port"]["severity"] == "low"


def test_split_into_batches_covers_full_text():
    chunk = "# file: a.js\n# line: 1\n+  'hello'"
    text = "\n\n".join([chunk] * 20)
    limit = len(chunk) * 3 + 10
    batches = gate.split_into_batches(text, limit=limit)
    assert len(batches) > 1
    assert all(len(b) <= limit for b in batches)
    assert sum(b.count("user_facing") + b.count("'hello'") for b in batches) >= 20
    for piece in text.split("\n\n"):
        assert any(piece in b for b in batches)


def test_split_text_for_limit_never_drops_chars():
    text = ("para-one\n\n" + "b" * 30 + "\n\n" + "c" * 200) * 3
    pieces = gate.split_text_for_limit(text, limit=50)
    assert "".join(pieces) == text
    assert all(len(p) <= 50 for p in pieces)
