"""Pydantic schemas used for validating API requests/responses."""

from pydantic import BaseModel, Field


class PromptRequest(BaseModel):
    """Schema for the JSON API comic-generation endpoint (/generate-comic/json)."""

    story_prompt: str = Field(..., description="Main idea for the comic.")
    character_name: str = Field(..., description="Name of the comic's hero.")
    setting: str = Field(..., description="Where the story takes place, e.g. forest, city.")
    tone: str = Field(..., description="Mood of the story, e.g. dramatic, funny.")
    art_style: str = Field(..., description="Visual style, e.g. anime, realistic.")


class Panel(BaseModel):
    """A single fully-built comic panel, ready for rendering/export."""

    panel_number: int
    title: str
    scene_description: str
    image_prompt: str
    image_path: str
    caption: str = ""
    narration: str = ""
