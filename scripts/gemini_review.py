import os
import time
import requests


api_key = os.environ["GEMINI_API_KEY"]


with open(
    "pr.diff",
    encoding="utf-8"
) as f:
    diff = f.read()


if not diff.strip():
    print("No diff")
    exit(0)


if len(diff) > 8000:
    diff = diff[:8000]


prompt = f"""
You are a localization quality reviewer.

Review this code diff.

Check:

1. English spelling
2. English grammar
3. Chinese wording
4. Portuguese wording
5. User-facing message quality


Return:

## Problems

- Location
- Problem
- Reason
- Suggested correction


Diff:

{diff}
"""


url = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/"
    "gemini-3.1-flash-lite:generateContent"
    f"?key={api_key}"
)


response = None


for retry in range(3):

    print(
        f"Gemini attempt {retry + 1}"
    )

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


    print(response.text)


    if response.status_code == 429:
        time.sleep(
            10 * (retry + 1)
        )


if response.status_code != 200:
    raise Exception(
        response.text
    )


result = response.json()


text = (
    result["candidates"][0]
    ["content"]
    ["parts"][0]
    ["text"]
)


print(text)


with open(
    "gemini-result.md",
    "w",
    encoding="utf-8"
) as f:
    f.write(text)
