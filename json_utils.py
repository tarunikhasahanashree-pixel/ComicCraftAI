import json
import re


def clean_json(text):

    text = text.strip()

    # Remove markdown code blocks
    text = re.sub(r"json", "", text)
    text = re.sub(r"", "", text)

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        return {
            "title": "Generated Comic",
            "panels": [
                {
                    "description": text,
                    "dialogue": ""
                }
            ]
        }