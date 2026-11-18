"""Similarity-search service (k-nearest neighbours over image embeddings).

Interface:
    ``SimilarityIndex.search(vector, k, exclude_ids) -> list[SimilarityMatch]``
    ``SimilarityIndex.score_all(vector) -> dict[product_id, score]``

Integration plan
    Swap ``BruteForceCosineIndex`` for a FAISS ``IndexFlatIP`` (or IVF index)
    loaded from disk / Hugging Face, with product metadata from PostgreSQL.
    Because vectors are L2-normalised, inner product == cosine similarity, so
    the scores shown in the UI keep the same meaning.
"""

from __future__ import annotations

from typing import Iterable, Protocol

import numpy as np

from services.mock_space import get_mock_space
from services.types import SimilarityMatch


class SimilarityIndex(Protocol):
    def search(self, vector: np.ndarray, k: int = 5,
               exclude_ids: Iterable[str] = ()) -> list[SimilarityMatch]: ...

    def score_all(self, vector: np.ndarray) -> dict[str, float]: ...

    def vector_for(self, product_id: str) -> np.ndarray: ...


class BruteForceCosineIndex:
    """Exact cosine k-NN in NumPy - functionally what FAISS IndexFlatIP does."""

    def __init__(self, product_ids: tuple[str, ...], matrix: np.ndarray) -> None:
        self.product_ids = product_ids
        self.matrix = matrix

    @classmethod
    def from_mock_catalog(cls) -> "BruteForceCosineIndex":
        space = get_mock_space()
        return cls(space.product_ids, space.product_matrix)

    def _scores(self, vector: np.ndarray) -> np.ndarray:
        q = vector / (np.linalg.norm(vector) + 1e-12)
        return self.matrix @ q.astype(self.matrix.dtype)

    def search(self, vector: np.ndarray, k: int = 5,
               exclude_ids: Iterable[str] = ()) -> list[SimilarityMatch]:
        excluded = set(exclude_ids)
        scores = self._scores(vector)
        order = np.argsort(-scores)
        results: list[SimilarityMatch] = []
        for idx in order:
            pid = self.product_ids[idx]
            if pid in excluded:
                continue
            results.append(SimilarityMatch(pid, float(scores[idx]), len(results) + 1))
            if len(results) == k:
                break
        return results

    def score_all(self, vector: np.ndarray) -> dict[str, float]:
        return dict(zip(self.product_ids, map(float, self._scores(vector))))

    def vector_for(self, product_id: str) -> np.ndarray:
        return self.matrix[self.product_ids.index(product_id)]
