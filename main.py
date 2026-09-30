"""ComicCraft FastAPI application entry point.

Run with:
    uvicorn app.main:app --reload

Then visit:
    http://127.0.0.1:8000        -> the app
    http://127.0.0.1:8000/docs   -> interactive API docs
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes import router

app = FastAPI(
    title="ComicCraft",
    description="AI Comic Story Creator using Gemini Models + Stable Diffusion",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)
