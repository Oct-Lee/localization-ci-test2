#!/usr/bin/env python3
"""测试 Gemini API 可用模型

用法:
    export GEMINI_API_KEY=your-key
    python test_gemini_models.py

可选参数:
    --models  手动指定模型ID列表，逗号分隔（覆盖默认列表）
    --timeout 请求超时秒数（默认 30）
"""

import os
import sys
import time
import json
import argparse
from typing import List, Dict, Any

import requests

# 默认测试的模型列表（基于已知支持的文本生成模型，可自行增删）
DEFAULT_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-3-flash-preview",
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash-lite",
    "gemini-3.0-flash-lite",   # 可能别名
    "gemini-2.5-flash-lite",
]

ENDPOINT_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent"


def test_model(model_id: str, api_key: str, timeout: int = 30) -> Dict[str, Any]:
    """测试单个模型是否可用，返回状态信息"""
    url = ENDPOINT_TEMPLATE.format(model_id=model_id)
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }
    payload = {
        "contents": [{"parts": [{"text": "Hello"}]}],
        "generationConfig": {"temperature": 0, "maxOutputTokens": 5},
    }
    start = time.monotonic()
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
        elapsed = time.monotonic() - start
        status = resp.status_code
        ok = status == 200
        error = None
        if not ok:
            try:
                error_body = resp.json()
                error = error_body.get("error", {}).get("message", resp.text[:200])
            except:
                error = resp.text[:200]
        # 检查是否返回了有效内容（即使200也可能无内容）
        if ok:
            try:
                data = resp.json()
                if "candidates" not in data or not data["candidates"]:
                    ok = False
                    error = "No candidates returned"
            except:
                ok = False
                error = "Invalid JSON response"
        return {
            "model": model_id,
            "status": status,
            "ok": ok,
            "elapsed": elapsed,
            "error": error,
            "response_preview": resp.text[:100] if ok else None,
        }
    except requests.Timeout:
        return {"model": model_id, "ok": False, "error": "Timeout", "elapsed": timeout}
    except requests.RequestException as e:
        return {"model": model_id, "ok": False, "error": str(e), "elapsed": time.monotonic() - start}


def main():
    parser = argparse.ArgumentParser(description="Test Gemini model availability")
    parser.add_argument(
        "--models",
        help="Comma-separated list of model IDs to test (overrides default list)",
    )
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    if args.models:
        model_list = [m.strip() for m in args.models.split(",") if m.strip()]
    else:
        model_list = DEFAULT_MODELS

    print(f"Testing {len(model_list)} models...\n")
    results = []
    for idx, model in enumerate(model_list, 1):
        print(f"[{idx}/{len(model_list)}] Testing {model} ... ", end="", flush=True)
        result = test_model(model, api_key, args.timeout)
        results.append(result)
        if result["ok"]:
            print(f"✅ Available ({result['elapsed']:.2f}s)")
        else:
            status = result.get("status", "N/A")
            error = result.get("error", "Unknown error")
            print(f"❌ Unavailable (HTTP {status}) - {error[:60]}")

    # 汇总表格
    print("\n" + "=" * 60)
    print(f"{'Model':<30} {'Status':<10} {'Time (s)':<10} {'Error'}")
    print("-" * 60)
    for r in results:
        status_str = "✅ OK" if r["ok"] else "❌ FAIL"
        err_str = r.get("error", "")[:40] if not r["ok"] else ""
        print(f"{r['model']:<30} {status_str:<10} {r['elapsed']:<10.2f} {err_str}")
    print("=" * 60)

    # 输出可用模型列表（便于脚本使用）
    available = [r["model"] for r in results if r["ok"]]
    if available:
        print("\nAvailable models:", ", ".join(available))
    else:
        print("\nNo available models found.")


if __name__ == "__main__":
    main()
