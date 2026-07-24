import os
import sys
import json
import requests


if len(sys.argv) < 2:
    print(
        "Usage: python gemini_localization_review.py <diff_file>"
    )
    sys.exit(1)


diff_file = sys.argv[1]


with open(
    diff_file,
    "r",
    encoding="utf-8"
) as f:

    diff = f.read()



if not diff.strip():

    print(
        "No changes detected"
    )

    sys.exit(0)



# ==============================
# Extract changed code context
# ==============================

lines = diff.splitlines()


changed_blocks = []

current_file = ""


for i, line in enumerate(lines):

    # 获取文件名
    if line.startswith("+++ b/"):

        current_file = line.replace(
            "+++ b/",
            ""
        )


    # 忽略 CI / script 文件
    if (
        current_file.startswith(".github/")
        or current_file.startswith("scripts/")
    ):
        continue


    # 只关注新增代码
    if (
        line.startswith("+")
        and not line.startswith("+++")
    ):

        start = max(
            0,
            i - 3
        )

        end = min(
            len(lines),
            i + 4
        )


        context = lines[start:end]


        changed_blocks.extend(
            context
        )



if not changed_blocks:

    print(
        "No user-facing code changes"
    )

    sys.exit(0)



# 去重保持顺序

review_text = "\n".join(
    dict.fromkeys(changed_blocks)
)



print(
    "===== Code to review ====="
)

print(
    review_text
)



# ==============================
# Gemini API
# ==============================

api_key = os.environ.get(
    "GEMINI_API_KEY"
)


if not api_key:

    print(
        "Missing GEMINI_API_KEY"
    )

    sys.exit(1)



url = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/"
    "gemini-3.1-flash-lite:generateContent"
    f"?key={api_key}"
)



prompt = f"""
You are a professional Localization Quality Reviewer.

Review the following Pull Request code changes.

Your goal:
Find problems in user-facing text quality.

Only review:

- UI messages
- Error messages
- Exception messages
- Logs visible to end users
- Localization resource strings


Check:

1. English grammar
2. English spelling
3. Chinese wording quality (only if Chinese exists)
4. Portuguese wording quality (only if Portuguese exists)
5. Professional wording quality


Important rules:

- Only analyze string literals.
- Ignore variable names.
- Ignore function names.
- Ignore comments.
- Ignore CI output.
- Ignore debug messages.
- Ignore developer-only text.
- Do NOT report missing translations.
- Do NOT require every message to have Chinese or Portuguese.
- Only report real localization problems.


Changed code:

----------------

{review_text}

----------------


Return format:

Issue:
Original:
Problem:
Suggestion:
Severity:


If there are no problems, return exactly:

No localization issues found
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



if response.status_code != 200:

    print(
        "Gemini API failed:"
    )

    print(
        response.text
    )

    sys.exit(1)



data = response.json()



try:

    result = (
        data["candidates"][0]
        ["content"]
        ["parts"][0]
        ["text"]
    )


except Exception:

    print(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False
        )
    )

    sys.exit(1)



print(
    "===== Gemini Result ====="
)

print(
    result
)



# ==============================
# Quality Gate
# ==============================


if (
    "No localization issues found"
    not in result
):

    print(
        "Localization issues detected"
    )

    sys.exit(1)



print(
    "Localization check passed"
)