import os
import sys
import json
import time
import requests


if len(sys.argv) < 2:
    print(
        "Usage: python gemini_localization_review.py <diff>"
    )
    sys.exit(1)


with open(
    sys.argv[1],
    "r",
    encoding="utf-8"
) as f:
    diff = f.read()



api_key = os.environ["GEMINI_API_KEY"]


url = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/"
    "gemini-3.1-flash-lite:generateContent"
    f"?key={api_key}"
)



prompt = f"""
You are a professional Localization Quality Reviewer.

Review only user-facing text in this PR diff.

Check languages:

English:
- spelling mistakes
- grammar mistakes
- unnatural sentences

Chinese:
- spelling mistakes
- grammar mistakes
- unnatural expressions
- punctuation problems

Portuguese:
- spelling mistakes
- grammar mistakes
- unnatural expressions


Ignore:

- variable names
- function names
- class names
- URLs
- file paths
- debug logs


Keep placeholders unchanged:

{{name}}
%s
%d


Severity:

HIGH:
- spelling errors
- grammar errors
- serious localization issues

MEDIUM:
- wording problems affecting readability

LOW:
- style suggestions


Return JSON only:

{{
  "issues": [
    {{
      "original": "",
      "problem": "",
      "suggestion": "",
      "severity": "HIGH|MEDIUM|LOW"
    }}
  ]
}}


PR diff:

{diff}
"""



for retry in range(3):

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


    if response.status_code == 200:
        break


    if response.status_code in [429, 503]:

        print(
            f"Gemini unavailable, retry {retry+1}/3"
        )

        time.sleep(
            (retry + 1) * 10
        )

        continue


    print(response.text)
    sys.exit(1)



data = response.json()


content = (
    data["candidates"][0]
    ["content"]
    ["parts"][0]
    ["text"]
)


print(
    "===== Gemini Result ====="
)

print(content)



try:

    result = json.loads(content)

except Exception:

    print(
        "Gemini response is not valid JSON"
    )

    sys.exit(1)



high = [
    issue
    for issue in result.get("issues", [])
    if issue.get("severity") == "HIGH"
]


if high:

    print(
        "❌ Localization issues found"
    )

    for issue in high:
        print(
            json.dumps(
                issue,
                ensure_ascii=False
            )
        )

    sys.exit(1)



print(
    "✅ Localization check passed"
)