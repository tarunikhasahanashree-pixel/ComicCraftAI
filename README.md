# ComicCraft — AI Comic Story Creator

ComicCraft turns a short story prompt into a full, illustrated comic strip.
It uses **Gemini Flash** to outline a 5-panel story, **Gemini Pro** to write
narration and dialogue, and **Stable Diffusion** (via Hugging Face
Diffusers) to illustrate each panel. The finished comic can be previewed in
the browser and downloaded as a PDF.

## Project structure

```
comiccraft/
├── app/
│   ├── main.py            # FastAPI app entry point
│   ├── routes.py          # All routes (/, /generate, /generate-comic/json, ...)
│   ├── models.py          # Pydantic schemas (PromptRequest, Panel)
│   ├── config.py          # Env var / .env loading
│   ├── layout_builder.py  # Merges outline + story + images into one layout
│   ├── exporters.py       # Builds the downloadable PDF (FPDF)
│   └── ai/
│       ├── gemini_flash.py    # generate_outline() — 5-panel story outline
│       ├── gemini_pro.py      # generate_story() — narration & dialogue
│       └── image_generator.py # generate_image() — Stable Diffusion illustrations
├── templates/              # Jinja2 HTML templates
│   ├── index.html
│   ├── comic_preview.html
│   └── export_success.html
├── static/
│   ├── css/style.css
│   ├── panels/              # generated panel images land here
│   └── exports/             # generated PDFs land here
├── requirements.txt
├── .env.example
└── .vscode/                 # launch.json + settings.json for one-click debugging
```

## 1. Open in VS Code

Open the `comiccraft/` folder in VS Code. Install the **Python** extension
if you don't already have it.

## 2. Set up the environment

```bash
python -m venv comiccraft-env

# Windows
comiccraft-env\Scripts\activate
# macOS/Linux
source comiccraft-env/bin/activate

pip install -r requirements.txt
```

In VS Code, select `comiccraft-env` as the Python interpreter
(`Ctrl+Shift+P` → "Python: Select Interpreter").

## 3. Configure your API keys

```bash
cp .env.example .env
```

Then edit `.env`:

- `GEMINI_API_KEY` — from https://ai.google.dev/
- `HF_API_KEY` — from https://huggingface.co/settings/tokens (needed to
  download `runwayml/stable-diffusion-v1-5`)
- `DEMO_MODE` — leave as `true` to use fast, offline placeholder text and
  images for most of the comic. The first panel always uses Stable Diffusion
  to create a small, 384-pixel prompt-related image with fewer sampling steps.
  The first run still downloads several GB of model weights and may take a
  while. Set to `false` to use real
  Gemini + Stable Diffusion generation for all panels.
- `SD_DEVICE` — `cuda` if you have an NVIDIA GPU, `mps` on Apple Silicon,
  otherwise `cpu` (slow but works).

> Stable Diffusion weights are several GB and the first real (non-demo) run
> will download them and can take a while, especially on CPU. `DEMO_MODE`
> is there so you can build/test the full pipeline first.

## 4. Run the app

From the project root, either:

- Press **F5** in VS Code (uses the included `.vscode/launch.json`), or
- Run from the terminal:

  ```bash
  uvicorn app.main:app --reload
  ```

Then open:

- http://127.0.0.1:8000 — the ComicCraft app
- http://127.0.0.1:8000/docs — interactive API docs (Swagger UI)

## API endpoints

| Route                     | Method | Purpose                                              |
| ------------------------- | ------ | ----------------------------------------------------- |
| `/`                       | GET    | Homepage with the story input form                     |
| `/generate`                | POST   | Form submission → runs the full pipeline → comic preview |
| `/generate-comic/json`     | POST   | Same pipeline, JSON in / JSON out (for API clients)    |
| `/download?path=...`       | GET    | Downloads the generated PDF                           |
| `/export-success`          | GET    | Confirmation page shown after download                |
| `/test-image`              | POST   | Test image generation directly from a prompt           |

Example JSON request body for `/generate-comic/json`:

```json
{
  "story_prompt": "A brave fox exploring an enchanted forest",
  "character_name": "Finn",
  "setting": "forest",
  "tone": "dramatic",
  "art_style": "anime"
}
```

## Notes

- All AI calls (`gemini_flash.py`, `gemini_pro.py`, `image_generator.py`)
  fail gracefully: if the API/model call errors out or `DEMO_MODE=true`,
  each module falls back to a fast, deterministic offline result so the
  rest of the pipeline keeps working.
- Generated panel images are saved to `static/panels/`; exported PDFs to
  `static/exports/`. Both are git-ignored except for a `.gitkeep` placeholder.
