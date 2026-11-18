"""Application-wide settings.

Change ``BACKEND_MODE`` to ``"api"`` once the FastAPI inference service exists
(see services/__init__.py for where the switch is resolved).
"""

from __future__ import annotations

import os
from pathlib import Path

APP_NAME = "FashionVision AI"
APP_TAGLINE = "Fashion Detection & Visual Similarity Recommendation System"
APP_VERSION = "1.0.0"
PROJECT_STATUS = "Frontend Demo"

ROOT_DIR = Path(__file__).resolve().parent
STYLES_PATH = ROOT_DIR / "styles" / "main.css"
LOGO_PATH = ROOT_DIR / "static" / "brand" / "logo.png"
MARK_PATH = ROOT_DIR / "static" / "brand" / "mark.png"

# "mock" -> deterministic demo services (current)
# "api"  -> HTTP client for the FastAPI backend (to be implemented)
BACKEND_MODE = os.getenv("FASHIONVISION_BACKEND", "mock")
API_BASE_URL = os.getenv("FASHIONVISION_API_URL", "http://localhost:8000")

# Model input / output contract shared by the mock and the future real models.
MODEL_INPUT_SIZE = (224, 224)
EMBEDDING_DIM = 1280          # EfficientNetB0 global-average-pooled feature size
TOP_K_RECOMMENDATIONS = 5

# Purely cosmetic delay used by the UI to walk through pipeline stages.
SIMULATED_STAGE_DELAY_S = 0.22

ALLOWED_IMAGE_TYPES = ("jpg", "jpeg", "png")
MAX_UPLOAD_MB = 10
