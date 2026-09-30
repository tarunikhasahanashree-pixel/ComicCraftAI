"""Panel-outline generation using Google's Gemini Flash model.

generate_outline() turns a user's story prompt into a structured, 5-panel
comic outline: one dict per panel with a title, scene description, and an
image-generation prompt.
"""

import json
import re

import google.generativeai as genai

from app.config import DEMO_MODE, GEMINI_API_KEY

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

MODEL_NAME = "models/gemini-1.5-flash"
NUM_PANELS = 5


def _demo_outline(story_prompt: str, character_name: str, setting: str, tone: str) -> list[dict]:
    """Offline fallback outline used when DEMO_MODE is on or no API key is set."""
    beats = [
        "sets the scene and introduces the world",
        "meets the first challenge",
        "discovers something unexpected",
        "faces the biggest obstacle yet",
        "resolves the story with a satisfying finish",
    ]
    panels = []
    for i, beat in enumerate(beats, start=1):
        panels.append(
            {
                "panel_number": i,
                "title": f"Panel {i}: {character_name} {beat}",
                "scene_description": (
                    f"{character_name} is in {setting}, in a {tone} moment where they {beat}. "
                    f"Inspired by the prompt: \"{story_prompt}\"."
                ),
                "image_prompt": (
                    f"{tone} comic panel, {character_name} in {setting}, {beat}, "
                    "dynamic composition, comic book illustration"
                ),
            }
        )
    return panels


def _extract_json(text: str) -> str:
    """Pull a JSON array out of a model response that may include prose or code fences."""
    fenced = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", text, re.DOTALL)
    if fenced:
        return fenced.group(1)
    bracket = re.search(r"(\[.*\])", text, re.DOTALL)
    if bracket:
        return bracket.group(1)
    return text


def generate_outline(story_prompt: str, character_name: str, setting: str, tone: str) -> list[dict]:
    """Generate a structured NUM_PANELS-panel comic outline.

    Returns a list of dicts, each with: panel_number, title,
    scene_description, image_prompt.
    """
    if DEMO_MODE or not GEMINI_API_KEY:
        return _demo_outline(story_prompt, character_name, setting, tone)

    model = genai.GenerativeModel(MODEL_NAME)
    system_instruction = (
        f"You are a comic book outline writer. Create a {NUM_PANELS}-panel comic outline "
        "as a strict JSON array. Each element must be an object with exactly these keys: "
        '"panel_number" (int), "title" (string), "scene_description" (string), '
        '"image_prompt" (string, a vivid visual description suitable for an image generator). '
        "Return ONLY the JSON array, no extra commentary."
    )
    user_prompt = (
        f"Story idea: {story_prompt}\n"
        f"Main character: {character_name}\n"
        f"Setting: {setting}\n"
        f"Tone: {tone}\n"
    )

    try:
        response = model.generate_content([system_instruction, user_prompt])
        raw = _extract_json(response.text)
        outline = json.loads(raw)
        if not isinstance(outline, list) or not outline:
            raise ValueError("Gemini Flash did not return a valid panel list.")
        return outline
    except Exception:
        # Any API, parsing, or quota failure falls back to the offline outline
        # so the rest of the pipeline (and the demo) still works.
        return _demo_outline(story_prompt, character_name, setting, tone)
