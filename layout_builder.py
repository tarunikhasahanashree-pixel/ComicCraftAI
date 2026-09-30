"""Combines the outline, narration, and generated images into a single,
ordered comic layout ready for the frontend and the PDF exporter.
"""


def build_comic_layout(outline: list[dict], story_panels: list[dict], image_paths: dict[int, str]) -> list[dict]:
    """Merge per-panel outline + narration + image path into one structure.

    Args:
        outline: list of dicts from gemini_flash.generate_outline()
        story_panels: list of dicts from gemini_pro.generate_story()
        image_paths: mapping of panel_number -> image path (relative to static/)

    Returns:
        A list of dicts (one per panel, sorted by panel_number) each with:
        panel_number, title, scene_description, image_prompt, image_path,
        caption, narration.
    """
    story_by_number = {p["panel_number"]: p for p in story_panels}

    layout = []
    for panel in outline:
        number = panel["panel_number"]
        story = story_by_number.get(number, {})
        layout.append(
            {
                "panel_number": number,
                "title": panel.get("title", f"Panel {number}"),
                "scene_description": panel.get("scene_description", ""),
                "image_prompt": panel.get("image_prompt", ""),
                "image_path": image_paths.get(number, ""),
                "caption": story.get("caption", ""),
                "narration": story.get("narration", ""),
            }
        )

    layout.sort(key=lambda p: p["panel_number"])
    return layout
