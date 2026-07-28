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



# ======================================
# Extract useful diff context
# ======================================

lines = diff.splitlines()


changed_lines = []


current_file = ""


for i, line in enumerate(lines):

    # get filename
    if line.startswith("+++ b/"):

        current_file = line[6:]


    # ignore CI scripts
    if (
        current_file.startswith(".github/")
        or current_file.startswith("scripts/")
    ):
        continue


    # collect changed context
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


        changed_lines.extend(
            lines[start:end]
        )



if not changed_lines:

    print(
        "No user-facing changes"
    )

    sys.exit(0)



# remove git metadata

review_lines = []


for line in changed_lines:

    if line.startswith("+++"):
        continue

    if line.startswith("---"):
        continue

    if line.startswith("@@"):
        continue


    review_lines.append(line)



# remove duplicate lines

review_text = "\n".join(
    dict.fromkeys(review_lines)
)



print(
    "===== Code to review ====="
)

print(
    review_text
)



# ======================================
# Gemini API
# ======================================

api_key = os.environ.get(
    "GEMINI_API_KEY"
)


if not api_key:

    print(
        "GEMINI_API_KEY is missing"
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

Review this Pull Request diff.

Only check user-facing text.

Review:

- UI messages
- Error messages
- Exception messages
- User-visible logs
- Localization strings


Check:
+9
1. English spelling
2. English grammar
3. Chinese wording quality if Chinese exists
4. Portuguese wording quality if Portuguese exists
5. Professional wording quality


Important rules:

- Only analyze string literals.
- Ignore comments.
- Ignore variable names.
- Ignore function names.
- Ignore CI output.
- Ignore debug-only messages.
- Do NOT report missing translations.
- Do NOT require every message to have Chinese or Portuguese.
- Only report real localization problems.


Changed code:

----------------

{review_text}

----------------


Return JSON only.

Format:

{{
  "has_issue": true,
  "issues": [
    {{
      "type": "",
      "original": "",
      "problem": "",
      "suggestion": "",
      "severity": "high|medium|low"
    }}
  ]
}}


If no issues:

{{
  "has_issue": false,
  "issues": []
}}
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
        "Gemini API error:"
    )

    print(
        response.text
    )

    sys.exit(1)



data = response.json()



try:

    gemini_text = (
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
    "===== Gemini Raw Result ====="
)

print(
    gemini_text
)



# ======================================
# Parse JSON result
# ======================================

try:

    result = json.loads(
        gemini_text
    )


except Exception:

    print(
        "Gemini did not return valid JSON"
    )

    sys.exit(1)



if result.get(
    "has_issue",
    False
):

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


    sys.exit(1)



print(
    "Localization check passed"
)

sys.exit(0)