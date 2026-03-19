from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "sdf_logo.png"


def font(size: int):
    try:
        return ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", size)
    except Exception:
        return ImageFont.load_default()


def main() -> None:
    img = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Document
    d.rounded_rectangle((28, 28, 418, 484), radius=46, fill="#eef7f3", outline="#1d3344", width=14)
    d.polygon([(360, 28), (484, 152), (418, 152), (418, 28)], fill="#eef7f3", outline="#1d3344")
    d.line([(360, 28), (360, 92), (418, 152)], fill="#1d3344", width=14)

    # Graph mark
    nodes = {
        "left": (142, 172),
        "right": (308, 162),
        "bottom": (228, 280),
    }
    colors = {
        "left": "#0f7661",
        "right": "#3d6fb3",
        "bottom": "#de8457",
    }
    d.line([nodes["left"], nodes["right"], nodes["bottom"], nodes["left"]], fill="#1d3344", width=16, joint="curve")
    for key, (x, y) in nodes.items():
        d.ellipse((x - 26, y - 26, x + 26, y + 26), fill=colors[key])

    # SDF label
    d.rounded_rectangle((56, 354, 336, 458), radius=28, fill="#c93f3f")
    f = font(92)
    text = "SDF"
    bbox = d.textbbox((0, 0), text, font=f)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    d.text((196 - tw / 2, 406 - th / 2), text, fill="#f7fbff", font=f)

    img.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
