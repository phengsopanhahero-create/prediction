"""Image loading and preprocessing.

Everything here is deterministic image processing (no ML) and is kept when the
real models are connected: the same ``prepare_model_input`` resize/crop must be
used by the backend so training and inference stay consistent.
"""

from __future__ import annotations

import io

import numpy as np
from PIL import Image, ImageFilter, ImageOps

from config import MODEL_INPUT_SIZE
from services.types import ImageProfile


class InvalidImageError(ValueError):
    """Raised when uploaded bytes are not a decodable image."""


def load_image(data: bytes) -> Image.Image:
    try:
        image = Image.open(io.BytesIO(data))
        image.load()
    except Exception as exc:  # noqa: BLE001 - Pillow raises many types
        raise InvalidImageError("The file could not be read as an image.") from exc
    image = ImageOps.exif_transpose(image)
    if image.mode in ("RGBA", "LA", "P"):
        rgba = image.convert("RGBA")
        background = Image.new("RGB", rgba.size, (255, 255, 255))
        background.paste(rgba, mask=rgba.getchannel("A"))
        return background
    return image.convert("RGB")


def prepare_model_input(image: Image.Image, size: tuple[int, int] = MODEL_INPUT_SIZE) -> Image.Image:
    """Centre-crop to square and resize - the EfficientNetB0 input contract."""
    return ImageOps.fit(image, size, method=Image.BICUBIC, centering=(0.5, 0.5))


def edge_energy_map(image: Image.Image, size: int = 320) -> Image.Image:
    """Edge-magnitude map: a proxy for the low-level features a CNN responds to."""
    gray = ImageOps.fit(image, (size, size)).convert("L")
    edges = gray.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(1.2))
    return ImageOps.autocontrast(edges, cutoff=1)


def average_hash(image: Image.Image, hash_size: int = 8) -> str:
    small = image.convert("L").resize((hash_size, hash_size), Image.BILINEAR)
    pixels = np.asarray(small, dtype=float)
    bits = (pixels > pixels.mean()).flatten()
    return f"{int(''.join('1' if b else '0' for b in bits), 2):016x}"


def hamming_distance(hash_a: str, hash_b: str) -> int:
    return bin(int(hash_a, 16) ^ int(hash_b, 16)).count("1")


def _dominant_colors(image: Image.Image, k: int = 5) -> tuple[tuple[str, float], ...]:
    small = image.copy()
    small.thumbnail((160, 160))
    quantized = small.quantize(colors=k, method=Image.Quantize.MEDIANCUT)
    palette = quantized.getpalette() or []
    counts = sorted(quantized.getcolors() or [], reverse=True)
    total = sum(c for c, _ in counts) or 1
    colors = []
    for count, idx in counts[:k]:
        r, g, b = palette[idx * 3: idx * 3 + 3]
        colors.append((f"#{r:02X}{g:02X}{b:02X}", count / total))
    return tuple(colors)


def profile_image(image: Image.Image, file_size_bytes: int) -> ImageProfile:
    luminance = np.asarray(image.convert("L"), dtype=float) / 255.0
    histogram, _ = np.histogram(luminance, bins=32, range=(0.0, 1.0))
    return ImageProfile(
        width=image.width,
        height=image.height,
        mode=image.mode,
        file_size_kb=file_size_bytes / 1024,
        brightness=float(luminance.mean()),
        contrast=float(luminance.std()),
        dominant_colors=_dominant_colors(image),
        luminance_histogram=tuple(int(v) for v in histogram),
        fingerprint=average_hash(image),
    )
