import os
import sys
import json
import time
import requests


# ======================================
# Configuration
# ======================================

MAX_RETRY = 3


BLOCK_TYPES = [
    "spelling",
    "grammar"
]


BLOCK_SEVERITY = [
    "high"
]


# ======================================
# Argument Check
# ======================================

if len(sys.argv) < 2:

    print(
        "Usage: python gemini_localization_review.py <diff_file>"
    )

    sys.exit(1)



diff_file = sys.argv[1]



# ======================================
# Read Diff
# ======================================

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
# Diff Analyzer
# Extract added lines + context
# ======================================


lines = diff.splitlines()


changed_lines = []


current_file = ""


for i, line in enumerate(lines):


    if line.startswith(
        "+++ b/"
    ):

        current_file = line[6:]



    # Ignore workflow and scripts

    if (
        current_file.startswith(".github/")
        or current_file.startswith("scripts/")
    ):

        continue



    # Only analyze added lines

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



# ======================================
# Remove Git Metadata
# ======================================


review_lines = []


for line in changed_lines:


    if line.startswith(
        "+++"
    ):

        continue


    if line.startswith(
        "---"
    ):

        continue


    if line.startswith(
        "@@"
    ):

        continue


    review_lines.append(
        line
    )



review_text = "\n".join(
    dict.fromkeys(
        review_lines
    )
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



# ======================================
# Prompt Builder
# ======================================


prompt = f"""

You are a professional Localization Quality Reviewer.

Review the Pull Request changed code.

Your first task is to identify user-facing text.

User-facing text includes:

- UI messages
- Error messages
- Exception messages
- User-visible logs
- CLI output
- Localization strings


Ignore:

- Variable names
- Function names
- Class names
- URLs
- File paths
- UUID
- Hash values
- Debug-only messages
- CI configuration


Only analyze real user-facing strings.


Language checks:


1. English text:

Check:

- English spelling
- English grammar
- Natural English expression


2. Chinese text (if Chinese exists):

Check:

- Chinese wording quality
- Sentence fluency
- Word usage
- Chinese punctuation
- Mixed Chinese and English expression


3. Portuguese text (if Portuguese exists):

Check:

- Portuguese spelling
- Portuguese grammar
- Natural Portuguese expression


4. General localization quality:

Check:

- Professional wording
- User understanding
- Localization consistency


5. Capitalization:

Check sentence capitalization.

Examples:

Bad:

"camera not found"

Suggestion:

"Camera not found"


Important:

- Capitalization issues MUST be LOW severity.
- Capitalization issues MUST NOT block Pull Request.


Severity rules:


HIGH severity:

- English spelling errors
- Portuguese spelling errors
- English grammar errors
- Portuguese grammar errors
- Serious Chinese wording problems
- Serious localization errors


MEDIUM severity:

- Localization consistency issues
- Awkward wording affecting readability
- Minor Chinese expression issues


LOW severity:

- First letter lowercase
- Capitalization problems
- Style improvements
- Optional wording improvements


Blocking rules:

- HIGH severity blocks Pull Request.
- Spelling issues always block.
- Grammar issues always block.
- LOW and MEDIUM issues do not block.


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
            "type": "Spelling",
            "language": "English",
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

"""



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



# ======================================
# Gemini Retry
# ======================================


def call_gemini(
    url,
    payload,
    retries=MAX_RETRY
):


    for attempt in range(
        retries
    ):


        try:


            response = requests.post(

                url,

                json=payload,

                timeout=60

            )


            if response.status_code == 200:

                return response



            if response.status_code in [

                429,

                500,

                503

            ]:


                wait = 2 ** attempt


                print(

                    f"Gemini temporary error "
                    f"{response.status_code}, "
                    f"retry after {wait}s"

                )


                time.sleep(
                    wait
                )


                continue



            return response



        except requests.exceptions.Timeout:


            wait = 2 ** attempt


            print(

                f"Gemini timeout, "
                f"retry after {wait}s"

            )


            time.sleep(
                wait
            )



    raise RuntimeError(
        "Gemini API failed after retries"
    )



# ======================================
# Call Gemini
# ======================================


try:


    response = call_gemini(

        url,

        payload

    )


except Exception as e:


    print(
        e
    )

    sys.exit(1)



if response.status_code != 200:


    print(
        "Gemini API error:"
    )


    print(
        response.text
    )


    sys.exit(1)



# ======================================
# Extract Gemini Response
# ======================================


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
# JSON Parse
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



    if "has_issue" not in result:

        return False



    if "issues" not in result:

        return False



    if not isinstance(
        result["issues"],
        list
    ):

        return False



    for issue in result["issues"]:


        required_fields = [

            "type",

            "language",

            "original",

            "problem",

            "suggestion",

            "severity"

        ]



        for field in required_fields:


            if field not in issue:

                return False



        if issue["severity"].lower() not in [

            "high",

            "medium",

            "low"

        ]:

            return False



    return True



if not validate_result(
    result
):


    print(
        "Invalid Gemini JSON response"
    )


    sys.exit(1)



# ======================================
# Severity Policy
# ======================================


block_pr = False



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



        # Spelling and Grammar always block

        if issue_type in BLOCK_TYPES:

            block_pr = True



        # High severity blocks

        if severity in BLOCK_SEVERITY:

            block_pr = True



# ======================================
# Final Result
# ======================================


if block_pr:


    print(
        ""
    )


    print(
        "Localization Quality Gate Failed"
    )


    sys.exit(1)



print(
    "Localization check passed"
)


sys.exit(0)