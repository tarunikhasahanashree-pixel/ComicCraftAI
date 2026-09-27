
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw


def create_comic_page(panel_paths, output_path):
    panel_width = 400
    panel_height = 300
    columns = 2
    rows = (len(panel_paths) + columns - 1) // columns

    page = Image.new(
        "RGB",
        (columns * panel_width, rows * panel_height),
        "white"
    )

    for index, path in enumerate(panel_paths):
        image = Image.open(path).convert("RGB")
        image = ImageOps.fit(
            image,
            (panel_width, panel_height)
        )

        x = (index % columns) * panel_width
        y = (index // columns) * panel_height
        page.paste(image, (x, y))

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    page.save(output_path)

    return str(output_path)