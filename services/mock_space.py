"""Deterministic mock embedding space used by the demo services.

There is no trained network here. To make the demo behave plausibly we build a
synthetic 1280-d vector space in which:

* every category has a centroid (centroids share a common component, so
  different categories are still mildly similar - as with real CNN features);
* every catalogue product sits near its category centroid;
* a query image is placed near the centroid of the category the mock
  classifier assigned to it.

Cosine similarity, k-NN ranking and scores are then computed for real on these
vectors, exactly as they will be on real embeddings.

Catalogue images are recognised by a perceptual average-hash so the sample
library returns the correct category in the demo.
"""

from __future__ import annotations

import zlib
from dataclasses import dataclass
from functools import cached_property

import numpy as np
from PIL import Image

from config import EMBEDDING_DIM
from data.mock_products import Product, get_categories, get_products
from services.preprocessing import average_hash, hamming_distance

_GLOBAL_SEED = 20260112
_SHARED_COMPONENT = 0.8      # cross-category similarity ~ 0.3-0.4
_QUERY_NOISE = 0.45
_GROUP_COMPONENT = 0.6       # related garments (tops, lower body, ...) sit closer
_GARMENT_GROUPS = {
    "tshirt": "tops", "shirt": "tops", "jacket": "tops",
    "pants": "lower", "dress": "lower",
    "shoes": "footwear",
    "bag": "carry", "accessory": "carry",
}


def _seed(*parts: str) -> int:
    return zlib.crc32("|".join(parts).encode()) ^ _GLOBAL_SEED


def _unit(v: np.ndarray) -> np.ndarray:
    return v / (np.linalg.norm(v) + 1e-12)


@dataclass
class CatalogMatch:
    product: Product
    distance: int


class MockEmbeddingSpace:
    def __init__(self, dim: int = EMBEDDING_DIM) -> None:
        self.dim = dim
        shared = _unit(np.random.default_rng(_GLOBAL_SEED).normal(size=dim))
        groups = {g: _unit(np.random.default_rng(_seed("group", g)).normal(size=dim))
                  for g in set(_GARMENT_GROUPS.values())}
        self.centroids: dict[str, np.ndarray] = {
            c.key: _unit(_SHARED_COMPONENT * shared
                         + _GROUP_COMPONENT * groups[_GARMENT_GROUPS[c.key]]
                         + _unit(np.random.default_rng(_seed("centroid", c.key)).normal(size=dim)))
            for c in get_categories()
        }
        self.products: tuple[Product, ...] = get_products()
        vectors = []
        for p in self.products:
            rng = np.random.default_rng(_seed("product", p.id))
            spread = rng.uniform(0.32, 0.62)
            vectors.append(_unit(self.centroids[p.category] + spread * _unit(rng.normal(size=dim))))
        self.product_matrix = np.vstack(vectors).astype(np.float32)
        self.product_ids: tuple[str, ...] = tuple(p.id for p in self.products)

    # ------------------------------------------------------------------ #
    @cached_property
    def _catalog_hashes(self) -> dict[str, str]:
        hashes = {}
        for p in self.products:
            if p.image_path.exists():
                with Image.open(p.image_path) as img:
                    hashes[p.id] = average_hash(img.convert("RGB"))
        return hashes

    def match_catalog_image(self, fingerprint: str, max_distance: int = 4) -> CatalogMatch | None:
        best: CatalogMatch | None = None
        for pid, h in self._catalog_hashes.items():
            d = hamming_distance(fingerprint, h)
            if d <= max_distance and (best is None or d < best.distance):
                best = CatalogMatch(next(p for p in self.products if p.id == pid), d)
        return best

    # ------------------------------------------------------------------ #
    def query_vector(self, category: str, fingerprint: str) -> np.ndarray:
        rng = np.random.default_rng(_seed("query", fingerprint))
        return _unit(self.centroids[category] + _QUERY_NOISE * _unit(rng.normal(size=self.dim))).astype(np.float32)

    def product_vector(self, product_id: str) -> np.ndarray:
        return self.product_matrix[self.product_ids.index(product_id)]


_SPACE: MockEmbeddingSpace | None = None


def get_mock_space() -> MockEmbeddingSpace:
    global _SPACE
    if _SPACE is None:
        _SPACE = MockEmbeddingSpace()
    return _SPACE
