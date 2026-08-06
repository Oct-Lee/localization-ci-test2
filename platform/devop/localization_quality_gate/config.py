"""Localization Quality Gate configuration."""

from pathlib import Path
from typing import NamedTuple
import re

# ===== Model Quotas =====
class GeminiModelQuota(NamedTuple):
    model_id: str
    rpm: int
    rpd: int
    tpm: int | None = None

GEMINI_MODEL_QUOTAS: tuple[GeminiModelQuota, ...] = (
    GeminiModelQuota("gemini-3.1-flash-lite", rpm=15, rpd=500, tpm=250_000),
    GeminiModelQuota("gemini-3.5-flash-lite", rpm=15, rpd=500, tpm=250_000),
    GeminiModelQuota("gemini-3-flash-preview", rpm=5, rpd=20, tpm=250_000),
    GeminiModelQuota("gemini-3.5-flash", rpm=5, rpd=20, tpm=250_000),
    GeminiModelQuota("gemini-3.6-flash", rpm=5, rpd=20, tpm=250_000),
)
GEMINI_MODELS = tuple(q.model_id for q in GEMINI_MODEL_QUOTAS)

# ===== Timeouts & Retries =====
HTTP_TIMEOUT_SEC = 60
MAX_ATTEMPTS = 3
MAX_QUOTA_RETRIES = 5
QUOTA_RETRY_DEFAULT_SEC = 60.0

# ===== Review batch limits =====
MAX_REVIEW_CHARS = 100_000
FOCUSED_TARGET_BATCHES = 2
PACKED_MAX_CHUNKS_PER_BATCH = 50
SHORT_FILE_MAX_CHUNKS = 40
SHORT_FILE_MAX_CHARS = 20_000
CONTEXT_LINES = 1

# ===== File paths =====
ALLOWLIST_PATH = Path(__file__).resolve().parent / "allowlist.json"

# ===== Focused path regex =====
_FOCUSED_PATH_RE = re.compile(
    r"(?:chinese|portuguese|brazil|/zh(?:[-_/]|$)|_zh\.|zh_cn|zh-cn|zh_hans|"
    r"pt_br|pt-br|/pt(?:[-_/]|$)|_pt\.|"
    r"i18n\.csv|(?:^|/)translation$|dimensional/ui/translations\.py)",
    re.IGNORECASE,
)

# ===== Regular expressions =====
PLACEHOLDER_RE = re.compile(r"\{[^}]*\}|%\w|\$\{[^}]*\}")
FENCE_RE = re.compile(r"^\s*```(?:json)?\s*\n?(.*?)\n?\s*```\s*$", re.DOTALL | re.IGNORECASE)
PROP_KEY = r"[A-Za-z_][A-Za-z0-9_]*"
KEY_ONLY_RE = re.compile(rf"^{PROP_KEY}\s*:?\s*,?\s*$")
KEY_ONLY_LINE_RE = re.compile(rf"^\s*({PROP_KEY})\s*:\s*$")
KEY_ASSIGN_PREFIX_RE = re.compile(rf"^\s*({PROP_KEY})\s*[:=]\s*$")
PY_KEY_OPEN_RE = re.compile(rf"^\s*([A-Z][A-Z0-9_]*)\s*=\s*\(\s*$")
STRUCT_OPEN_RE = re.compile(rf"^\s*{PROP_KEY}\s*:\s*[{{\[]\s*,?\s*$")
QUOTED_KEY_STRUCT_OPEN_RE = re.compile(
    r'''^\s*"(?P<key>(?:\\.|[^"\\])*)"\s*:\s*\{\s*,?\s*$'''
)
NESTED_LOCALE_OBJECT_RE = re.compile(
    r'''^\s*"(?P<key>(?:\\.|[^"\\])*)"\s*:\s*\{(?P<body>.*)\}\s*,?\s*$'''
)
NESTED_LOCALE_PAIR_RE = re.compile(
    r'''"(?P<lang>(?:\\.|[^"\\])*)"\s*:\s*"(?P<val>(?:\\.|[^"\\])*)"'''
)
_LOCALE_LANG_KEYS = frozenset({
    "en", "zh", "pt", "en-us", "zh-cn", "pt-pt", "pt-br", "zh-hans", "zh-hant",
    "english", "chinese", "portuguese",
})
PY_TRIPLE_OPEN_RE = re.compile(
    rf"""^\s*({PROP_KEY})\s*=\s*[fFrRbBuU]*(?P<q>\"\"\"|''')(?P<rest>.*)$"""
)
STRING_VALUE_LINE_RE = re.compile(
    r"""^\s*(['"])((?:\\.|(?!\1)[^\r\n])*)\1\s*,?\s*$"""
)
ASSIGNMENT_LINE_RE = re.compile(rf"""^\s*({PROP_KEY})\s*[:=]\s*(['"])(.*)\2\s*,?\s*$""", re.DOTALL)
JSON_KV_RE = re.compile(r"""^\s*"((?:\\.|[^"\\])*)"\s*:\s*"((?:\\.|[^"\\])*)"\s*,?\s*$""")
SKIP_LINE_RE = re.compile(
    r"""(?x)^\s*(?:import\b|from\b|export\s+default\b|export\s+const\b|
    const\s+\w+\s*=\s*\{|/\*|^\s*\*|^\s*//|\}|\{|,|\#)"""
)
SYNTAX_PROBLEM_RE = re.compile(
    r"missing comma|extra comma|\bsyntax\b|missing colon|json structure|"
    r"javascript syntax|python syntax|typescript syntax|\bbrace\b|\bquote\b",
    re.IGNORECASE,
)
_WS_PROBLEM_RE = re.compile(
    r"leading\s+space|trailing\s+space|leading\s+whitespace|trailing\s+whitespace|"
    r"extra\s+space|whitespace\s+at\s+(the\s+)?(start|beginning|end)|"
    r"starts?\s+with\s+(a\s+)?space|ends?\s+with\s+(a\s+)?space|"
    r"前导空格|尾随空格|首尾空格",
    re.IGNORECASE,
)
HUNK_RE = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
_STRUCT_TOKENS = frozenset(("{", "}", "},", "[", "],", "];", "};", ")", "),", "("))
_ID_PROBLEM_TOKENS = (
    "identifier", "constant name", "key name", "object key", "property name",
    "variable name", "key typo",
)
_COMPLETE_FINISH_REASONS = frozenset({"STOP", "stop", "FINISH_REASON_STOP"})

# ===== Severity =====
SEVERITY_HIGH, SEVERITY_MEDIUM, SEVERITY_LOW = "high", "medium", "low"
VALID_SEVERITIES = {SEVERITY_HIGH, SEVERITY_MEDIUM, SEVERITY_LOW}
_SEVERITY_RANK = {SEVERITY_HIGH: 3, SEVERITY_MEDIUM: 2, SEVERITY_LOW: 1}

# ===== Response schema for Gemini =====
_ISSUE_SCHEMA: dict[str, any] = {
    "type": "OBJECT",
    "properties": {
        "file": {"type": "STRING"},
        "line": {"type": "INTEGER"},
        "original": {"type": "STRING"},
        "problem": {"type": "STRING"},
        "suggestion": {"type": "STRING"},
        "severity": {"type": "STRING", "enum": ["high", "medium", "low"]},
    },
    "required": ["original", "problem", "suggestion", "severity"],
}
RESPONSE_SCHEMA: dict[str, any] = {
    "type": "OBJECT",
    "properties": {
        "has_issue": {"type": "BOOLEAN"},
        "issues": {"type": "ARRAY", "items": _ISSUE_SCHEMA},
    },
    "required": ["has_issue", "issues"],
}

# ===== Endpoint helper =====
def gemini_endpoint(model_id: str) -> str:
    return f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent"

# ===== Rate limit interval helper =====
def min_request_interval_sec(rpm: int | None = None) -> float:
    """Minimum seconds between request starts to approach RPM limit."""
    limit = rpm if rpm is not None else GEMINI_MODEL_QUOTAS[0].rpm
    return 60.0 / limit
