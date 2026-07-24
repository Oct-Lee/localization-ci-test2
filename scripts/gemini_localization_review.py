import os
import sys
import json
import requests


diff_file = sys.argv[1]


with open(diff_file, "r", encoding="utf-8") as f:
    diff = f.read()


if not diff.strip():
    print("No changes")
    sys.exit(0)


# 保留修改上下文
changed_blocks = []

lines = diff.splitlines()

for i, line in enumerate(lines):

    # 找新增代码行
    if line.startswith("+") and not line.startswith("+++"):

        start = max(0, i - 3)
        end = min(len(lines), i + 4)

        context = lines[start:end]

        changed_blocks.extend(context)


if not changed_blocks:
    print("No added lines")
    sys.exit(0)


# 去重，保持顺序
review_text = "\n".join(
    dict.fromkeys(changed_blocks)
)


print("===== Code to review =====")
print(review_text)



api_key = os.environ["GEMINI_API_KEY"]


url = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/"
    "gemini-3.1-flash-lite:generateContent"
    f"?key={api_key}"
)



prompt = f"""
You are a professional localization quality reviewer.

Review the changed code below.

Only check existing user-facing text.

Check:

1. English grammar issues
2. English spelling issues
3. Chinese wording quality if Chinese exists
4. Portuguese wording quality if Portuguese exists
5. User-facing message professionalism


Important rules:

- Review only languages that appear in the code.
- Do NOT report missing translations.
- Do NOT require every message to have Chinese or Portuguese.
- Ignore variable names.
- Ignore code syntax issues.
- Only report real localization problems.


Changed code:

{review_text}


Return format:

Issue:
Original:
Problem:
Suggestion:
Severity:
"""


response = requests.post(
    url,
    json={
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    },
    timeout=60
)



data = response.json()


try:

    result = (
        data["candidates"][0]
        ["content"]
        ["parts"][0]
        ["text"]
    )

except Exception:

    print(json.dumps(data, indent=2))
    sys.exit(1)



print("===== Gemini Result =====")
print(result)



# 只根据真实 Issue 失败
if (
    "Issue:" in result
    and "No issue" not in result
):

    print(
        "Localization issues detected"
    )

    sys.exit(1)


print(
    "Localization check passed"
)