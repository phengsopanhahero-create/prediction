"""Page 3 - Categories."""

from __future__ import annotations

from html import escape

import streamlit as st

import state
from components.layout import kv_grid, page_header
from data.mock_products import get_categories, get_product, get_products, product_counts


def _browse(label: str) -> None:
    st.session_state[state.GALLERY_CATEGORY] = label
    st.session_state[state.GALLERY_SEARCH] = ""


page_header(
    "Catalogue",
    "Categories",
    "The classifier is designed around eight fashion categories. Each category below shows the "
    "number of items currently in the demo catalogue.",
)

counts = product_counts()
st.html(kv_grid([
    ("Categories", str(len(get_categories()))),
    ("Catalogue items", str(len(get_products()))),
    ("Data source", "Mock catalogue"),
], columns=3))
st.space("medium")

categories = get_categories()
for start in range(0, len(categories), 4):
    cols = st.columns(4, gap="medium")
    for col, category in zip(cols, categories[start:start + 4]):
        cover = get_product(category.cover_product_id)
        n = counts[category.key]
        with col:
            st.html(
                f'<div class="fv-category"><img src="{cover.image_url}" alt="{escape(category.label)}">'
                f'<div class="fv-category__info"><div class="fv-category__name">{escape(category.label)}</div>'
                f'<div class="fv-category__count">{n} product{"s" if n != 1 else ""}</div></div></div>'
                f'<div class="fv-category__desc">{escape(category.description)}</div>'
            )
            if st.button(f"Browse {category.label}", key=f"fv_browse_{category.key}",
                         on_click=_browse, args=(category.label,), width="stretch"):
                st.switch_page("app_pages/recommendation_gallery.py")
    st.space("small")
