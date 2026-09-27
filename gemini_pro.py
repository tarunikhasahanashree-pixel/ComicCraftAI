
from app.services.gemini_client import client
from app.config import get_settings


def improve_story(story):
    settings = get_settings()

    response = client.models.generate_content(
        model=settings.gemini_story_model,
        contents=f"""
Improve this comic story. Make it engaging and
suitable for a comic book.

Keep the story's main events and characters.

Story:
{story}

Return the improved story only.
"""
    )

    return response.text