
from pathlib import Path
from PIL import Image, ImageDraw


def generate_image(description, panel_number=0):
    output_dir = Path("static/panels")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"panel_{panel_number + 1}.png"

    image = Image.new("RGB", (800, 600), "white")
    draw = ImageDraw.Draw(image)

    draw.text(
        (40, 40),
        description[:500],
        fill="black"
    )

    image.save(output_path)
    return str(output_path)


def create_placeholder(description, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    image = Image.new("RGB", (800, 600), "white")
    draw = ImageDraw.Draw(image)
    draw.text((40, 40), description[:500], fill="black")
    image.save(output_path)

    return str(output_path)
