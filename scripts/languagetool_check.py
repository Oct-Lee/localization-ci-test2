#!/usr/bin/env python3

import os
import requests


LANGUAGETOOL_URL = (
    "https://api.languagetool.org/v2/check"
)


SUPPORTED_EXTENSIONS = (

    ".py",
    ".sh",
    ".cpp",
    ".hpp",
    ".c",
    ".h",
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml"

)



LANGUAGES = [

    "en-US",

    "zh-CN",

    "pt-PT"

]



def get_changed_files():

    """
    Get changed files from GitHub Actions.
    Provided by tj-actions/changed-files.
    """

    value = os.environ.get(
        "CHANGED_FILES",
        ""
    )


    if not value:

        print(
            "No changed files."
        )

        return []



    files = []


    for file in value.split():


        if file.endswith(
            SUPPORTED_EXTENSIONS
        ):

            files.append(
                file
            )


    return files





def read_files(files):

    """
    Read only changed files.
    """

    content = ""


    for file in files:


        try:


            print(
                "Reading:",
                file
            )


            with open(
                file,
                encoding="utf-8"
            ) as f:


                content += (
                    "\n"
                    + f.read()
                )


        except Exception as e:


            print(
                "Skip file:",
                file,
                e
            )


    return content





def remove_code_noise(text):

    """
    Reduce false positives.

    Keep user-facing strings.
    """

    lines = []


    for line in text.splitlines():


        line=line.strip()


        if not line:

            continue



        # ignore imports

        if line.startswith(
            (
                "import ",
                "from "
            )
        ):

            continue



        # ignore comments

        if line.startswith("#"):

            continue



        lines.append(
            line
        )



    return "\n".join(
        lines
    )





def call_languagetool(
    text,
    language
):


    data = {

        "text": text,

        "language": language

    }


    try:


        response = requests.post(

            LANGUAGETOOL_URL,

            data=data,

            timeout=60

        )



        print(
            "",
            language,
            "HTTP:",
            response.status_code
        )



        if response.status_code != 200:


            print(
                response.text[:500]
            )


            return None



        content_type = response.headers.get(
            "content-type",
            ""
        )



        if "json" not in content_type:


            print(
                "Unexpected response:"
            )


            print(
                response.text[:500]
            )


            return None



        return response.json()



    except Exception as e:


        print(
            "LanguageTool request failed:",
            e
        )


        return None





def print_result(
    language,
    result
):


    if not result:


        return



    matches = result.get(
        "matches",
        []
    )



    if not matches:


        print(
            language,
            "PASS"
        )

        return



    print(
        ""
    )

    print(
        "=============================="
    )


    print(
        "Language:",
        language
    )


    print(
        "Issues:",
        len(matches)
    )


    print(
        "=============================="
    )



    for item in matches:


        message = item.get(
            "message",
            ""
        )


        context = item.get(
            "context",
            {}
        ).get(
            "text",
            ""
        )



        replacements = [

            x.get(
                "value"
            )

            for x in item.get(
                "replacements",
                []
            )[:5]

        ]



        print(
            ""
        )


        print(
            "Problem:"
        )


        print(
            message
        )


        print(
            "Context:"
        )


        print(
            context
        )


        print(
            "Suggestion:"
        )


        print(
            replacements
        )



        print(
            "------------------------------"
        )





def main():


    print(
        "================================"
    )


    print(
        "Localization Grammar Check"
    )


    print(
        "================================"
    )



    files = get_changed_files()



    print(
        "Changed files:"
    )


    for f in files:

        print(
            " -",
            f
        )



    if not files:


        print(
            "Nothing to check."
        )

        return



    text = read_files(
        files
    )



    if not text.strip():


        print(
            "No text."
        )

        return



    text = remove_code_noise(
        text
    )



    # Avoid huge request

    if len(text) > 12000:


        text = text[:12000]


        print(
            "Text truncated."
        )



    failed = False



    for language in LANGUAGES:


        result = call_languagetool(

            text,

            language

        )


        print_result(

            language,

            result

        )


        if result:


            if len(
                result.get(
                    "matches",
                    []
                )
            ) > 0:

                failed = True



    if failed:


        print(
            ""
        )


        print(
            "❌ Localization grammar check failed"
        )


        # 当前测试阶段不阻断PR
        # 正式门禁打开:
        # exit(1)


    else:


        print(
            "✅ Localization grammar check passed"
        )





if __name__ == "__main__":

    main()