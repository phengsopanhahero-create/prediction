"""Rendering of an ``AnalysisResult``: classification, visual analysis, matches."""

from __future__ import annotations

from html import escape

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image

from components.layout import card, card_heading, image_to_data_uri, kv_grid
from components.recommendation_grid import GridItem, render_product_grid
from config import MODEL_INPUT_SIZE
from data.mock_products import get_category, get_product
from services.preprocessing import edge_energy_map, prepare_model_input
from services.types import AnalysisResult, ClassificationResult

_AXIS = dict(labelColor="#777777", titleColor="#777777", domainColor="#DDDDDD", tickColor="#DDDDDD",
             gridColor="#EFEFEF", labelFont="Jost", titleFont="Jost", labelFontSize=11, titleFontSize=11)


def _confidence_band(confidence: float) -> str:
    if confidence >= 0.85:
        return "High confidence"
    if confidence >= 0.60:
        return "Moderate confidence"
    return "Low confidence"


# --------------------------------------------------------------------------- #
# Classification
# --------------------------------------------------------------------------- #
def render_classification(result: ClassificationResult) -> None:
    card_heading("Fashion classification",
                 f'{escape(result.model_name)}<span class="fv-tag">Demo output</span>')
    category = get_category(result.category)
    st.html(
        '<div class="fv-prediction">'
        f'<div><div class="fv-label">Predicted category</div>'
        f'<div class="fv-prediction__label">{escape(category.singular)}</div></div>'
        f'<div><div class="fv-prediction__conf">{result.confidence * 100:.0f}%</div>'
        f'<div class="fv-prediction__band">{_confidence_band(result.confidence)}</div></div>'
        "</div>"
    )
    rows = []
    for i, score in enumerate(result.scores):
        label = get_category(score.category).label
        top = " fv-prob--top" if i == 0 else ""
        pct = score.probability * 100
        value = f"{pct:.1f}%" if pct >= 0.1 else "&lt;0.1%"
        rows.append(
            f'<div class="fv-prob{top}"><span class="fv-prob__name">{escape(label)}</span>'
            f'<span class="fv-prob__bar"><span style="width:{max(pct, 0.4):.2f}%"></span></span>'
            f'<span class="fv-prob__val">{value}</span></div>'
        )
    st.html('<div class="fv-label" style="margin-top:.2rem">Class probabilities</div>' + "".join(rows))
    st.html(
        '<div style="height:.9rem"></div>'
        + kv_grid([
            ("Input tensor", f"{MODEL_INPUT_SIZE[0]} × {MODEL_INPUT_SIZE[1]} × 3"),
            ("Classes", str(len(result.scores))),
            ("Activation", "Softmax"),
            ("Inference", "Simulated"),
        ])
    )


# --------------------------------------------------------------------------- #
# Visual analysis
# --------------------------------------------------------------------------- #
def _luminance_chart(histogram: tuple[int, ...]) -> alt.Chart:
    total = sum(histogram) or 1
    df = pd.DataFrame({
        "Luminance": np.linspace(0, 1, len(histogram), endpoint=False) + 0.5 / len(histogram),
        "Share": [h / total for h in histogram],
    })
    return (
        alt.Chart(df, height=120)
        .mark_area(color="#9A9A9A", line={"color": "#333333", "strokeWidth": 1.2}, opacity=0.55)
        .encode(
            x=alt.X("Luminance:Q", scale=alt.Scale(domain=[0, 1]), axis=alt.Axis(format="%", tickCount=5, grid=False, **_AXIS), title="Dark → light"),
            y=alt.Y("Share:Q", axis=alt.Axis(format="%", tickCount=3, **_AXIS), title=None),
            tooltip=[alt.Tooltip("Luminance:Q", format=".0%"), alt.Tooltip("Share:Q", format=".1%")],
        )
        .configure_view(stroke=None, fill="#FFFFFF")
        .configure(background="#FFFFFF")
    )


def _embedding_chart(vector: np.ndarray, dims: int = 64) -> alt.Chart:
    values = vector[:dims]
    df = pd.DataFrame({"Dimension": np.arange(dims), "Value": values, "Sign": np.where(values >= 0, "pos", "neg")})
    return (
        alt.Chart(df, height=150)
        .mark_bar(size=5)
        .encode(
            x=alt.X("Dimension:Q", axis=alt.Axis(tickCount=8, grid=False, **_AXIS), title=f"First {dims} of {vector.shape[0]} dimensions"),
            y=alt.Y("Value:Q", axis=alt.Axis(tickCount=3, format=".2f", **_AXIS), title=None),
            color=alt.Color("Sign:N", scale=alt.Scale(domain=["pos", "neg"], range=["#333333", "#B5B5B5"]), legend=None),
            tooltip=["Dimension:Q", alt.Tooltip("Value:Q", format=".4f")],
        )
        .configure_view(stroke=None, fill="#FFFFFF")
        .configure(background="#FFFFFF")
    )


def render_visual_analysis(image: Image.Image, result: AnalysisResult) -> None:
    profile = result.profile
    card_heading("Visual analysis",
                 "Pixel statistics are computed from your image. The embedding is an illustrative mock vector.")

    model_input = prepare_model_input(image)
    edges = edge_energy_map(image)
    figures = [
        (image_to_data_uri(image), f"Original &middot; {profile.width}&times;{profile.height}px"),
        (image_to_data_uri(model_input), f"Model input &middot; {MODEL_INPUT_SIZE[0]}&times;{MODEL_INPUT_SIZE[1]} centre crop"),
        (image_to_data_uri(edges), "Edge-energy map &middot; low-level feature proxy"),
    ]
    st.html(
        '<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.75rem;margin-bottom:1.3rem">'
        + "".join(f'<figure class="fv-figure"><img src="{src}" alt=""><figcaption>{cap}</figcaption></figure>'
                  for src, cap in figures)
        + "</div>"
    )

    left, right = st.columns(2, gap="large")
    with left:
        swatches = "".join(f'<span style="flex:{share:.4f};background:{hexv}"></span>'
                           for hexv, share in profile.dominant_colors)
        legend = "".join(f'<span><i style="background:{hexv}"></i>{hexv} &middot; {share * 100:.0f}%</span>'
                         for hexv, share in profile.dominant_colors)
        st.html(f'<div class="fv-label">Dominant colours</div><div class="fv-swatches">{swatches}</div>'
                f'<div class="fv-swatch-legend">{legend}</div><div style="height:1rem"></div>'
                '<div class="fv-label">Luminance distribution</div>')
        st.altair_chart(_luminance_chart(profile.luminance_histogram), width="stretch", theme=None)
        st.html(kv_grid([
            ("Brightness", f"{profile.brightness * 100:.0f}%"),
            ("Contrast", f"{profile.contrast * 100:.0f}%"),
            ("Colour mode", profile.mode),
            ("Perceptual hash", profile.fingerprint),
        ]))

    with right:
        summary = result.embedding.summary()
        st.html('<div class="fv-label">Embedding preview <span class="fv-tag">Mock vector</span></div>')
        st.altair_chart(_embedding_chart(result.embedding.vector), width="stretch", theme=None)
        st.html(kv_grid([
            ("Dimensions", f"{int(summary['dimension']):,}"),
            ("L2 norm", f"{summary['l2_norm']:.3f}"),
            ("Mean", f"{summary['mean']:+.4f}"),
            ("Std. deviation", f"{summary['std']:.4f}"),
            ("Range", f"{summary['min']:+.3f} … {summary['max']:+.3f}"),
            ("Active components", f"{summary['active_ratio'] * 100:.0f}%"),
        ]))


# --------------------------------------------------------------------------- #
# Similar products
# --------------------------------------------------------------------------- #
def render_similar_products(result: AnalysisResult) -> None:
    items = [GridItem(get_product(m.product_id), m.score, m.rank) for m in result.matches]
    render_product_grid(items, columns=max(1, len(items)), key_prefix="fv_match")


def render_analysis_results(image: Image.Image, result: AnalysisResult) -> None:
    left, right = st.columns([0.85, 1.4], gap="medium")
    with left, card("classification"):
        render_classification(result.classification)
    with right, card("visual"):
        render_visual_analysis(image, result)
