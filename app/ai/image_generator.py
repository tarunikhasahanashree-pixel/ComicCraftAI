"""Comic-panel illustration generation using Hugging Face Diffusers /
Stable Diffusion (runwayml/stable-diffusion-v1-5).

generate_image() is the single entry point used by the rest of the app.
The real Stable Diffusion pipeline is loaded lazily (only on first real
call) since the model weights are several GB and take real time to load --
we don't want that cost paid at import time or in DEMO_MODE.
"""

import os
import re
import textwrap
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

from app.config import DEMO_MODE, HF_API_KEY, PANELS_DIR, SD_DEVICE

_pipeline = None  # lazily-initialized StableDiffusionPipeline, cached across calls

MODEL_ID = "runwayml/stable-diffusion-v1-5"


def _sanitize_filename(prompt: str, panel_number: int) -> str:
    """Turn a free-text prompt into a short, filesystem-safe filename."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", prompt.strip().lower()).strip("_")[:40] or "panel"
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    return f"panel{panel_number}_{slug}_{timestamp}.png"


def _load_pipeline():
    """Load the Stable Diffusion pipeline once and cache it."""
    global _pipeline
    if _pipeline is not None:
        return _pipeline

    import torch
    from diffusers import StableDiffusionPipeline

    dtype = torch.float16 if SD_DEVICE in ("cuda", "mps") else torch.float32
    pipe = StableDiffusionPipeline.from_pretrained(
        MODEL_ID, torch_dtype=dtype, token=HF_API_KEY or None
    )
    pipe = pipe.to(SD_DEVICE)
    _pipeline = pipe
    return _pipeline


def _demo_image(prompt: str, art_style: str, panel_number: int, out_path: str) -> None:
    """Draw a fast, offline placeholder image so the full pipeline can be
    exercised without a GPU or a Stable Diffusion download.
    """
    width, height = 640, 480
    palette = [
        (255, 214, 165), (168, 218, 220), (202, 240, 248),
        (255, 173, 173), (189, 224, 254), (255, 214, 224),
    ]
    bg = palette[panel_number % len(palette)]
    img = Image.new("RGB", (width, height), color=bg)
    draw = ImageDraw.Draw(img)
    draw.rectangle([8, 8, width - 8, height - 8], outline=(30, 30, 30), width=6)

    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 26)
        font_body = ImageFont.truetype("DejaVuSans.ttf", 18)
    except Exception:
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()

    draw.text((24, 24), f"Panel {panel_number} ({art_style})", font=font_title, fill=(20, 20, 20))
    wrapped = textwrap.fill(prompt, width=42)
    draw.multiline_text((24, 80), wrapped, font=font_body, fill=(40, 40, 40), spacing=6)
    draw.text(
        (24, height - 36),
        "DEMO MODE placeholder — enable real generation in .env",
        font=font_body,
        fill=(90, 90, 90),
    )
    img.save(out_path)


def generate_image(
    image_prompt: str, art_style: str, panel_number: int, require_real: bool = False
) -> str:
    """Generate a comic-style illustration for one panel.

    Saves the image under static/panels/ and returns a path relative to
    static/ (e.g. "panels/panel1_xxx.png") suitable for use in Jinja2
    templates as /static/<that path>.
    """
    filename = _sanitize_filename(image_prompt, panel_number)
    out_path = os.path.join(PANELS_DIR, filename)
    full_prompt = f"{art_style} style comic panel, {image_prompt}, comic book illustration"

    # Ensure the panels directory exists
    os.makedirs(PANELS_DIR, exist_ok=True)
    
    if DEMO_MODE and not require_real:
        _demo_image(full_prompt, art_style, panel_number, out_path)
        return f"panels/{filename}"

    try:
        pipe = _load_pipeline()
        result = pipe(
            full_prompt,
            num_inference_steps=12,
            width=384,
            height=384,
        )
        image = result.images[0]
        image.save(out_path)
    except Exception as exc:
        if require_real:
            raise RuntimeError(
                "Could not generate the required real panel image. Check internet access, "
                "Hugging Face model access, and SD_DEVICE settings."
            ) from exc
        # If the real model isn't available (no GPU, missing weights, no
        # internet, etc.) fall back to the placeholder rather than crashing
        # the whole comic-generation request.
        _demo_image(full_prompt, art_style, panel_number, out_path)

    return f"panels/{filename}"
