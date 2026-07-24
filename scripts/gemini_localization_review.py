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



# 只检查新增代码行
added_lines = []


for line in diff.splitlines():

    if line.startswith("+") and not line.startswith("+++"):
        added_lines.append(line)



if not added_lines:

    print("No added lines")
    sys.exit(0)



changed_text = "\n".join(added_lines)



print(
    "Checking added lines:"
)

print(changed_text)



api_key = os.environ["GEMINI_API_KEY"]


url = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/"
    "gemini-3.1-flash-lite:generateContent"
    f"?key={api_key}"
)



prompt = f"""
You are a professional localization quality reviewer.

Review ONLY the newly added code lines below.

Check:

1. English grammar
2. English spelling
3. Chinese wording quality
4. Portuguese wording quality
5. User-facing message professionalism

Rules:

- Ignore variable names
- Ignore comments unless they are user-facing
- Only report real localization issues
- Provide corrected text

New code:

{changed_text}


Output format:

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



print(
    "===== Gemini Result ====="
)

print(result)



# 简单门禁
if "Issue:" in result:

    print(
        "Localization issues detected"
    )

    sys.exit(1)



print(
    "Localization check passed"
)
