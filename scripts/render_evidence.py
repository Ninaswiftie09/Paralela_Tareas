from pathlib import Path
import textwrap
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parents[1]
font_path = Path("C:/Windows/Fonts/consola.ttf")
font = ImageFont.truetype(str(font_path), 21) if font_path.exists() else ImageFont.load_default(size=21)
for name in ["compile", "sequential", "parallel", "optimized", "hardware"]:
    content = (root / "evidence" / f"{name}.txt").read_text(encoding="utf-8")
    lines = ["Registro de salida real de terminal", ""]
    for line in content.splitlines():
        lines.extend(textwrap.wrap(line, width=106, replace_whitespace=False) or [""])
    image = Image.new("RGB", (1400, 40 + 30 * len(lines)), "#101820")
    draw = ImageDraw.Draw(image)
    for i, line in enumerate(lines):
        draw.text((22, 18 + 30 * i), line, fill="#edf3f7", font=font)
    image.save(root / "evidence" / f"{name}.png")
