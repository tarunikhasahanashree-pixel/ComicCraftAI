
import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is missing from your .env file")

client = genai.Client(api_key=API_KEY)


def generate_outline(prompt: str) -> list:
    """Generate a comic story outline using Gemini."""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"""
Create a short comic story based on this idea:

{prompt}

Return ONLY valid JSON in this format:

{{
    "title": "Comic title",
    "panels": [
        {{
            "title": "Panel title",
            "narration": "Panel description",
            "dialogue": "Character dialogue",
            "image_prompt": "Visual description for the panel"
        }}
    ]
}}

Requirements:
- Create 4 to 6 panels.
- Make the story interesting and coherent.
- Include a visual description for each panel.
- Return only JSON, without Markdown code fences.
"""
    )

    response_text = (response.text or "").strip()

    # Remove Markdown code fences if present
    if response_text.startswith("```"):
        response_text = response_text.replace("```json", "", 1)
        response_text = response_text.replace("```", "").strip()

    try:
        data = json.loads(response_text)

        if not isinstance(data, dict):
            raise ValueError("Expected a JSON object")

        panels = data.get("panels", [])

        if not isinstance(panels, list) or not panels:
            raise ValueError("No panels returned by Gemini")

        return [
            {
                "title": str(panel.get("title", f"Panel {i + 1}")),
                "narration": str(panel.get("narration", panel.get("description", ""))),
                "dialogue": str(panel.get("dialogue", "")),
                "image_prompt": str(panel.get("image_prompt", panel.get("description", "")))
            }
            for i, panel in enumerate(panels)
            if isinstance(panel, dict)
        ]

    except (json.JSONDecodeError, ValueError, TypeError) as error:
        raise ValueError(
            f"Gemini returned an invalid comic outline: {error}"
        ) from error
