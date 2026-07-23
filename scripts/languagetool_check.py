import subprocess
import requests
import sys
import os



LANGUAGETOOL_URL = (
    "https://api.languagetool.org/v2/check"
)



CHECK_EXTENSIONS = (

    ".py",
    ".sh",
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml"

)



def changed_files():


    before = os.environ.get(
        "GITHUB_EVENT_BEFORE"
    )


    after = os.environ.get(
        "GITHUB_SHA"
    )


    if before:


        cmd = [

            "git",
            "diff",
            "--name-only",
            before,
            after

        ]


    else:


        cmd = [

            "git",
            "diff",
            "--name-only",
            "HEAD~1",
            "HEAD"

        ]



    try:

        result = subprocess.check_output(
            cmd,
            text=True
        )

    except Exception:


        print(
            "Cannot get git diff"
        )

        return []



    files=[]


    for f in result.splitlines():

        if f.endswith(
            CHECK_EXTENSIONS
        ):

            files.append(f)



    return files





def extract_text(files):


    content=""


    for f in files:


        try:


            with open(
                f,
                encoding="utf-8"
            ) as fd:


                content += "\n" + fd.read()


        except Exception:


            pass



    return content





def check_language(
    text,
    language
):


    data={

        "text":text,

        "language":language

    }



    try:


        response=requests.post(

            LANGUAGETOOL_URL,

            data=data,

            timeout=30

        )


        print(
            "LanguageTool status:",
            response.status_code
        )


        if response.status_code != 200:


            print(
                response.text[:500]
            )

            return None



        return response.json()



    except Exception as e:


        print(
            "LanguageTool error:",
            e
        )


        return None





def report(
    result,
    language
):


    if not result:

        return



    matches=result.get(
        "matches",
        []
    )



    if not matches:

        print(
            language,
            "OK"
        )

        return



    print(
        "\nLanguage:",
        language
    )


    for item in matches:


        print(
            "Problem:",
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
            [
                x.get("value")
                for x in item.get(
                    "replacements",
                    []
                )[:3]
            ]
        )


        print(
            "------"
        )





def main():


    files=changed_files()


    print(
        "Changed files:",
        files
    )


    if not files:


        print(
            "No files"
        )

        return



    text=extract_text(
        files
    )



    if not text.strip():

        return



    for lang in [

        "en-US",

        "zh-CN",

        "pt-PT"

    ]:


        result=check_language(

            text,

            lang

        )


        report(

            result,

            lang

        )




if __name__=="__main__":

    main()