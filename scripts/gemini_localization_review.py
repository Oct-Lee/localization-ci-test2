import os
import sys
import json
import time
import re
import requests


MAX_RETRY = 3


# Spelling / Grammar always block
BLOCK_TYPES = [
    "spelling",
    "grammar"
]


# ======================================
# Read diff
# ======================================

if len(sys.argv) < 2:
    print("Usage: python gemini_localization_review.py <diff_file>")
    sys.exit(1)


with open(
    sys.argv[1],
    "r",
    encoding="utf-8"
) as f:
    diff = f.read()


if not diff.strip():
    print("No changes detected")
    sys.exit(0)



# ======================================
# Extract changed lines + context
# ======================================

lines = diff.splitlines()

review_lines = []

current_file = ""


for i, line in enumerate(lines):

    if line.startswith("+++ b/"):
        current_file = line[6:]


    if (
        current_file.startswith(".github/")
        or current_file.startswith("scripts/")
    ):
        continue


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

        review_lines.extend(
            lines[start:end]
        )



if not review_lines:
    print("No user-facing changes")
    sys.exit(0)



review_text = "\n".join(
    dict.fromkeys(
        x for x in review_lines
        if not x.startswith(("---", "+++", "@@"))
    )
)


print(
    "===== Code to review ====="
)

print(
    review_text
)



# ======================================
# Gemini Prompt
# ======================================

prompt = f"""
You are a professional Localization Quality Reviewer.

Review only user-facing text.

Check:

1. English:
- spelling
- grammar
- natural expression

2. Chinese (if exists):
- wording quality
- sentence fluency
- punctuation

3. Portuguese (if exists):
- spelling
- grammar
- natural expression

4. Localization quality.


Ignore:

- variable names
- function names
- class names
- URLs
- paths
- debug messages


Important:

Preserve placeholders.

Examples:

{{camera_id}}
%s
%d
${{name}}

Placeholders are part of user-facing text.

Do NOT remove, change, or omit them.


Severity:

HIGH:
- spelling errors
- grammar errors
- serious localization problems

MEDIUM:
- wording problems

LOW:
- capitalization issues
- style suggestions


Rules:

- Spelling and Grammar must be HIGH.
- Capitalization must be LOW.
- LOW issues do not block.


Return JSON only.

Format:

{{
 "has_issue": true,
 "issues": [
  {{
   "type": "Grammar",
   "language": "English",
   "original": "",
   "problem": "",
   "suggestion": "",
   "severity": "high"
  }}
 ]
}}


Changed code:

----------------

{review_text}

----------------
"""


# ======================================
# Gemini API
# ======================================

api_key = os.environ.get(
    "GEMINI_API_KEY"
)


if not api_key:
    print("Missing GEMINI_API_KEY")
    sys.exit(1)



url = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/"
    "gemini-3.1-flash-lite:generateContent"
    f"?key={api_key}"
)



def call_gemini():

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }


    for retry in range(MAX_RETRY):

        try:

            r = requests.post(
                url,
                json=payload,
                timeout=60
            )


            if r.status_code == 200:
                return r


            if r.status_code in (
                429,
                500,
                503
            ):

                sleep = 2 ** retry

                print(
                    f"Gemini retry after {sleep}s"
                )

                time.sleep(
                    sleep
                )

                continue


            return r


        except requests.exceptions.Timeout:

            sleep = 2 ** retry

            print(
                f"Timeout retry after {sleep}s"
            )

            time.sleep(
                sleep
            )


    raise Exception(
        "Gemini API failed"
    )



response = call_gemini()



if response.status_code != 200:

    print(
        response.text
    )

    sys.exit(1)



# ======================================
# Parse result
# ======================================

data = response.json()


try:

    text = (
        data["candidates"][0]
        ["content"]
        ["parts"][0]
        ["text"]
    )


    result = json.loads(
        text
    )


except Exception:

    print(
        "Invalid Gemini response"
    )

    sys.exit(1)



# ======================================
# Validate
# ======================================

def placeholders(text):

    return re.findall(
        r"\{[^}]+\}|%\w|\$\{[^}]+\}",
        text
    )



for issue in result.get(
    "issues",
    []
):

    if placeholders(
        issue.get("original", "")
    ) != placeholders(
        issue.get("suggestion", "")
    ):

        print(
            "Placeholder changed:"
        )

        print(
            json.dumps(
                issue,
                indent=2,
                ensure_ascii=False
            )
        )

        sys.exit(1)



# ======================================
# Severity policy
# ======================================

failed = False


for issue in result.get(
    "issues",
    []
):

    issue_type = issue.get(
        "type",
        ""
    ).lower()


    severity = issue.get(
        "severity",
        ""
    ).lower()


    if (
        "spelling" in issue_type
        or "grammar" in issue_type
    ):

        failed = True


    if severity == "high":

        failed = True



print(
    "===== Localization Issues ====="
)


print(
    json.dumps(
        result,
        indent=2,
        ensure_ascii=False
    )
)



if failed:

    print(
        "Localization Quality Gate Failed"
    )

    sys.exit(1)



print(
    "Localization check passed"
)

sys.exit(0)