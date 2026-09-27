from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.exceptions import ComicCraftError
from app.schemas import ComicResponse, HealthResponse, PromptRequest
from app.services.comic_service import generate_comic
from app.services.image_generator import generate_image


router = APIRouter()


# ---------------------------------------------------------
# Project directories
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
PANELS_DIR = STATIC_DIR / "panels"
EXPORTS_DIR = STATIC_DIR / "exports"


# Make sure required folders exist
PANELS_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


# Jinja templates
templates = Jinja2Templates(
    directory=str(TEMPLATES_DIR)
)


# ---------------------------------------------------------
# Error helper
# ---------------------------------------------------------

def _friendly_error(exc: Exception) -> str:
    """
    Convert application errors into a user-friendly message.
    """

    if isinstance(exc, ComicCraftError):
        return str(exc)

    return f"Unexpected error: {exc}"


# ---------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------

@router.get(
    "/",
    response_class=HTMLResponse,
)
async def home(request: Request):
    """
    Display ComicCraft homepage.
    """

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "error": None,
            "settings": get_settings(),
        },
    )


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@router.get(
    "/health",
    response_model=HealthResponse,
)
async def health():
    """
    Check whether ComicCraft backend is running.
    """

    settings = get_settings()

    return HealthResponse(
        status="ok",
        gemini_configured=bool(settings.gemini_api_key),
        image_model=settings.sd_model_id,
    )


# ---------------------------------------------------------
# GENERATE COMIC FROM HTML FORM
# ---------------------------------------------------------

@router.post(
    "/generate",
    response_class=HTMLResponse,
)
async def generate_form(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    """
    Receive comic form data and generate the complete comic.
    """

    try:
        payload = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

        layout, pdf_url = await run_in_threadpool(
            generate_comic,
            payload,
        )

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "layout": layout,
                "pdf_url": pdf_url,
                "error": None,
            },
        )

    except Exception as exc:
        error_message = _friendly_error(exc)

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": error_message,
                "settings": get_settings(),
            },
            status_code=500,
        )


# ---------------------------------------------------------
# GENERATE COMIC JSON API
# ---------------------------------------------------------

@router.post(
    "/generate-comic/json",
    response_model=ComicResponse,
)
async def generate_comic_json(
    payload: PromptRequest,
):
    """
    JSON API endpoint for generating a comic.
    """

    try:
        layout, pdf_url = await run_in_threadpool(
            generate_comic,
            payload,
        )

        return ComicResponse(
            panels=layout,
            pdf_url=pdf_url,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=_friendly_error(exc),
        ) from exc


# ---------------------------------------------------------
# TEST IMAGE GENERATION
# ---------------------------------------------------------

@router.get("/test-image")
async def test_image(
    prompt: str = (
        "A brave fox exploring an enchanted forest, "
        "beautiful fantasy comic book art, "
        "cinematic lighting, highly detailed"
    ),
):
    """
    Test the image-generation system independently.
    """

    try:
        image_url = await run_in_threadpool(
            generate_image,
            prompt,
            0,
        )

        return {
            "success": True,
            "image_url": image_url,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=_friendly_error(exc),
        ) from exc


# ---------------------------------------------------------
# EXPORT SUCCESS PAGE
# ---------------------------------------------------------

@router.get(
    "/export-success",
    response_class=HTMLResponse,
)
async def export_success(
    request: Request,
    pdf_url: str = "",
):
    """
    Display PDF export success page.
    """

    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "pdf_url": pdf_url,
        },
    )


# ---------------------------------------------------------
# DOWNLOAD PDF
# ---------------------------------------------------------

@router.get("/download/{filename}")
async def download_pdf(
    filename: str,
):
    """
    Safely download a generated PDF.
    """

    # Prevent path traversal
    if Path(filename).name != filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename.",
        )

    # Only PDF files are allowed
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files can be downloaded.",
        )

    export_root = EXPORTS_DIR.resolve()
    pdf_path = (EXPORTS_DIR / filename).resolve()

    # Make sure the file stays inside exports directory
    if export_root not in pdf_path.parents:
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF path.",
        )

    # Check file exists
    if not pdf_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="PDF not found.",
        )

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=pdf_path.name,
    )