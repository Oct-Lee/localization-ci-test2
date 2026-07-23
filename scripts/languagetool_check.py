import requests
import subprocess
import re
import sys


def changed_files():

    result = subprocess.check_output(
        [
            "git",
            "diff",
            "--name-only",
            "HEAD~1",
            "HEAD"
        ]
    )

    return [
        x
        for x in result.decode().splitlines()
        if x.endswith(
            (
                ".py",
                ".sh",
                ".cpp",
                ".h"
            )
        )
    ]



def extract_strings(files):

    results=[]


    pattern=re.compile(
        r'"([^"]+)"'
    )


    for file in files:


        try:

            with open(
                file,
                encoding="utf-8"
            ) as f:


                for lineno,line in enumerate(
                    f,
                    1
                ):


                    matches=pattern.findall(
                        line
                    )


                    for text in matches:


                        # ignore paths
                        if "/" in text:
                            continue


                        # ignore shell variables
                        if "$" in text:
                            continue


                        results.append(
                            {
                                "file":file,
                                "line":lineno,
                                "text":text
                            }
                        )


        except Exception as e:

            print(
                "Skip",
                file,
                e
            )


    return results



files=changed_files()


print(
    "Files:",
    files
)


texts=extract_strings(
    files
)


failed=False



languages=[

    "en-US",

    "zh-CN",

    "pt-PT"

]



for item in texts:


    print(
        "\nChecking:",
        item["file"],
        item["line"]
    )


    print(
        item["text"]
    )



    for lang in languages:


        response=requests.post(

            "http://localhost:8010/v2/check",

            data={

                "language":lang,

                "text":item["text"]

            },

            timeout=60

        )


        data=response.json()



        for error in data.get(
            "matches",
            []
        ):


            failed=True


            print(
                "Language:",
                lang
            )


            print(
                "Problem:",
                error["message"]
            )


            print(
                "Context:",
                error["context"]["text"]
            )


            print(
                "Suggestion:",
                [
                    x["value"]
                    for x in error.get(
                        "replacements",
                        []
                    )[:5]
                ]
            )



if failed:


    sys.exit(
        1
    )


print(
    "\nLocalization check passed"
)
