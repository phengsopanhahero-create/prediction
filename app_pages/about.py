"""Page 5 - About Project."""

from __future__ import annotations

from html import escape

import streamlit as st

from components.layout import card, card_heading, page_header, section_title
from config import APP_NAME, APP_TAGLINE

OBJECTIVES = (
    ("Detect", "Recognise the garment in a product photo or webcam frame and assign it to one of eight fashion categories."),
    ("Explain", "Report a calibrated confidence and the full class-probability distribution, not only a label."),
    ("Recommend", "Retrieve visually similar products using CNN embeddings and cosine-similarity search."),
    ("Integrate", "Deliver a modular system in which models, API and database can be developed independently."),
)

TECH_CURRENT = ("Python 3.12+", "Streamlit", "Pillow", "Pandas", "NumPy", "Altair", "Custom CSS")
TECH_PLANNED = ("TensorFlow / Keras", "EfficientNetB0", "K-Nearest Neighbors", "FAISS", "FastAPI",
                "PostgreSQL", "Kaggle", "Hugging Face Hub")

WORKFLOW = (
    ("Data collection", "Gather labelled fashion product images for the eight categories."),
    ("Preprocessing & augmentation", "Clean, resize to 224 × 224, normalise, and augment (flip, crop, colour jitter)."),
    ("Model training", "Fine-tune EfficientNetB0 on Kaggle GPUs with a held-out validation split."),
    ("Evaluation", "Measure accuracy, per-class precision / recall and confusion matrix on a test set."),
    ("Embedding generation", "Run the backbone over the catalogue to produce one vector per product."),
    ("Indexing", "Build a FAISS index over normalised embeddings for cosine k-NN retrieval."),
    ("Publishing", "Upload model weights and index artefacts to the Hugging Face model repository."),
    ("Serving & integration", "Expose inference through FastAPI and connect it to this frontend."),
)

TEAM = (
    ("Pheng Sopanha", "Team Leader", "AI/ML Engineering", True),
    ("Den Chankarona", "Team Member", "Frontend Development", False),
    ("Tith AnnChengly", "Team Member", "Backend Development", False),
    ("Phearun Lidasaknit", "Team Member", "Database Engineering", False),
)


def _initials(name: str) -> str:
    return "".join(part[0] for part in name.split()[:2]).upper()


page_header("About the project", APP_NAME, f"{escape(APP_TAGLINE)}. A university project that applies "
            "computer vision and machine learning to fashion e-commerce: identify what a garment is "
            "from a photo, then find the products that look most like it.")

section_title("Objectives")
cols = st.columns(4, gap="medium")
for i, (col, (title, text)) in enumerate(zip(cols, OBJECTIVES), start=1):
    col.html(
        f'<div class="fv-objective"><div class="fv-objective__num">0{i}</div>'
        f'<div class="fv-objective__title">{escape(title)}</div>'
        f'<div class="fv-objective__text">{escape(text)}</div></div>'
    )

section_title("Technology & workflow")
left, right = st.columns([1, 1.25], gap="medium")
with left, card("tech"):
    card_heading("Main technologies")
    st.html('<div class="fv-label">In this release</div><div class="fv-chips">'
            + "".join(f'<span class="fv-chip">{escape(t)}</span>' for t in TECH_CURRENT)
            + '</div><div style="height:1.3rem"></div><div class="fv-label">Planned integration</div>'
            '<div class="fv-chips">'
            + "".join(f'<span class="fv-chip fv-chip--planned">{escape(t)}</span>' for t in TECH_PLANNED)
            + "</div>")
    st.space("small")
    card_heading("Scope of this release")
    st.markdown(
        "- Complete, functional frontend with five pages\n"
        "- Image upload, webcam capture and sample library\n"
        "- Mock classification, embeddings and similarity search behind real service interfaces\n"
        "- No trained models, API or database connected yet"
    )
with right, card("workflow"):
    card_heading("Machine learning workflow")
    st.html('<ol class="fv-timeline">'
            + "".join(f"<li><b>{escape(t)}</b><span>{escape(d)}</span></li>" for t, d in WORKFLOW)
            + "</ol>")

section_title("Team", "4 members")
cols = st.columns(4, gap="medium")
for col, (name, role, focus, lead) in zip(cols, TEAM):
    col.html(
        f'<div class="fv-member{" fv-member--lead" if lead else ""}">'
        f'<div class="fv-member__mono">{_initials(name)}</div>'
        f'<div class="fv-member__name">{escape(name)}</div>'
        f'<div class="fv-member__role">{escape(role)}</div>'
        f'<div class="fv-member__focus">{escape(focus)}</div></div>'
    )
