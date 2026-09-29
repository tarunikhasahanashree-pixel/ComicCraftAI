"""Comic narration & dialogue generation using Google's Gemini Pro model.

generate_story() expands a panel outline (from gemini_flash.generate_outline)
into full narration, captions, and character dialogue for every panel.
"""

import json
import re

import google.generativeai as genai

from app.config import DEMO_MODE, GEMINI_API_KEY

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

MODEL_NAME = "models/gemini-1.5-pro"


def _demo_story(outline: list[dict], character_name: str, tone: str) -> list[dict]:
    """Offline fallback narration used when DEMO_MODE is on or no API key is set."""
    story_panels = []
    for panel in outline:
        story_panels.append(
            {
                "panel_number": panel["panel_number"],
                "caption": f"The air feels {tone} as the scene unfolds.",
                "narration": (
                    f'{character_name} says, "This is it -- {panel["title"].split(": ", 1)[-1]}." '
                    f"{panel['scene_description']}"
                ),
            }
        )
    return story_panels


def _extract_json(text: str) -> str:
    fenced = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", text, re.DOTALL)
    if fenced:
        return fenced.group(1)
    bracket = re.search(r"(\[.*\])", text, re.DOTALL)
    if bracket:
        return bracket.group(1)
    return text


def generate_story(outline: list[dict], character_name: str, tone: str) -> list[dict]:
    """Expand a panel outline into narration + captions + dialogue per panel.

    Returns a list of dicts, each with: panel_number, caption, narration.
    """
    if DEMO_MODE or not GEMINI_API_KEY:
        return _demo_story(outline, character_name, tone)

    model = genai.GenerativeModel(MODEL_NAME)
    system_instruction = (
        "You are a comic book writer. Given a JSON panel outline, write a "
        f"{tone} narration and short ambient caption for every panel, including "
        "character dialogue where it fits naturally. Respond with ONLY a strict "
        "JSON array where each element has exactly these keys: "
        '"panel_number" (int, matching the input), "caption" (string, one short '
        'ambient line), "narration" (string, 2-4 sentences of narration/dialogue).'
    )
    user_prompt = json.dumps(outline)

    try:
        response = model.generate_content([system_instruction, user_prompt])
        raw = _extract_json(response.text)
        story_panels = json.loads(raw)
        if not isinstance(story_panels, list) or not story_panels:
            raise ValueError("Gemini Pro did not return a valid narration list.")
        return story_panels
    except Exception:
        return _demo_story(outline, character_name, tone)
