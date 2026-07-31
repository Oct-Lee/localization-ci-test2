import os
import requests
import json


api_key = os.environ["GEMINI_API_KEY"]


url = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/"
    "gemini-3.6-flash:generateContent"
    f"?key={api_key}"
)


prompt = """
You are a localization quality reviewer.

Check this message:

CAMERA_NOT_FOUND_ERROR = (
    "camera[{camera_id}] not Founded. "
    "Please check whether the camera_id parameter "
    "of the configration file is correct"
)

Find:
1. Grammar issue
2. Spelling issue
3. Suggested correction
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


print("HTTP Status:")
print(response.status_code)


print("Response:")
print(
    json.dumps(
        response.json(),
        indent=2,
        ensure_ascii=False
    )
)
