import os
import sys
import requests
import json


if len(sys.argv) < 2:
    print(
        "Usage: python3 test_gemini.py <file>"
    )
    sys.exit(1)


file_path = sys.argv[1]


with open(
    file_path,
    "r",
    encoding="utf-8"
) as f:
    file_content = f.read()


print("===== Input File =====")
print(file_content)


api_key = os.environ["GEMINI_API_KEY"]


url = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/"
    "gemini-3.1-flash-lite:generateContent"
    f"?key={api_key}"
)


prompt = f"""
You are a Localization Quality Reviewer.

Review the following file content.

Check:

English:
- spelling
- grammar
- sentence errors

Chinese:
- spelling
- grammar
- sentence errors

Portuguese:
- spelling
- grammar
- sentence errors


Ignore:
- variable names
- function names
- class names
- URLs
- paths


File:

{file_content}


Return JSON only.
"""


print("===== Calling Gemini =====")


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


print("HTTP Status:")
print(response.status_code)


print("===== Gemini Result =====")

print(
    json.dumps(
        response.json(),
        indent=2,
        ensure_ascii=False
    )
)