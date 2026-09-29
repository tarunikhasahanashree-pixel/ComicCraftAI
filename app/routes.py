"""All ComicCraft FastAPI routes:

/               -> homepage with the story input form
/generate       -> form submission -> full AI pipeline -> comic preview page
/generate-comic/json -> same pipeline, JSON in / JSON out (for API clients)
/download/{comic_id}/{filename} -> triggers the PDF download + export-success
/export-success -> confirmation page shown after a PDF download
/test-image     -> developer utility to test image generation in isolation
"""

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from app.ai.gemini_flash import generate_outline
from app.ai.gemini_pro import generate_story
from app.ai.image_generator import generate_image
from app.config import STATIC_DIR
from app.exporters import save_pdf
from app.layout_builder import build_comic_layout
from app.models import PromptRequest

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def _run_pipeline(story_prompt: str, character_name: str, setting: str, tone: str, art_style: str):
    """Shared pipeline used by both the form route and the JSON API route."""
    outline = generate_outline(story_prompt, character_name, setting, tone)
    story_panels = generate_story(outline, character_name, tone)

    image_paths = {}
    for index, panel in enumerate(outline):
        image_paths[panel["panel_number"]] = generate_image(
            panel["image_prompt"],
            art_style,
            panel["panel_number"],
            require_real=index == 0,
        )

    layout = build_comic_layout(outline, story_panels, image_paths)
    pdf_path = save_pdf(layout, comic_title=f"{character_name}'s Comic")
    return layout, pdf_path


@router.get("/")
async def homepage(request: Request):
    """Loads the homepage where users submit their story details."""
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/generate")
async def generate_comic_form(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    """Handles form submission: runs the full AI pipeline and renders the
    comic preview page.
    """
    try:
        layout, pdf_path = _run_pipeline(story_prompt, character_name, setting, tone, art_style)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Comic generation failed: {exc}") from exc

    return templates.TemplateResponse(
        "comic_preview.html",
        {
            "request": request,
            "layout": layout,
            "pdf_path": pdf_path,
            "character_name": character_name,
        },
    )


@router.post("/generate-comic/json")
async def generate_comic_json(payload: PromptRequest):
    """JSON API equivalent of /generate: accepts a PromptRequest body,
    returns the comic layout data plus the exported PDF path.
    """
    try:
        layout, pdf_path = _run_pipeline(
            payload.story_prompt,
            payload.character_name,
            payload.setting,
            payload.tone,
            payload.art_style,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Comic generation failed: {exc}") from exc

    return {"layout": layout, "pdf_path": pdf_path}


@router.get("/download")
async def download_comic(request: Request, path: str):
    """Serves the generated PDF as a file download, then the frontend
    redirects the user to /export-success.
    """
    full_path = f"{STATIC_DIR}/{path}"
    return FileResponse(full_path, media_type="application/pdf", filename=path.split("/")[-1])


@router.get("/export-success")
async def export_success(request: Request):
    """Displays a success confirmation page after the comic is downloaded."""
    return templates.TemplateResponse("export_success.html", {"request": request})


@router.post("/test-image")
async def test_image(prompt: str = Form(...), art_style: str = Form("comic book")):
    """Developer utility route: test image generation from a direct prompt
    without running the full comic-creation pipeline.
    """
    image_path = generate_image(prompt, art_style, panel_number=0)
    return {"image_path": f"/static/{image_path}"}
