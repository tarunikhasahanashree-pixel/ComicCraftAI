from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI(title="ComicCraft AI")

# Adjust template folder path if needed (e.g. "templates" or "app/templates")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # FIX: Explicitly pass context=... instead of direct positional dict
    return templates.TemplateResponse(
        request=request, 
        name="base.html", 
        context={}
    )


@app.post("/generate", response_class=HTMLResponse)
async def generate_comic(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(None),
    setting: str = Form(None),
    tone: str = Form(...),
    art_style: str = Form(...)
):
    result = {
        "story_prompt": story_prompt,
        "character_name": character_name or "Not specified",
        "setting": setting or "Not specified",
        "tone": tone,
        "art_style": art_style,
        "status": "Comic generated successfully!"
    }

    # FIX: Updated Starlette/FastAPI syntax for TemplateResponse
    return templates.TemplateResponse(
        request=request,
        name="base.html",
        context={"result": result}
    )


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
