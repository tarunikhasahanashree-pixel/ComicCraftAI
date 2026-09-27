
from pydantic import BaseModel, Field
from typing import List, Optional


class PromptRequest(BaseModel):
    story_prompt: str = Field(..., min_length=3, max_length=2000)
    character_name: str = Field(default="Hero", max_length=100)
    setting: str = Field(default="Fantasy world", max_length=200)
    tone: str = Field(default="Adventure", max_length=100)
    art_style: str = Field(default="Comic book", max_length=100)


class ComicPanel(BaseModel):
    panel_number: int
    title: str = ""
    narration: str = ""
    dialogue: str = ""
    image_prompt: str = ""
    image_url: Optional[str] = None


class ComicResponse(BaseModel):
    title: str = "Untitled Comic"
    genre: str = "Fantasy"
    summary: str = ""
    panels: List[ComicPanel] = Field(default_factory=list)
    pdf_url: Optional[str] = None


class HealthResponse(BaseModel):
    status: str = "ok"
    gemini_configured: bool = False
    image_model: str = ""