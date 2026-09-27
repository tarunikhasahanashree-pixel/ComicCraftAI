
import os
from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    def __init__(self):
        self.app_name = os.getenv("APP_NAME", "ComicCraft")
        self.app_env = os.getenv("APP_ENV", "development")
        self.host = os.getenv("HOST", "127.0.0.1")
        self.port = int(os.getenv("PORT", "8000"))
        self.log_level = os.getenv("LOG_LEVEL", "info")

        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.gemini_outline_model = os.getenv(
            "GEMINI_OUTLINE_MODEL", "gemini-2.5-flash"
        )
        self.gemini_story_model = os.getenv(
            "GEMINI_STORY_MODEL", "gemini-2.5-pro"
        )

        self.hf_api_key = os.getenv("HF_API_KEY", "")
        self.sd_model_id = os.getenv(
            "SD_MODEL_ID", "runwayml/stable-diffusion-v1-5"
        )
        self.sd_device = os.getenv("SD_DEVICE", "auto")
        self.sd_dtype = os.getenv("SD_DTYPE", "auto")
        self.sd_steps = int(os.getenv("SD_STEPS", "25"))
        self.sd_guidance_scale = float(
            os.getenv("SD_GUIDANCE_SCALE", "7.5")
        )
        self.sd_width = int(os.getenv("SD_WIDTH", "512"))
        self.sd_height = int(os.getenv("SD_HEIGHT", "512"))

        self.comic_panels = int(os.getenv("COMIC_PANELS", "5"))
        self.max_story_prompt_length = int(
            os.getenv("MAX_STORY_PROMPT_LENGTH", "2000")
        )
        self.max_field_length = int(
            os.getenv("MAX_FIELD_LENGTH", "120")
        )


@lru_cache(maxsize=1)
def get_settings():
    return Settings()