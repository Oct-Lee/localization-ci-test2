import subprocess
import requests
import sys
import os



LANGUAGETOOL_URL = (
    "https://api.languagetool.org/v2/check"
)



def changed_files():


    try:

        result = subprocess.check_output(
            [
                "git",
                "diff",
                "--name-only",
                "HEAD^",
                "HEAD"
            ],
            text=True
        )


    except subprocess.CalledProcessError:


        print(
            "No previous commit found."
        )


        result = subprocess.check_output(
            [
                "git",
                "ls-files"
            ],
            text=True
        )


    files = []


    for file in result.splitlines():

        if file.endswith(
            (
                ".py",
                ".sh",
                ".md",
                ".txt",
                ".json",
                ".yaml",
                ".yml"
            )
        ):

            files.append(file)


    return files





def extract_text(file):


    try:

        with open(
            file,
            encoding="utf-8"
        ) as f:

            return f.read()


    except Exception:


        return ""





def check_language(
    text,
    language
):


    response = requests.post(

        LANGUAGETOOL_URL,

        data={

            "text": text,

            "language": language

        },

        timeout=60

    )


    return response.json()





def main():


    files = changed_files()


    print(
        "Changed files:"
    )


    for f in files:

        print(
            f
        )



    failed = False



    languages = [

        (
            "en-US",
            "English"
        ),

        (
            "zh-CN",
            "Chinese"
        ),

        (
            "pt-PT",
            "Portuguese"
        )

    ]



    for file in files:


        text = extract_text(file)


        if not text:

            continue



        for lang,name in languages:


            result = check_language(
                text,
                lang
            )


            matches = result.get(
                "matches",
                []
            )


            for item in matches:


                failed = True


                print(
                    ""
                )


                print(
                    "File:",
                    file
                )


                print(
                    "Language:",
                    name
                )


                print(
                    "Message:",
                    item.get(
                        "message"
                    )
                )


                print(
                    "Context:",
                    item.get(
                        "context",
                        {}
                    ).get(
                        "text"
                    )
                )


                print(
                    "Suggestion:",
                    item.get(
                        "replacements",
                        []
                    )[:3]
                )



    if failed:


        print(
            ""
        )

        print(
            "Localization quality check failed."
        )


        sys.exit(1)



    print(
        "Localization quality check passed."
    )





if __name__ == "__main__":

    main()