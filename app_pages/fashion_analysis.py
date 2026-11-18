"""Page 1 - Fashion Analysis (main experience)."""

from __future__ import annotations

import time

import streamlit as st

import state
from components.layout import card, demo_notice, page_header, section_title
from components.prediction_result import render_analysis_results, render_similar_products
from components.upload_component import render_image_input, render_image_preview
from config import SIMULATED_STAGE_DELAY_S, TOP_K_RECOMMENDATIONS
from data.mock_products import get_category
from services import InvalidImageError, load_image

PIPELINE_STAGES = (
    "Preprocessing image",
    "Classifying garment",
    "Extracting CNN features",
    "Searching visually similar products",
    "Ranking recommendations",
)


def _run_analysis(current: state.CurrentImage) -> None:
    progress = st.progress(0.0, text="Starting analysis…")
    for i, stage in enumerate(PIPELINE_STAGES):
        progress.progress(i / len(PIPELINE_STAGES), text=f"{stage}…")
        time.sleep(SIMULATED_STAGE_DELAY_S)
    try:
        image = load_image(current.data)
        st.session_state[state.RESULT] = state.get_service().analyze(image, current.size_bytes)
        st.session_state[state.GALLERY_REF] = "analysis"
    except InvalidImageError as exc:
        st.session_state[state.INPUT_ERROR] = str(exc)
    progress.empty()


def _open_gallery() -> None:
    st.session_state[state.GALLERY_REF] = "analysis"
    st.session_state[state.GALLERY_CATEGORY] = state.ALL_CATEGORIES


page_header(
    "Analysis studio",
    "Fashion Analysis",
    "Identify a garment from a photo and discover visually similar pieces from the catalogue. "
    "Upload an image or use your webcam; the system classifies the item, encodes it as a "
    "feature vector and ranks products by cosine similarity.",
)
demo_notice()
st.space("small")

left, right = st.columns([1.05, 1], gap="medium")
with left, card("input"):
    render_image_input()
with right, card("preview"):
    analyze_clicked = render_image_preview()
    if analyze_clicked:
        _run_analysis(st.session_state[state.IMAGE])

result = st.session_state.get(state.RESULT)
current = st.session_state.get(state.IMAGE)

if result is not None and current is not None:
    predicted = get_category(result.classification.category)
    section_title("Analysis results", f"Completed in {result.elapsed_ms:,.0f} ms · demo output")
    render_analysis_results(load_image(current.data), result)

    section_title(
        "Similar fashion products",
        f"Top {len(result.matches)} by cosine similarity · predicted: {predicted.singular}",
    )
    render_similar_products(result)
    for note in result.notes:
        st.caption(note)

    st.space("small")
    if st.button("Explore all recommendations", type="secondary", on_click=_open_gallery,
                 key="fv_open_gallery"):
        st.switch_page("app_pages/recommendation_gallery.py")
elif current is not None:
    st.space("small")
    st.caption(
        f"Ready. Select **Analyze image** to classify the item and retrieve the top "
        f"{TOP_K_RECOMMENDATIONS} similar products."
    )
