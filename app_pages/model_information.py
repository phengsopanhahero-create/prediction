"""Page 4 - Model Information (planned ML architecture)."""

from __future__ import annotations

from html import escape

import streamlit as st

from components.layout import card, notice, page_header, section_title
from config import EMBEDDING_DIM, MODEL_INPUT_SIZE, TOP_K_RECOMMENDATIONS

STATUS = "Demo / Not connected"

MODELS = (
    {
        "name": "Classification Model",
        "desc": "Assigns each image to one of eight fashion categories and reports a softmax confidence.",
        "specs": [
            ("Model", "EfficientNetB0"),
            ("Task", "Fashion image classification"),
            ("Input", f"{MODEL_INPUT_SIZE[0]} × {MODEL_INPUT_SIZE[1]} RGB"),
            ("Output", "8-class probability vector"),
            ("Training", "Transfer learning on Kaggle"),
            ("Evaluation", "Pending: reported after training"),
        ],
        "service": "services/classification.py",
    },
    {
        "name": "Feature Extraction",
        "desc": "Encodes the garment's visual appearance (shape, texture, colour) as a dense vector.",
        "specs": [
            ("Model", "CNN feature extractor"),
            ("Task", "Generate image embeddings"),
            ("Backbone", "EfficientNetB0, head removed"),
            ("Embedding", f"{EMBEDDING_DIM:,}-d, L2-normalised"),
            ("Distribution", "Hugging Face model repository"),
            ("Evaluation", "Pending: reported after training"),
        ],
        "service": "services/feature_extraction.py",
    },
    {
        "name": "Recommendation Engine",
        "desc": "Retrieves the catalogue items whose embeddings are closest to the query image.",
        "specs": [
            ("Algorithm", "K-Nearest Neighbors"),
            ("Similarity", "Cosine similarity"),
            ("Vector search", "FAISS"),
            ("Results", f"Top {TOP_K_RECOMMENDATIONS}, ranked by score"),
            ("Metadata", "PostgreSQL product catalogue"),
            ("Evaluation", "Pending: reported after training"),
        ],
        "service": "services/similarity_search.py",
    },
)

PIPELINE = (
    ("Input Image", "Upload or webcam capture (JPG / PNG)", True),
    ("Preprocessing", f"EXIF fix, RGB, centre crop, {MODEL_INPUT_SIZE[0]}px resize", False),
    ("Classification", "EfficientNetB0 softmax over 8 classes", False),
    ("Feature Extraction", "Backbone pooled activations", False),
    ("Embeddings", f"{EMBEDDING_DIM:,}-d unit-length vector", False),
    ("Similarity Search", "Cosine k-NN over FAISS index", False),
    ("Recommendations", f"Top {TOP_K_RECOMMENDATIONS} products with scores", True),
)

ROADMAP = (
    ("Kaggle", "Model training notebooks: data preparation, augmentation, fine-tuning, evaluation.", "Planned"),
    ("Hugging Face Hub", "Versioned storage for the trained classifier and feature extractor weights.", "Planned"),
    ("FastAPI", "Inference API: /classify, /embed and /recommend endpoints consumed by this frontend.", "Planned"),
    ("PostgreSQL", "Product catalogue, categories and image metadata.", "Planned"),
    ("FAISS", "Vector index of catalogue embeddings for fast nearest-neighbour search.", "Planned"),
    ("Streamlit frontend", "This application: UI, session state and service interfaces.", "Demo ready"),
)


def _model_card(index: int, model: dict) -> str:
    specs = "".join(
        f'<div class="fv-spec"><span>{escape(k)}</span><span>{escape(v)}</span></div>' for k, v in model["specs"]
    )
    return (
        f'<div class="fv-model-head"><span class="fv-model-index">0{index}</span>'
        f'<span class="fv-badge">{escape(STATUS)}</span></div>'
        f'<div class="fv-model-name">{escape(model["name"])}</div>'
        f'<div class="fv-model-desc">{escape(model["desc"])}</div>'
        f"{specs}"
        f'<div class="fv-spec"><span>Status</span><span>{escape(STATUS)}</span></div>'
        f'<div class="fv-spec"><span>Service interface</span><span><code>{escape(model["service"])}</code></span></div>'
    )


def _pipeline_html() -> str:
    parts = []
    for i, (name, desc, io) in enumerate(PIPELINE):
        arrow = '<div class="fv-step__arrow">&rarr;</div>' if i < len(PIPELINE) - 1 else ""
        parts.append(
            f'<div class="fv-step{" fv-step--io" if io else ""}"><div class="fv-step__box">'
            f'<div class="fv-step__num">STEP {i + 1:02d}</div>'
            f'<div class="fv-step__name">{escape(name)}</div>'
            f'<div class="fv-step__desc">{escape(desc)}</div></div>{arrow}</div>'
        )
    return f'<div class="fv-pipeline">{"".join(parts)}</div>'


page_header(
    "Architecture",
    "Model Information",
    "The planned machine learning architecture behind FashionVision AI. Models are trained "
    "separately on Kaggle and published to Hugging Face; this frontend is already structured "
    "around their interfaces.",
)
notice(
    "Not connected",
    "No model is connected in this release, and no accuracy or performance figures are shown "
    "because none have been measured yet. Every result in the app comes from mock services.",
)

section_title("Model components", "3 services")
cols = st.columns(3, gap="medium")
for i, (col, model) in enumerate(zip(cols, MODELS), start=1):
    with col, card(f"model_{i}"):
        st.html(_model_card(i, model))

section_title("Inference pipeline", "Input image to recommendations")
st.html(_pipeline_html())

section_title("Integration roadmap")
with card("roadmap"):
    rows = "".join(
        f'<tr><td>{escape(c)}</td><td class="fv-muted">{escape(d)}</td><td>{escape(s)}</td></tr>'
        for c, d, s in ROADMAP
    )
    st.html(
        '<div class="fv-table-wrap"><table class="fv-table"><thead><tr><th>Component</th>'
        f"<th>Responsibility</th><th>Status</th></tr></thead><tbody>{rows}</tbody></table></div>"
    )

section_title("Service contracts", "What the backend must return")
left, right = st.columns([1, 1.25], gap="medium")
with left:
    st.markdown(
        "The UI never calls a model directly. It talks to `RecommendationService`, which composes "
        "three replaceable interfaces:\n\n"
        "- **`FashionClassifier`**: `classify(image) -> ClassificationResult`\n"
        "- **`FeatureExtractor`**: `extract(image) -> EmbeddingResult`\n"
        "- **`SimilarityIndex`**: `search(vector, k) -> list[SimilarityMatch]`\n\n"
        "Swapping the mock implementations for real ones (or for a FastAPI client) is done in "
        "`services/__init__.py` via the `FASHIONVISION_BACKEND` setting, with no UI changes."
    )
with right:
    st.code(
        """@dataclass(frozen=True)
class ClassificationResult:
    category: str              # e.g. "tshirt"
    confidence: float          # 0..1
    scores: tuple[CategoryScore, ...]
    model_name: str

@dataclass(frozen=True)
class SimilarityMatch:
    product_id: str            # e.g. "FV-TS-004"
    score: float               # cosine similarity
    rank: int""",
        language="python",
    )
