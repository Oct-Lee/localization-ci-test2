import json
import os
import requests


api_key = os.environ["CURSOR_API_KEY"]


payload = {
    "prompt": {
        "text": "Review this text for localization issues: camera not Founded"
    }
}


response = requests.post(
    "https://api.cursor.com/v1/agents",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    json=payload,
    timeout=60,
)


print(response.status_code)
print(response.text)
