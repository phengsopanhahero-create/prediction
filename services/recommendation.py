"""Recommendation service - orchestrates the full analysis pipeline.

    image -> preprocessing -> classification -> feature extraction
          -> similarity search -> recommendations

The UI calls this service only; it never talks to individual models. When the
FastAPI backend exists, this whole class can be replaced by a thin HTTP client
that returns the same ``AnalysisResult``.
"""

from __future__ import annotations

import time

import numpy as np
from PIL import Image

from config import TOP_K_RECOMMENDATIONS
from services.classification import FashionClassifier
from services.feature_extraction import FeatureExtractor
from services.mock_space import get_mock_space
from services.preprocessing import profile_image
from services.similarity_search import SimilarityIndex
from services.types import AnalysisResult, SimilarityMatch


class RecommendationService:
    def __init__(self, classifier: FashionClassifier, extractor: FeatureExtractor,
                 index: SimilarityIndex, is_demo: bool = True) -> None:
        self.classifier = classifier
        self.extractor = extractor
        self.index = index
        self.is_demo = is_demo

    # Pipeline ------------------------------------------------------------
    def analyze(self, image: Image.Image, file_size_bytes: int,
                k: int = TOP_K_RECOMMENDATIONS) -> AnalysisResult:
        started = time.perf_counter()
        profile = profile_image(image, file_size_bytes)
        classification = self.classifier.classify(image)
        embedding = self.extractor.extract(image, classification.category)

        # If the query *is* a catalogue item, do not recommend it to itself.
        exclude: list[str] = []
        notes: list[str] = []
        if self.is_demo:
            match = get_mock_space().match_catalog_image(profile.fingerprint)
            if match is not None:
                exclude.append(match.product.id)
                notes.append(f"Query matches catalogue item {match.product.id}; it is excluded from results.")

        matches = self.index.search(embedding.vector, k=k, exclude_ids=exclude)
        return AnalysisResult(
            profile=profile,
            classification=classification,
            embedding=embedding,
            matches=tuple(matches),
            elapsed_ms=(time.perf_counter() - started) * 1000,
            is_demo=self.is_demo,
            notes=tuple(notes),
        )

    # Catalogue helpers -----------------------------------------------------
    def similar_products(self, product_id: str, k: int = TOP_K_RECOMMENDATIONS) -> list[SimilarityMatch]:
        return self.index.search(self.index.vector_for(product_id), k=k, exclude_ids=[product_id])

    def score_catalog(self, vector: np.ndarray) -> dict[str, float]:
        return self.index.score_all(vector)

    def product_vector(self, product_id: str) -> np.ndarray:
        return self.index.vector_for(product_id)
