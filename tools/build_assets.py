"""Build local static assets for the FashionVision AI frontend.

Usage (from the project root):
    python tools/build_assets.py            # build anything that is missing
    python tools/build_assets.py --force    # rebuild everything

What it does
* Downloads transparent product cut-outs listed in data/mock_products.py and
  places each on a uniform 800x1000 studio canvas (static/images/products).
* Renders flat-lay placeholders for products whose source is ``generated``.
* Renders the sidebar wordmark and favicon (static/brand).

The resulting images are committed to the repository, so running the app never
needs network access.
"""

from __future__ import annotations

import argparse
import io
import sys
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from data.mock_products import PRODUCT_IMAGE_DIR, get_products  # noqa: E402

CANVAS = (800, 1000)
STUDIO_BG = (244, 244, 244)
BRAND_DIR = ROOT / "static" / "brand"
USER_AGENT = {"User-Agent": "FashionVisionAI-student-project/1.0"}


# --------------------------------------------------------------------------- #
# Product photos
# --------------------------------------------------------------------------- #
def download(url: str) -> bytes:
    request = urllib.request.Request(url, headers=USER_AGENT)
    with urllib.request.urlopen(request, timeout=45) as response:
        return response.read()


def place_on_canvas(cutout: Image.Image, fill: float = 0.78) -> Image.Image:
    """Trim transparent margins and centre the product on the studio canvas."""
    rgba = cutout.convert("RGBA")
    bbox = rgba.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
    if bbox:
        rgba = rgba.crop(bbox)
    max_w, max_h = int(CANVAS[0] * fill), int(CANVAS[1] * fill)
    scale = min(max_w / rgba.width, max_h / rgba.height)
    rgba = rgba.resize((max(1, round(rgba.width * scale)), max(1, round(rgba.height * scale))),
                       Image.LANCZOS)
    canvas = Image.new("RGB", CANVAS, STUDIO_BG)
    offset = ((CANVAS[0] - rgba.width) // 2, (CANVAS[1] - rgba.height) // 2)
    canvas.paste(rgba, offset, rgba)
    return canvas


# --------------------------------------------------------------------------- #
# Generated flat-lay pants
# --------------------------------------------------------------------------- #
PANTS_STYLES = {
    #            outer-hem  inner-hem  hip-out  details
    "jeans":    dict(outer=245, inner=386, hip=250, stitch=(201, 162, 94), crease=False, cargo=False),
    "chino":    dict(outer=268, inner=390, hip=254, stitch=None, crease=False, cargo=False),
    "tailored": dict(outer=252, inner=389, hip=252, stitch=None, crease=True, cargo=False),
    "cargo":    dict(outer=230, inner=392, hip=248, stitch=None, crease=False, cargo=True),
}


def _hex(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _shade(rgb: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
    return tuple(max(0, min(255, int(c * factor))) for c in rgb)  # type: ignore[return-value]


def render_pants(style: str, color: str) -> Image.Image:
    s = 2  # supersampling factor
    spec = PANTS_STYLES[style]
    base = _hex(color)
    W, H = CANVAS[0] * s, CANVAS[1] * s

    def P(x: float, y: float) -> tuple[int, int]:
        return int(x * s), int(y * s)

    o, i, hip = spec["outer"], spec["inner"], spec["hip"]
    top, waist_h, hem = 150, 36, 880
    outline = [P(272, top), P(528, top), P(800 - hip, 360), P(800 - o, hem), P(800 - i, hem),
               P(400, 418), P(i, hem), P(o, hem), P(hip, 360)]

    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(outline, fill=255)

    # Fabric: base colour + soft horizontal shading + fine noise.
    x = np.linspace(-1, 1, W)[None, :]
    shading = 1.0 - 0.10 * np.abs(x) ** 1.5
    rng = np.random.default_rng(abs(hash(style)) % (2**32))
    noise = rng.normal(0, 4.5, (H, W, 1))
    fabric = np.clip(np.array(base, dtype=float)[None, None, :] * shading[..., None] + noise, 0, 255)
    fabric_img = Image.fromarray(fabric.astype("uint8"), "RGB")

    canvas = Image.new("RGB", (W, H), STUDIO_BG)
    shadow = mask.filter(ImageFilter.GaussianBlur(18 * s))
    shadow = ImageChops.offset(shadow, 0, 10 * s).point(lambda v: int(v * 0.22))
    canvas.paste(Image.new("RGB", (W, H), (150, 150, 150)), (0, 0), shadow)
    canvas.paste(fabric_img, (0, 0), mask)

    d = ImageDraw.Draw(canvas)
    dark, light = _shade(base, 0.72), _shade(base, 1.18)
    seam = spec["stitch"] or _shade(base, 0.82)
    lw = 2 * s

    # Waistband, belt loops, button.
    d.rectangle([P(272, top), P(528, top + waist_h)], fill=_shade(base, 0.9))
    d.line([P(272, top + waist_h), P(528, top + waist_h)], fill=dark, width=lw)
    for lx in (292, 345, 455, 508):
        d.rectangle([P(lx - 5, top - 2), P(lx + 5, top + waist_h + 6)], fill=_shade(base, 0.84))
    d.ellipse([P(393, top + 11), P(407, top + 25)], fill=(180, 180, 176) if style == "jeans" else dark)

    # Fly and front pockets.
    d.line([P(400, top + waist_h), P(400, 330)], fill=dark, width=lw)
    d.arc([P(368, 250), P(432, 340)], 0, 90, fill=seam, width=lw)
    d.arc([P(252, 120), P(352, 290)], 0, 90, fill=dark, width=lw)
    d.arc([P(448, 120), P(548, 290)], 90, 180, fill=dark, width=lw)

    # Outer seams and hems.
    d.line([P(hip + 4, 360), P(o + 6, hem - 4)], fill=seam, width=lw)
    d.line([P(800 - hip - 4, 360), P(800 - o - 6, hem - 4)], fill=seam, width=lw)
    d.line([P(o + 2, hem - 22), P(i - 2, hem - 22)], fill=seam, width=lw)
    d.line([P(800 - i + 2, hem - 22), P(800 - o - 2, hem - 22)], fill=seam, width=lw)

    if spec["crease"]:
        for side in (1, -1):
            cx_top = 400 - side * 72
            cx_bot = 400 - side * ((o + i) / 2 - 400) * -1
            d.line([P(cx_top, top + waist_h + 4), P(cx_bot, hem)], fill=light, width=lw)
    if spec["cargo"]:
        for side in (1, -1):
            cx = 400 + side * 118
            box = [P(cx - 52, 470), P(cx + 52, 600)]
            d.rectangle(box, outline=dark, width=lw)
            d.rectangle([P(cx - 56, 462), P(cx + 56, 500)], fill=_shade(base, 0.9), outline=dark, width=lw)
    if style == "jeans":
        # Contrast stitching on pockets and whiskering.
        d.arc([P(258, 128), P(358, 296)], 0, 90, fill=seam, width=lw)
        d.arc([P(442, 128), P(542, 296)], 90, 180, fill=seam, width=lw)
        for k in range(3):
            y = 360 + k * 14
            d.line([P(330 - k * 6, y), P(380, y + 18)], fill=light, width=s)
            d.line([P(470 + k * 6, y), P(420, y + 18)], fill=light, width=s)

    return canvas.resize(CANVAS, Image.LANCZOS)


# --------------------------------------------------------------------------- #
# Brand assets
# --------------------------------------------------------------------------- #
def _font(names: list[str], size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size)


def _tracked_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str,
                  font, fill, tracking: int) -> int:
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += int(draw.textlength(ch, font=font)) + tracking
    return x


def render_logo(path: Path) -> None:
    scale = 4
    W, H = 300 * scale, 48 * scale
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    word = _font(["seguisb.ttf", "segoeuib.ttf", "DejaVuSans-Bold.ttf", "arial.ttf"], 22 * scale)
    tag = _font(["segoeuil.ttf", "segoeui.ttf", "DejaVuSans.ttf", "arial.ttf"], 22 * scale)
    y = 11 * scale
    x = _tracked_text(d, (0, y), "FASHIONVISION", word, (245, 245, 245, 255), 3 * scale)
    d.line([(x + 6 * scale, 14 * scale), (x + 6 * scale, 38 * scale)], fill=(110, 110, 110, 255), width=scale)
    _tracked_text(d, (x + 14 * scale, y), "AI", tag, (170, 170, 170, 255), 3 * scale)
    bbox = img.getbbox()
    img.crop((0, 0, bbox[2] + 2 * scale, H)).resize(
        ((bbox[2] + 2 * scale) // 2, H // 2), Image.LANCZOS).save(path)


def render_mark(path: Path, size: int = 128) -> None:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=size // 10, fill=(37, 37, 37, 255))
    font = _font(["seguisb.ttf", "DejaVuSans-Bold.ttf", "arial.ttf"], int(size * 0.42))
    text = "FV"
    w = d.textlength(text, font=font)
    d.text(((size - w) / 2, size * 0.24), text, font=font, fill=(245, 245, 245, 255))
    img.save(path)


# --------------------------------------------------------------------------- #
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--force", action="store_true", help="rebuild images that already exist")
    args = parser.parse_args()

    PRODUCT_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    BRAND_DIR.mkdir(parents=True, exist_ok=True)

    failures = 0
    for product in get_products():
        target = product.image_path
        if target.exists() and not args.force:
            continue
        try:
            if product.source == "generated":
                _, style, color = product.source_ref.split(":")
                image = render_pants(style, color)
            else:
                image = place_on_canvas(Image.open(io.BytesIO(download(product.source_ref))))
            image.save(target, "JPEG", quality=86, optimize=True, progressive=True)
            print(f"  built   {product.id}  {product.name}")
        except Exception as exc:  # noqa: BLE001 - report and continue
            failures += 1
            print(f"  FAILED  {product.id}: {exc}", file=sys.stderr)

    for name, renderer in (("logo.png", render_logo), ("mark.png", render_mark)):
        target = BRAND_DIR / name
        if args.force or not target.exists():
            renderer(target)
            print(f"  built   brand/{name}")

    print("Done." if not failures else f"Done with {failures} failure(s).")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
