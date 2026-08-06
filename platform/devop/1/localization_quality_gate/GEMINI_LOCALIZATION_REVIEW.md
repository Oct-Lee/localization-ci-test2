# Localization Quality Gate

中文说明见：[GEMINI_LOCALIZATION_REVIEW_CN.md](./GEMINI_LOCALIZATION_REVIEW_CN.md)

PR quality gate for user-facing text (English / Simplified Chinese / Portuguese). Gemini reviews spelling, grammar, and localization quality; only **HIGH** severity blocks merge.

## Deliverables

| Component | Path |
| --- | --- |
| Workflow (sole path-allowlist source) | [`.github/workflows/localization-quality-gate.yml`](../../../.github/workflows/localization-quality-gate.yml) |
| Review script | [`localization_quality_gate.py`](./localization_quality_gate.py) |
| Unit tests | [`test_localization_quality_gate.py`](./test_localization_quality_gate.py) |

## Secret

In the repo **Settings → Secrets and variables → Actions**:

- Name: `GEMINI_API_KEY`
- Value: Google AI Studio / Gemini API key

Do not put the key in code, PR output, or the Step Summary.

## Path allowlist

Scope is maintained only in the workflow env `LOCALIZATION_GATE_PATHSPECS`. Changes outside the allowlist never enter `pr.diff` and never call Gemini.

Coverage is roughly: `locales/lang`, various `translations*`, `i18n/locales`, apps/x `i18n.csv`, and similar user-facing copy. Vendor paths and binaries are excluded.

## Local run

```bash
python -m pip install "requests>=2.31.0,<3"

# pathspecs must match LOCALIZATION_GATE_PATHSPECS in the workflow
git diff <base> <head> --unified=0 -- \
  apps/optix/ui/locales/lang \
  ':(glob)**/translations_optix/**' \
  > pr.diff

export GEMINI_API_KEY=your-key
python platform/devop/localization_quality_gate/localization_quality_gate.py pr.diff
```

Unit tests (no live API):

```bash
python -m pip install "pytest>=8.0.0,<9" "requests>=2.31.0,<3"
python -m pytest platform/devop/localization_quality_gate/test_localization_quality_gate.py -q
```

## CI behavior

1. Build `pr.diff` for PR base…head using `LOCALIZATION_GATE_PATHSPECS`
2. Empty diff → skip API, exit 0
3. Install `requests` if missing, then run the review script
4. Print result JSON on stdout; write Markdown to `GITHUB_STEP_SUMMARY`

Compact review payload format:

```text
[path/to/file.py:123]
user facing string value
```

One Gemini session per file; focused locale files (e.g. Chinese / Portuguese) use about 1–2 batches per file. Identifier/key and whitespace-style findings are forced to low in post-processing; placeholder-breaking suggestions are dropped.

## Output

stdout example:

```json
{
  "has_issue": true,
  "issues": [
    {
      "file": "apps/optix/ui/locales/lang/en.json",
      "line": 11,
      "original": "camera[{camera_id}] not Founded",
      "problem": "Grammatical error",
      "suggestion": "camera[{camera_id}] not found",
      "severity": "high"
    }
  ],
  "files": [
    {
      "path": "apps/optix/ui/locales/lang/en.json",
      "added": 1,
      "deleted": 0
    }
  ]
}
```

Exit codes:

| Code | Meaning |
| --- | --- |
| `0` | No in-scope changes / nothing to review / no HIGH |
| `1` | HIGH findings, or missing key / API failure / invalid JSON / incomplete generation (fail-closed). Malformed individual issues are dropped with a warning. |

## False-positive allowlist

When the model marks HIGH but the copy is intentional, add an entry to [`allowlist.json`](allowlist.json):

```json
[
  {"original": "intentional VALUE as-is"},
  {"file": "translations/chinese.js", "original": "VALUE matched only under this file"}
]
```

- `original` (required): exact match on the issue VALUE
- `file` (optional): when set, issue path must equal or end with this suffix

## Model failover

Models are tried in `GEMINI_MODEL_QUOTAS` order (sticky within one process). Daily-quota 429 and exhausted same-model 503/500 retries advance to the next model. After the last model fails, the gate fail-closes and **does not wrap back to the first**.

| Order | Model ID | RPM | RPD |
| --- | --- | ---: | ---: |
| 1 | `gemini-3.1-flash-lite` | 15 | 500 |
| 2 | `gemini-3.5-flash-lite` | 15 | 500 |
| 3 | `gemini-3-flash-preview` | 5 | 20 |
| 4 | `gemini-3.5-flash` | 5 | 20 |
| 5 | `gemini-3.6-flash` | 5 | 20 |

The API key is sent via the `x-goog-api-key` header.

## Results and required check

1. Open the PR → **Checks** → `Localization Quality Gate`
2. Job log for JSON; **Summary** tab for the Markdown report

Under branch protection → Require status checks, enable **`Localization Quality Gate`** (must match the workflow `name`).
