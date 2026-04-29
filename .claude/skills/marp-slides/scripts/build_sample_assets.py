"""Generate placeholder images and icons used by the starter deck.

Outputs go into ../assets/images and ../assets/icons. These are intentionally
plain so they look reasonable on light, dark, and warm backgrounds.

Usage:
    python build_sample_assets.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SKILL_ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = SKILL_ROOT / "assets" / "images"
ICONS_DIR = SKILL_ROOT / "assets" / "icons"


def _try_font(size: int) -> ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for c in candidates:
        try:
            return ImageFont.truetype(c, size)
        except OSError:
            continue
    return ImageFont.load_default()


def gradient_image(name: str, c1: tuple[int, int, int], c2: tuple[int, int, int],
                   label: str, size=(1600, 900)) -> None:
    w, h = size
    img = Image.new("RGB", size, c1)
    px = img.load()
    for y in range(h):
        t = y / (h - 1)
        r = int(c1[0] * (1 - t) + c2[0] * t)
        g = int(c1[1] * (1 - t) + c2[1] * t)
        b = int(c1[2] * (1 - t) + c2[2] * t)
        for x in range(w):
            px[x, y] = (r, g, b)

    # Soft circle accent
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.ellipse((w * 0.55, -h * 0.2, w * 1.2, h * 0.7),
               fill=(255, 255, 255, 40))
    overlay = overlay.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    d = ImageDraw.Draw(img)
    font = _try_font(72)
    bbox = d.textbbox((0, 0), label, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((w - tw) / 2, (h - th) / 2), label, fill=(255, 255, 255), font=font)

    out = IMAGES_DIR / name
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)
    print(f"  wrote {out.relative_to(SKILL_ROOT)}")


def icon(name: str, color: tuple[int, int, int], glyph: str, size: int = 256) -> None:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((10, 10, size - 10, size - 10), radius=40, fill=color)
    font = _try_font(int(size * 0.55))
    bbox = d.textbbox((0, 0), glyph, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    # textbbox can include leading; tweak position for visual centering
    d.text(((size - tw) / 2 - bbox[0], (size - th) / 2 - bbox[1]),
           glyph, fill=(255, 255, 255, 255), font=font)
    out = ICONS_DIR / name
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)
    print(f"  wrote {out.relative_to(SKILL_ROOT)}")


def main() -> int:
    print("Building placeholder images:")
    gradient_image("hero-blue.png", (37, 99, 235), (14, 165, 233), "HERO")
    gradient_image("hero-dark.png", (13, 17, 23), (32, 41, 64), "TECH")
    gradient_image("hero-warm.png", (181, 101, 29), (140, 106, 63), "STORY")
    gradient_image("chart-placeholder.png", (245, 245, 245), (220, 220, 220), "CHART")

    print("Building icons:")
    icon("check.png", (16, 185, 129), "✓")
    icon("bolt.png", (245, 158, 11), "⚡")
    icon("target.png", (239, 68, 68), "◎")
    icon("spark.png", (139, 92, 246), "✨")
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
