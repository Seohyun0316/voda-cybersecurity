import os
import requests


API_KEY = os.environ["TRANSLATION_API_KEY"]

API_URL = "https://api.example.com/v1/translate"


def translate(text, target_lang="ko"):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "text": text,
        "target_language": target_lang
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=data
    )

    response.raise_for_status()

    result = response.json()

    return result["translation"]


# Å×½ºÆ®
print(
    translate("Hello world", "ko")
)