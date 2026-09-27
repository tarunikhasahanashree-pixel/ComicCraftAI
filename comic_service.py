
import json
from pathlib import Path

from app.config import get_settings
from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import improve_story
from app.services.image_generator import generate_image
from app.services.layout_builder import create_comic_page
from app.services.exporters import export_pdf


BASE_DIR = Path(__file__).resolve().parents[2]
PANELS_DIR = BASE_DIR / "static" / "panels"
EXPORTS_DIR = BASE_DIR / "static" / "exports"


def generate_comic(payload):
    settings = get_settings()

    PANELS_DIR.mkdir(parents=True, exist_ok=True)
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

    raw_outline = generate_outline(
        payload.story_prompt,
        payload.character_name,
        payload.setting,
        payload.tone,
        payload.art_style,
    )

    try:
        outline = json.loads(raw_outline)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError(
            "Gemini returned an invalid comic outline."
        ) from exc

    if not isinstance(outline, list) or not outline:
        raise ValueError("Gemini returned no comic panels.")

    story_text = "\n".join(
        str(panel.get("narration", ""))
        for panel in outline
        if isinstance(panel, dict)
    )

    improved_story = improve_story(story_text)

    if improved_story.strip():
        outline[0]["narration"] = improved_story

    panel_paths = []
    layout = []

    for index, panel in enumerate(outline):
        if not isinstance(panel, dict):
            continue

        panel_number = index + 1
        image_prompt = panel.get(
            "image_prompt",
            f"{payload.art_style}: {panel.get('narration', '')}"
        )

        image_path = generate_image(
            image_prompt,
            panel_number - 1
        )
        panel["image_url"] = f"/static/panels/panel_{panel_number}.png"
        panel["panel_number"] = panel_number

        panel_paths.append(str(image_path))
        layout.append(panel)

    page_path = EXPORTS_DIR / "comic_page.png"
    create_comic_page(panel_paths, page_path)

    pdf_path = EXPORTS_DIR / "comic.pdf"
    export_pdf(page_path, pdf_path)

    pdf_url = "/download/comic.pdf"

    return layout, pdf_url