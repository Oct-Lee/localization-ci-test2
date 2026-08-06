#!/usr/bin/env python3
"""测试多个 Gemini 模型对同一用户文本的审查结果"""

import os
import json
import time
import requests

# 要测试的模型列表（按你的要求）
MODELS = [
    "gemini-3-flash-preview",
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
]

# 待审查的文本（示例中含有拼写错误）
TEXT_TO_REVIEW = (
    'camera[{camera_id}] not Founded，Please check whether the "camera_id" '
    'parameter of the configration file is correct'
)

# 构造审查 Prompt（与门禁系统风格一致）
PROMPT_TEMPLATE = """You are a Localization Quality Reviewer.
Review ONLY the user-facing string VALUE below for English/Simplified Chinese/Portuguese.
Rules:
- Identify spelling, grammar, wrong words (including Chinese character mistakes).
- Keep placeholders identical (e.g., {{...}}, %s, ${{...}}).
- Leading/trailing whitespace style → severity "low" only.
- Return JSON only: {{"has_issue": bool, "issues": [{{"original": str, "problem": str, "suggestion": str, "severity": "high"|"medium"|"low"}}]}}
If no issues, set has_issue=false and issues=[].

VALUE to review:
{TEXT}
"""

def review_with_model(model_id: str, api_key: str, text: str) -> dict:
    """调用单个模型进行审查，返回完整响应"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent"
    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
    prompt = PROMPT_TEMPLATE.format(TEXT=text)
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0,
            "responseMimeType": "application/json",
        },
    }
    start = time.monotonic()
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        elapsed = time.monotonic() - start
        result = {
            "model": model_id,
            "status": resp.status_code,
            "elapsed": elapsed,
        }
        if resp.status_code == 200:
            data = resp.json()
            # 提取模型返回的文本
            try:
                text_response = data["candidates"][0]["content"]["parts"][0]["text"]
                # 尝试解析为 JSON
                try:
                    result["parsed"] = json.loads(text_response)
                except json.JSONDecodeError:
                    result["raw_text"] = text_response
                    result["parse_error"] = "Invalid JSON"
            except (KeyError, IndexError):
                result["error"] = "Unexpected response structure"
        else:
            result["error"] = resp.text[:200]
        return result
    except Exception as e:
        return {"model": model_id, "error": str(e), "elapsed": time.monotonic() - start}


def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY environment variable not set", file=sys.stderr)
        return 1

    print(f"🔍 Testing {len(MODELS)} models on the same text:\n")
    print(f"   Text: {TEXT_TO_REVIEW!r}\n")
    print("=" * 80)

    all_results = []
    for idx, model in enumerate(MODELS, 1):
        print(f"[{idx}/{len(MODELS)}] {model} ... ", end="", flush=True)
        res = review_with_model(model, api_key, TEXT_TO_REVIEW)
        all_results.append(res)

        if res.get("status") == 200 and "parsed" in res:
            has_issue = res["parsed"].get("has_issue", False)
            issue_count = len(res["parsed"].get("issues", []))
            print(f"✅ OK ({res['elapsed']:.2f}s) - has_issue={has_issue}, issues={issue_count}")
        else:
            error = res.get("error", res.get("parse_error", "Unknown"))
            print(f"❌ FAIL ({res['elapsed']:.2f}s) - {error[:60]}")

    # 详细输出每个模型的审查结果
    print("\n" + "=" * 80)
    print("📋 Detailed results:\n")
    for res in all_results:
        print(f"\n--- {res['model']} ---")
        if "parsed" in res:
            print(json.dumps(res["parsed"], indent=2, ensure_ascii=False))
        elif "raw_text" in res:
            print("Raw response (not JSON):")
            print(res["raw_text"][:500])
        else:
            print("Error:", res.get("error", "No response"))

    print("\n" + "=" * 80)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
