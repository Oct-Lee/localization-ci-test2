import os
import sys
import json
import time
import re
import requests


MAX_RETRY = 3


# ======================================
# Read diff
# ======================================

if len(sys.argv) < 2:

    print(
        "Usage: python gemini_localization_review.py <diff_file>"
    )

    sys.exit(1)



with open(
    sys.argv[1],
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
# Extract changed lines + context
# ======================================


lines = diff.splitlines()

review_lines = []

current_file = ""


for i, line in enumerate(lines):


    if line.startswith(
        "+++ b/"
    ):

        current_file = line[6:]



    # Ignore CI related files

    if (
        current_file.startswith(".github/")
        or current_file.startswith("scripts/")
    ):

        continue



    # Only added lines

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

    print(
        "No user-facing changes"
    )

    sys.exit(0)



review_text = "\n".join(
    dict.fromkeys(
        line
        for line in review_lines
        if not line.startswith(
            (
                "---",
                "+++",
                "@@"
            )
        )
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

Review only user-facing text in the Pull Request changes.


Your goal:

Identify real localization issues while preserving the original user-facing
message structure.


Check:


1. English text:

- spelling errors
- grammar errors
- incorrect word usage
- unnatural expressions


2. Chinese text if Chinese exists:

- wording quality
- sentence fluency
- punctuation
- mixed Chinese and English expression issues


3. Portuguese text if Portuguese exists:

- spelling errors
- grammar errors
- natural expression


4. General localization quality:

- professional wording
- user understanding
- consistency


--------------------------------------------------

Ignore:

- variable names
- function names
- class names
- URLs
- file paths
- UUIDs
- hashes
- debug-only messages
- internal developer comments


--------------------------------------------------

User-facing Text Rules:


- Only report issues from user-facing strings.
- The "original" field MUST contain the complete original user-facing text.
- Do NOT shorten, summarize, or extract only part of the text.
- Keep the original context when reporting an issue.


--------------------------------------------------

Placeholder Rules:


Preserve all placeholders exactly.

Placeholders include:

- template variables
- format specifiers
- runtime parameters


The "original" and "suggestion" fields MUST keep the same placeholders.


Do NOT:

- remove placeholders
- rename placeholders
- change placeholder format
- modify placeholder values


--------------------------------------------------

Text Preservation Rules:


- Do not remove product names, device names, or user-visible identifiers.
- Do not rewrite unrelated parts of the message.
- Only change the incorrect language part in the suggestion.


--------------------------------------------------

Severity Rules:


HIGH:

- spelling errors
- grammar errors
- incorrect word usage
- serious localization problems
- issues affecting user understanding


MEDIUM:

- wording problems affecting readability
- localization consistency issues


LOW:

- capitalization issues
- first letter lowercase
- optional style improvements


--------------------------------------------------

Blocking Rules:


- All spelling issues MUST be HIGH severity.
- All grammar issues MUST be HIGH severity.
- All incorrect word usage issues MUST be HIGH severity.
- Capitalization issues MUST be LOW severity.
- LOW severity issues do not block Pull Request.


--------------------------------------------------

Output Rules:


Return JSON only.

Do not include markdown.
Do not include explanations outside JSON.


Format:


{{
    "has_issue": true,

    "issues": [
        {{
            "original": "",
            "problem": "",
            "suggestion": "",
            "severity": "high"
        }}
    ]
}}


If no issues:


{{
    "has_issue": false,
    "issues": []
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



def call_gemini():


    for attempt in range(
        MAX_RETRY
    ):


        try:


            response = requests.post(

                url,

                json=payload,

                timeout=60

            )


            if response.status_code == 200:

                return response



            if response.status_code in (

                429,
                500,
                503

            ):


                wait = 2 ** attempt


                print(
                    f"Gemini retry after {wait}s"
                )


                time.sleep(
                    wait
                )

                continue



            return response



        except requests.exceptions.Timeout:


            wait = 2 ** attempt


            print(
                f"Gemini timeout retry after {wait}s"
            )


            time.sleep(
                wait
            )



    raise RuntimeError(
        "Gemini API failed after retry"
    )



response = call_gemini()



if response.status_code != 200:


    print(
        "Gemini API error:"
    )


    print(
        response.text
    )


    sys.exit(1)



# ======================================
# Parse Gemini Result
# ======================================


try:


    data = response.json()


    result_text = (

        data["candidates"][0]

        ["content"]

        ["parts"][0]

        ["text"]

    )


    result = json.loads(
        result_text
    )


except Exception:


    print(
        "Invalid Gemini response"
    )

    sys.exit(1)



# ======================================
# JSON Validation
# ======================================


def validate_result(
    result
):


    if not isinstance(
        result,
        dict
    ):

        return False



    if (
        "has_issue" not in result
        or "issues" not in result
    ):

        return False



    for issue in result["issues"]:


        fields = [

            "original",

            "problem",

            "suggestion",

            "severity"

        ]


        for field in fields:


            if field not in issue:

                return False



        if issue["severity"].lower() not in (

            "high",
            "medium",
            "low"

        ):

            return False



    return True



if not validate_result(
    result
):

    print(
        "Invalid JSON format"
    )

    sys.exit(1)



# ======================================
# Placeholder Validation
# ======================================


def get_placeholders(
    text
):

    return re.findall(

        r"\{[^}]+\}|%\w|\$\{[^}]+\}",

        text

    )



for issue in result.get(
    "issues",
    []
):


    original = issue.get(
        "original",
        ""
    )


    suggestion = issue.get(
        "suggestion",
        ""
    )


    if (
        get_placeholders(original)
        !=
        get_placeholders(suggestion)
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
# Severity Policy
# ======================================


failed = False


if result.get(
    "has_issue",
    False
):


    print(
        "===== Language Quality Issues ====="
    )


    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )


    for issue in result.get(
        "issues",
        []
    ):


        if issue.get(
            "severity",
            ""
        ).lower() == "high":

            failed = True



# ======================================
# Final Result
# ======================================


if failed:


    print(
        "Localization Quality Gate Failed"
    )


    sys.exit(1)



print(
    "Localization check passed"
)


sys.exit(0)