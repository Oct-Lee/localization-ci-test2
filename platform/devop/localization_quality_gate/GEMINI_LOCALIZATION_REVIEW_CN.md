# Localization Quality Gate

English: [GEMINI_LOCALIZATION_REVIEW.md](./GEMINI_LOCALIZATION_REVIEW.md)

PR 用户可见文本（English / Simplified Chinese / Portuguese）质量门禁。Gemini 检查拼写、语法与本地化表达；仅 **HIGH** 阻断合入。

## 交付物

| 组件 | 路径 |
| --- | --- |
| Workflow（路径白名单唯一数据源） | [`.github/workflows/localization-quality-gate.yml`](../../../.github/workflows/localization-quality-gate.yml) |
| CLI 入口（facade） | [`localization_quality_gate.py`](./localization_quality_gate.py) |
| 实现模块 | [`config.py`](./config.py)、[`diff_parser.py`](./diff_parser.py)、[`gemini_client.py`](./gemini_client.py)、[`review_batcher.py`](./review_batcher.py)、[`response_processor.py`](./response_processor.py)、[`report_formatter.py`](./report_formatter.py)、[`models.py`](./models.py) |
| 误报白名单 | [`allowlist.json`](./allowlist.json) |
| 单元测试 | [`test_localization_quality_gate.py`](./test_localization_quality_gate.py) |

## Secret

仓库 **Settings → Secrets and variables → Actions**：

- Name: `GEMINI_API_KEY`
- Value: Google AI Studio / Gemini API Key

勿把 Key 写入代码、PR 输出或 Step Summary。

## 路径白名单

范围只在 workflow 的 `env.LOCALIZATION_GATE_PATHSPECS` 维护。未命中白名单的改动不会进入 `pr.diff`，也不会调用 Gemini。

覆盖大致包括：`locales/lang`、各类 `translations*`、`i18n/locales`、apps/x 的 `i18n.csv` 等用户可见文案路径。不含 vendor / 二进制。

## 本地运行

```bash
python -m pip install "requests>=2.31.0,<3"

# pathspec 须与 workflow 中 LOCALIZATION_GATE_PATHSPECS 一致
git diff <base> <head> --unified=0 -- \
  apps/optix/ui/locales/lang \
  ':(glob)**/translations_optix/**' \
  > pr.diff

export GEMINI_API_KEY=your-key
python platform/devop/localization_quality_gate/localization_quality_gate.py pr.diff
```

单元测试（不调真实 API）：

```bash
python -m pip install "pytest>=8.0.0,<9" "requests>=2.31.0,<3"
python -m pytest platform/devop/localization_quality_gate/test_localization_quality_gate.py -q
```

## CI 行为摘要

1. 对 PR base…head 按 `LOCALIZATION_GATE_PATHSPECS` 生成 `pr.diff`
2. 空 diff → 跳过 API，exit 0
3. 缺失时安装 `requests`，再跑审查脚本
4. stdout 输出结果 JSON；摘要写入 `GITHUB_STEP_SUMMARY`

送审格式为紧凑条目：

```text
[path/to/file.py:123]
user facing string value
```

按文件分会话；中文/葡语等 focused 文件约 1–2 批/文件。KEY/空白类问题在后处理中压为 low；placeholder 篡改会丢弃。

## 输出

stdout 示例：

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

Exit：

| 码 | 含义 |
| --- | --- |
| `0` | 无范围变更 / 无待审文本 / 无 HIGH |
| `1` | 有 HIGH，或缺 Key / API 失败 / JSON 非法 / 生成未完成（fail-closed）。单条畸形 issue 仅丢弃并告警，不中断整次运行。 |

## 误报白名单（allowlist）

模型判 HIGH、但文案故意如此时，加入同目录 [`allowlist.json`](allowlist.json)：

```json
[
  {"original": "故意保留的原文 VALUE"},
  {"file": "translations/chinese.js", "original": "仅该文件下匹配的 VALUE"}
]
```

- `original`：必填；整句 VALUE 一致，或 VALUE 内含该术语（中文子串如「采像」；英文按整词，如 `IPC` 不匹配 `IPConfig`）
- `file`：可选；有则路径相等或以该后缀结尾才忽略

## 模型 failover

按 `GEMINI_MODEL_QUOTAS` 顺序切换（同进程粘性）。429（日额度）与 503/500（同模型重试耗尽后）会切下一模型；到末模型仍失败则 fail-closed，**不绕回第一个**。

| 顺序 | Model ID | RPM | RPD |
| --- | --- | ---: | ---: |
| 1 | `gemini-3.1-flash-lite` | 15 | 500 |
| 2 | `gemini-3.5-flash-lite` | 15 | 500 |
| 3 | `gemini-3-flash-preview` | 5 | 20 |
| 4 | `gemini-3.5-flash` | 5 | 20 |
| 5 | `gemini-3.6-flash` | 5 | 20 |

Key 经 `x-goog-api-key` header 传递。

## 查看结果与 Required Check

1. PR → **Checks** → `Localization Quality Gate` / `Localization Quality Gate Required`
2. Job log 看 JSON；**Summary** 看 Markdown 报告

分支保护 Require status checks 勾选：**`Localization Quality Gate Required`**（与 required 聚合 job 的 `name` 一致）。
