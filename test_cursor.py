#!/usr/bin/env python3

import json
import os
import sys
import requests


api_key = os.environ.get("CURSOR_API_KEY")

if not api_key:
    print("Missing CURSOR_API_KEY")
    sys.exit(1)


payload = {
    "prompt": {
        "text": """
You are a professional localization quality reviewer.

Review the following user-facing text.

Check:

1. English spelling mistakes
2. English grammar problems
3. User-facing wording quality
4. Localization issues


Text:

camera[{camera_id}] not Founded.

Please check whether the camera_id parameter of the configration file is correct.


Output format:

Severity:
Issue:
Original:
Suggestion:
Reason:
"""
    }
}


print("Request payload:")
print(json.dumps(payload, indent=2))


response = requests.post(
    "https://api.cursor.com/v1/agents",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    json=payload,
    timeout=60,
)


print()
print("Status:", response.status_code)

try:
    print(
        json.dumps(
            response.json(),
            indent=2,
            ensure_ascii=False,
        )
    )
except Exception:
    print(response.text)
