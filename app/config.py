"""Centralized environment / configuration loading for ComicCraft."""

import os

from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
HF_API_KEY = os.getenv("HF_API_KEY", "")
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() in ("1", "true", "yes")
SD_DEVICE = os.getenv("SD_DEVICE", "cpu")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
PANELS_DIR = os.path.join(STATIC_DIR, "panels")
EXPORTS_DIR = os.path.join(STATIC_DIR, "exports")

os.makedirs(PANELS_DIR, exist_ok=True)
os.makedirs(EXPORTS_DIR, exist_ok=True)
