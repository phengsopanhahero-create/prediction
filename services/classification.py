"""Fashion classification service.

Interface: ``FashionClassifier.classify(image) -> ClassificationResult``

Integration plan
    Replace ``MockFashionClassifier`` with an implementation that either
    (a) loads the Kaggle-trained EfficientNetB0 from the Hugging Face Hub, or
    (b) POSTs the image to the FastAPI ``/classify`` endpoint.
    The UI only depends on the ``ClassificationResult`` contract.
"""

from __future__ import annotations

from typing import Protocol

import numpy as np
from PIL import Image

from data.mock_products import get_categories
from services.mock_space import _seed, get_mock_space
from services.preprocessing import average_hash, prepare_model_input
from services.types import CategoryScore, ClassificationResult


class FashionClassifier(Protocol):
    model_name: str

    def classify(self, image: Image.Image) -> ClassificationResult: ...


class MockFashionClassifier:
    """Returns plausible, deterministic predictions without running a model.

    * Images from the sample library are recognised and get their true category.
    * Any other image returns the documented demo prediction (T-shirt, 96%).
    """

    model_name = "EfficientNetB0 (demo - not connected)"
    DEFAULT_CATEGORY = "tshirt"
    DEFAULT_CONFIDENCE = 0.96

    def classify(self, image: Image.Image) -> ClassificationResult:
        model_input = prepare_model_input(image)
        fingerprint = average_hash(model_input)
        match = get_mock_space().match_catalog_image(average_hash(image))

        if match is not None:
            top = match.product.category
            rng = np.random.default_rng(_seed("conf", match.product.id))
            confidence = float(rng.uniform(0.86, 0.975))
        else:
            top, confidence = self.DEFAULT_CATEGORY, self.DEFAULT_CONFIDENCE
            rng = np.random.default_rng(_seed("conf", fingerprint))

        others = [c.key for c in get_categories() if c.key != top]
        remainder = rng.dirichlet(np.full(len(others), 0.6)) * (1.0 - confidence)
        scores = [CategoryScore(top, confidence)] + [
            CategoryScore(k, float(p)) for k, p in zip(others, remainder)
        ]
        scores.sort(key=lambda s: s.probability, reverse=True)
        return ClassificationResult(
            category=top,
            confidence=confidence,
            scores=tuple(scores),
            model_name=self.model_name,
            is_demo=True,
        )
