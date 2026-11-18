"""Service layer: the only place the UI gets predictions from.

``build_recommendation_service`` resolves ``config.BACKEND_MODE``:

* ``"mock"`` - deterministic demo implementations (current)
* ``"api"``  - reserved for the FastAPI client; add an implementation of the
  ``FashionClassifier`` / ``FeatureExtractor`` / ``SimilarityIndex`` protocols
  (or of ``RecommendationService`` itself) that calls the backend.
"""

from __future__ import annotations

from config import BACKEND_MODE
from services.classification import FashionClassifier, MockFashionClassifier
from services.feature_extraction import FeatureExtractor, MockFeatureExtractor
from services.preprocessing import InvalidImageError, load_image
from services.recommendation import RecommendationService
from services.similarity_search import BruteForceCosineIndex, SimilarityIndex

__all__ = [
    "FashionClassifier",
    "FeatureExtractor",
    "InvalidImageError",
    "RecommendationService",
    "SimilarityIndex",
    "build_recommendation_service",
    "load_image",
]


def build_recommendation_service(mode: str = BACKEND_MODE) -> RecommendationService:
    if mode == "mock":
        return RecommendationService(
            classifier=MockFashionClassifier(),
            extractor=MockFeatureExtractor(),
            index=BruteForceCosineIndex.from_mock_catalog(),
            is_demo=True,
        )
    if mode == "api":
        raise NotImplementedError(
            "BACKEND_MODE='api' is reserved for the FastAPI integration. "
            "Implement an HTTP client returning services.types contracts."
        )
    raise ValueError(f"Unknown backend mode: {mode!r}")
