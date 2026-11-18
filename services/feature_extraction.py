"""CNN feature-extraction service.

Interface: ``FeatureExtractor.extract(image, category) -> EmbeddingResult``

Integration plan
    The real extractor will run the EfficientNetB0 backbone without its
    classification head and return the 1280-d global-average-pooled vector,
    L2-normalised so that the inner product equals cosine similarity (FAISS
    ``IndexFlatIP``). ``category`` is only needed by the mock and can be ignored
    by the real implementation.
"""

from __future__ import annotations

from typing import Protocol

from PIL import Image

from services.mock_space import get_mock_space
from services.preprocessing import average_hash, prepare_model_input
from services.types import EmbeddingResult


class FeatureExtractor(Protocol):
    model_name: str

    def extract(self, image: Image.Image, category: str | None = None) -> EmbeddingResult: ...


class MockFeatureExtractor:
    model_name = "CNN feature extractor (demo - not connected)"

    def extract(self, image: Image.Image, category: str | None = None) -> EmbeddingResult:
        space = get_mock_space()
        fingerprint = average_hash(prepare_model_input(image))
        vector = space.query_vector(category or "tshirt", fingerprint)
        return EmbeddingResult(vector=vector, model_name=self.model_name, is_demo=True)
