"""Data contracts exchanged between the UI and the ML services.

These shapes are what the FastAPI backend should return (as JSON) later on, so
UI components never depend on how a result was produced.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass(frozen=True)
class CategoryScore:
    category: str          # Category.key
    probability: float     # 0..1


@dataclass(frozen=True)
class ClassificationResult:
    category: str                       # top-1 Category.key
    confidence: float                   # 0..1
    scores: tuple[CategoryScore, ...]   # all categories, sorted descending
    model_name: str
    is_demo: bool = True


@dataclass(frozen=True)
class EmbeddingResult:
    vector: np.ndarray                  # shape (EMBEDDING_DIM,), L2-normalised
    model_name: str
    is_demo: bool = True

    @property
    def dim(self) -> int:
        return int(self.vector.shape[0])

    def summary(self) -> dict[str, float]:
        v = self.vector
        return {
            "dimension": float(v.shape[0]),
            "l2_norm": float(np.linalg.norm(v)),
            "mean": float(v.mean()),
            "std": float(v.std()),
            "min": float(v.min()),
            "max": float(v.max()),
            "active_ratio": float((np.abs(v) > 0.02).mean()),
        }


@dataclass(frozen=True)
class SimilarityMatch:
    product_id: str
    score: float           # cosine similarity, -1..1
    rank: int


@dataclass(frozen=True)
class ImageProfile:
    """Descriptive, non-ML statistics computed directly from the pixels."""
    width: int
    height: int
    mode: str
    file_size_kb: float
    brightness: float                         # 0..1 mean luminance
    contrast: float                           # 0..1 luminance std
    dominant_colors: tuple[tuple[str, float], ...]   # (hex, share)
    luminance_histogram: tuple[int, ...]      # 32 bins
    fingerprint: str                          # 64-bit average hash (hex)


@dataclass(frozen=True)
class AnalysisResult:
    profile: ImageProfile
    classification: ClassificationResult
    embedding: EmbeddingResult
    matches: tuple[SimilarityMatch, ...]
    elapsed_ms: float
    is_demo: bool = True
    notes: tuple[str, ...] = field(default_factory=tuple)
